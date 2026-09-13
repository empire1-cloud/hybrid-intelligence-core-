# CLAUDE.md

Working notes for Empire-1's **Hybrid Intelligence Core (HIC)**. Every rule below is
here because it was actually broken, not because it sounded good. Read this before
adding an engine, a router, or a model call.

**Canon: WE EVOLVE. NEVER DELETE.** Supersede and extend; do not remove working
surfaces.

---

## Shape of the repo

```
backend/          FastAPI app. server.py builds `app`; uvicorn imports it.
  core/           engine_context.py (auth + logging), dependencies.py, security.py
  routers/        ALL HTTP routers live here
  services/       engines, model_policy.py, billing, usage, registry
  middleware/     model policy, subscription usage, execution logging
  models/         Pydantic models
  database/       lazy Mongo connection + collection accessors
  tests/
frontend/         Create React App via craco
```

---

## The five rules that get broken

### 1. No Google / Gemini. Ever.

`services/model_policy.py` is the authority:

```python
APPROVED_MODELS = {"gpt-5.2", "gpt-4o", "gpt-4o-mini",
                   "claude-sonnet-4.5", "claude-3-5-sonnet"}
BLOCKED_MODEL_TOKENS = ("gemini", "google", "vertex")
```

The stack is *deliberately* independent of Google APIs. `middleware/model_policy_middleware.py`
enforces this at the API boundary and fails closed — a request carrying a top-level
`model` or `force_model` of `gemini-*` gets `400 MODEL_POLICY_BLOCKED`. An unapproved
model gets `400 MODEL_POLICY_UNAPPROVED` rather than being silently rerouted.

> **Known gap — do not copy the surrounding code.** Only `strategy_engine.py`,
> `router.py` and `plan_builder.py` call `enforce_approved_model()`. Thirteen other
> engines still carry a `"gemini-3-flash"` entry in their own `MODEL_CONFIG` and
> enforce nothing. Those paths are unreachable over HTTP because of the middleware,
> but reachable by any in-process caller. New engines call the policy.

### 2. Routers declare a **bare** prefix

`server.py` already mounts everything under `/api`:

```python
api_router = APIRouter(prefix="/api")
```

So a router declares `APIRouter(prefix="/pipelines")` — **never** `"/api/pipelines"`.
Declaring it twice mounts the endpoints at `/api/api/...`, which raises nothing, passes
every syntax check, and 404s every call the frontend makes.

Guarded by `tests/test_app_contract.py::test_no_double_api_prefix`.

### 3. Routers live in `backend/routers/`

Not `backend/routes/`. A stray `backend/routes/` exists with a single file and no
`__init__.py`; it works only via namespace packages. Put new routers in `routers/`.

### 4. Tenancy is **team**-scoped, not user-scoped

Every collection filters on `team_id`. Authentication and scoping come from one place:

```python
from core.engine_context import get_engine_context, EngineContext

@router.get("/thing")
async def read_thing(ctx: EngineContext = Depends(get_engine_context)):
    ctx.require_read()          # or require_write() / require_admin()
    team_id = ctx.team_id
```

`EngineContext` resolves either a JWT user or a `hic_...` API key, and API keys can
never administer a workspace. Do **not** introduce `user_id` as an ownership key — a
`user_id`-owned record is invisible to the team that paid for it. Own by `team_id`,
attribute with `created_by`, the shape `PipelineInDB` already uses.

### 5. Commit your work — `/app` is not the repo

`services/execution_logger.py` hardcodes `/app/backend/execution_logs.json`. `/app` is
the **deploy directory**. Editing files there changes the running container and puts
nothing in git; a redeploy from `main` silently discards all of it. Work in the repo.

---

## Calling an LLM

The client is `emergentintegrations` (not on PyPI — see CI below). The canonical
pattern is `services/strategy_engine.py`:

```python
approved = enforce_approved_model(model)                 # fail closed first
provider, model_name = cls.MODEL_CONFIG[approved]
chat = LlmChat(
    api_key=cls._get_api_key(provider),
    session_id=f"<engine>-{approved}",
    system_message=cls.SYSTEM_PROMPT,
).with_model(provider, model_name)                        # model set HERE

response = await chat.send_message(UserMessage(text=prompt))   # returns a plain str
```

None of the following exist, and each has shipped at least once:

| Wrong | Right |
|---|---|
| `LlmChat(model_name=...)` | `.with_model(provider, model)` |
| `await chat.complete_chat_async(messages=[...])` | `await chat.send_message(msg)` |
| `UserMessage(content=...)` | `UserMessage(text=...)` |
| `response.message.content` | `response` is already the string |

A `MODEL_CONFIG` dict that nothing reads is dead code: without `.with_model()` the
client keeps its own default (`gpt-4o`/openai) regardless of what you configured.

---

## Execution instrumentation

`core/engine_context.py::log_engine_call` is the single logging path. It calls
`extract_execution_metrics()` and forwards `provider`, `model`, `input_tokens`,
`output_tokens`, `cost_usd` and `confidence` to `log_execution()`.

An engine opts in simply by putting those keys in `metadata` on its response — no
router changes needed. Malformed values are dropped rather than raised, so an
execution never fails on its own instrumentation.

Analytics read this back at `/api/analytics/executions/*`, all team-scoped.

---

## Commands

```bash
# backend tests (PYTHONPATH matters)
cd backend && PYTHONPATH=. python -m pytest -q tests/test_app_contract.py
cd backend && PYTHONPATH=. python -m pytest -q tests/test_model_policy.py

# frontend
cd frontend && npm install && npm run build     # craco
```

---

## CI, and what it does *not* prove

`.github/workflows/hic-subscription-ci.yml`:

- **`backend-contract`** — compiles the backend tree, then **imports the app** and runs
  the contract tests. Importing is the part that matters: `compileall` accepts any
  syntactically valid file and never resolves an import, so a router importing a module
  that does not exist used to compile clean and pass while the app could not start.
- **`frontend-build`** — `npm run build`.

Two things to know before touching the workflow:

- **`requirements.txt` does not resolve.** `emergentintegrations==0.1.1` is not on PyPI
  and conflicts with the pinned `litellm` wheel; `pip install -r requirements.txt` fails
  even with the extra index that `deployment/deploy.sh` uses. CI therefore installs a
  pinned subset of what the app actually imports, and supplies `emergentintegrations`
  from the vendored `backend/emergentintegrations_local_backup/` drop-in copy. Keep that
  list in sync when adding a third-party import.
- A green `backend-contract` proves the app **starts** and the routes are wired. It does
  not prove any engine produces good output, and it makes no live LLM call.

---

## Known gaps (verified, not yet fixed)

- `GET /api/health` is registered twice; the second registration shadows the first.
- Thirteen engines carry a `gemini` entry with no `enforce_approved_model` call (see §1).
- `requirements.txt` is unresolvable, so `deployment/deploy.sh` would fail as written.
- `backend_test.py` asserts that forcing `gemini-3-flash` *works*, which contradicts the
  policy the middleware enforces.

---

## Working style

State what is verified and what is not. "CI is green" is a fact about CI, not about the
software — if a claim has not been exercised, say so in the same breath as the claim.

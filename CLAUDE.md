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

- Thirteen engines carry a `gemini` entry with no `enforce_approved_model` call (see §1).
  Still true after both Canon Contract passes below — those engine files' model-selection
  code was not touched. (Three of the thirteen — `strategy_engine.py`, `plan_builder.py`,
  `analysis_engine.py` — did get touched in pass 2, but only their JSON-parse-failure
  handling; their `MODEL_CONFIG`/policy-enforcement gap is untouched.)
- `requirements.txt` is unresolvable, so `deployment/deploy.sh` would fail as written.
- `backend_test.py` asserts that forcing `gemini-3-flash` *works*, which contradicts the
  policy the middleware enforces.
- `services/hybrid_core.py::HybridIntelligenceCore.execute()` only ever calls
  `StrategyEngine` or `PlanBuilderEngine`; its own `ENGINE_MAP` dict is declared and never
  read anywhere. Left as-is (existing `/core/*` behavior is not to be changed) in both
  passes; `/canon/*` dispatches to 8 engines for real instead — see pass 2 below.
- Opportunity Mapper, Evaluator, Pricing and Persona (newly wired into `/canon/*` in pass 2)
  still fabricate a hardcoded placeholder on `JSONDecodeError`, the same bug class fixed in
  Strategy/Plan/Analysis in pass 2. `services/canon_contract.py` detects and refuses to
  canonize their specific fallback shapes, same as pass 1 did for the original three before
  they were fixed at the source. Not fixed at the source for these four — next pass.
- Blueprint Engine, the anime/art-direction content engines, Money Pipeline, Pipeline
  Composer, and the 12 Startup Copilot skills (a separate product surface) are still not
  reachable from either orchestrator. 8 of ~19 engines are genuinely dispatched by task type
  as of pass 2 (`/canon/*` only) — see `services/canon_routing.py` for the exact list.

**Correction (pass 2):** pass 1's note here previously said `GET /api/health` was
registered three times. Re-verified against the actual live route table
(`app.routes`, not grep) rather than trusting that count: it was genuinely registered
twice (`routers/engines/core.py` and `server.py`) — the third grep hit was
`routers/system.py`, whose router carries its own `/system` prefix, so its `/health`
lives at the distinct path `/api/system/health` and was never actually colliding. Fixed
in pass 2 — see below. Flagging the correction itself: this file's own working-style rule
is to say what's verified, and the "three times" claim wasn't.

---

## Canon Contract layer (`/canon/*`) — additive, alongside `/core/*`

Founding canon defines a four-part output contract — Core Insight → System Blueprint →
Leverage Point → Executable Output — and a hybrid tri-model stack (GPT-5.2 + Claude
Sonnet 4.5 + Gemini 3 Flash) run with parallel calls and fallbacks. Before this pass,
**neither existed anywhere in this codebase** — verified by `git log --all -S` across
every local and remote branch for `CORE_INSIGHT_PROMPT`, `class SystemOutput`,
`GeneratedComponent`, `SystemMeta`: zero hits, ever. `CanonEnforcer`'s "canon" is a
different thing — tone/phrase hygiene plus Strategy Engine's own 5-field shape — not the
founding four-part contract.

What's new, all additive, `/core/*` untouched:

- `models/canon_contract.py`, `services/canon_contract.py` — `FourPartOutput` and
  `FourPartContractMapper`, mapping Strategy/Plan/Analysis output onto the four-part
  contract. Refuses (raises `CanonContractError`) rather than canonizes a detected
  parse-failure fallback from those three engines.
- `services/tri_model_execution.py` — real fallback (`run_with_fallback`) and real
  concurrent dispatch (`run_in_parallel`) across `services.model_policy.APPROVED_MODELS`.
  **Honest naming note:** Gemini is blocked by the live, tested model policy, so this is
  dual-model (GPT-5.2 / Claude Sonnet 4.5) today, not literally tri-model. It reads
  `APPROVED_MODELS` at call time rather than hardcoding a count, so it becomes tri-model
  automatically if policy ever admits a third approved provider — nothing here special-cases
  Gemini back in.
- `services/canon_orchestrator.py` — `CanonicalOrchestrator`, a second orchestrator next to
  `HybridIntelligenceCore`. Dispatches Analysis-classified prompts to `AnalysisEngine` (the
  first time that dispatch intent in `ENGINE_MAP` is actually exercised), runs every call
  through the fallback layer, and maps the result through the contract mapper.
  `HybridIntelligenceCore.execute()` is not imported for its dispatch logic and not modified.
- `services/canon_run_service.py`, `canon_runs_collection()` — the "My Systems" library:
  team-scoped, soft-delete (`is_active` flip, never a physical delete — WE EVOLVE, NEVER
  DELETE), mirrors `pipeline_service.py`'s existing pattern exactly.
- `routers/engines/canon.py` — `POST /canon/execute`, `GET /canon/runs`,
  `GET /canon/runs/{id}`, `DELETE /canon/runs/{id}` (soft), `GET /canon/status`. Mounted the
  same way as every other engine router (`dependencies=engine_dependencies`).

Tests: `tests/test_canon_contract.py`, `tests/test_tri_model_execution.py`,
`tests/test_canon_orchestrator.py`, `tests/test_canon_router_wiring.py`. Run the same way
as the rest of this file's test commands, with the same `emergentintegrations` shim.

Not done in this pass, left for the next one: the 13 engines' unenforced `gemini` entries,
the duplicate `/health` registration, `requirements.txt` resolution, and actually fixing (not
just detecting) the three engines' fabrication-on-parse-failure fallback.

---

## Canon Contract layer, pass 2 — more engines, the source-level honesty fix, `/health` dedupe

Three things from pass 1's "not done" list, done in pass 2. `/core/*` is still completely
untouched by this pass too.

**1. Four more engines wired into `/canon/*`.** `services/canon_orchestrator.py` reached
Strategy, Plan Builder and Analysis in pass 1. It now also reaches Opportunity Mapper,
Evaluator, Pricing and Persona — 8 of ~19 engines genuinely dispatched by task type. New
module `services/canon_routing.py` replaces pass 1's reliance on
`services.hybrid_core.TaskType` (6 narrow categories) with a wider, regex-scored classifier
over `CANON_ENGINE_KEYS`; `canon_orchestrator.py` no longer imports `hybrid_core` at all.
`POST /canon/execute`'s `task_type` field still accepts every value it did before (the old
TaskType values were already lowercase strings matching their `.value`, e.g. `"analysis"`;
`"code"`/`"quick"`/`"general"` still resolve, now via a default-to-strategy fallback instead
of an enum member) — this is additive at the API level, not a breaking change. Still not
wired: Blueprint, the anime/art-direction engines, Money Pipeline, Pipeline Composer, the 12
Startup Copilot skills.

**2. The fabrication-on-parse-failure bug is actually fixed, at the source, in three
engines.** `strategy_engine.py`, `plan_builder.py`, `analysis_engine.py` no longer return a
hardcoded placeholder dict when the model's response doesn't parse as JSON — each now raises
`services/engine_errors.py::EngineOutputError` (mirrors the already-proven
`startup_copilot_engines.py::SkillOutputError` pattern exactly). Checked every existing
caller before making this change: `routers/engines/strategy.py`, `plan.py`, `analysis.py`,
and `services/hybrid_core.py::execute()` all already wrap their engine call in
`try/except Exception -> a structured error response`, so this raise is caught everywhere it
already ran — no unhandled failure anywhere, `/core/execute` included. A parse failure now
correctly reports `success: false` there too, instead of silently returning fabricated
content as a success. `services/canon_contract.py`'s marker-detection for these three engines
is kept as defense-in-depth (belt-and-suspenders — WE EVOLVE, NEVER DELETE), though it should
no longer trigger for them in practice; it's still load-bearing for the four newly-wired
engines above, which were **not** fixed at the source in this pass.

**3. `GET /api/health` duplicate removed.** See the correction above — it was genuinely
registered twice. `server.py`'s copy is deleted; `routers/engines/core.py`'s copy (the one
that was actually live) gained the fields the deleted one had (`parent`, `product`,
`version`, `timestamp`), so nothing either version promised is lost. Verified against the
live route table, and `test_app_contract.py` now asserts exactly one `GET /api/health`
handler (this was one of the two assertions that file's own comment had explicitly deferred
as "worth fixing separately").

Tests: `tests/test_canon_routing.py`, `tests/test_engine_output_honesty.py` (the source-level
proof for item 2 — only `_create_chat` is patched per engine, not the whole method, so the
engine's real JSON-parsing logic runs), plus new cases in `tests/test_canon_orchestrator.py`
for the four newly-wired engines. `test_app_contract.py` gained
`test_no_duplicate_health_route`.

---

## Working style

State what is verified and what is not. "CI is green" is a fact about CI, not about the
software — if a claim has not been exercised, say so in the same breath as the claim.

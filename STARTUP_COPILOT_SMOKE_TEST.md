# Startup Copilot — Verification Status

Tracks what has been mechanically verified versus what still needs a human
with live API keys. Claims here are only added once a command has proven them.

---

## Verified in CI / locally

| Check | How it is proven |
|---|---|
| Frontend compiles | `CI=true npm run build` → "Compiled successfully", warnings treated as errors |
| Dashboard reaches the bundle | `grep founder-copilot build/static/js/main.*.js` → present |
| Route is wired | `/founder-copilot` in `App.js` behind `ProtectedRoute`; "Copilot" link in `AppHeader` |
| Routes mount correctly | Router enumeration → 16 paths under `/api/startup-copilot/`, none double-prefixed |
| Every required field is collected | `tests/test_startup_copilot_contract.py` — 12/12 input models satisfied by the form catalog |
| Contract test actually fails on drift | Removing `runway_months` from the catalog turns the suite red; restoring it turns it green |
| Engines never fabricate output | All 12 raise `SkillOutputError` on unparseable model output instead of returning placeholder guidance; guard fails if a fallback is reintroduced |
| Happy path passes the model through | A well-formed response yields the model's own values, not defaults |
| No bare `except:` in the engines | Static check in the contract suite |
| LLM call signature is real | Verified against the vendored `emergentintegrations_local_backup`: `LlmChat(api_key, session_id, system_message).with_model(provider, model)` then `await send_message(UserMessage(text=...))` |
| A missing API key surfaces as an error | Ran an engine with every key unset → HTTP 401 propagates out of the engine rather than being swallowed |

Run them:

```bash
cd frontend && CI=true npm run build
cd backend  && PYTHONPATH=. python -m pytest -q tests/test_startup_copilot_contract.py  # 28 tests
```

---

## Not yet verified — needs live keys

Nothing below has been executed. No request has ever reached a model.

- [ ] A skill returns real guidance (requires `ANTHROPIC_API_KEY` and a reachable LLM)
- [ ] What a real model actually emits. The engine-side parse contract is tested against synthetic payloads; no real response has been seen.
- [ ] `enforce_engine_subscription` admits a normal logged-in user rather than 402/403 on quota
- [ ] A chained workflow completes without timing out (3–4 sequential model calls in one request)
- [ ] Latency is tolerable for a single request, and the loading state holds up

### Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # then add real keys
uvicorn server:app --reload --port 8001

cd frontend
npm install
REACT_APP_BACKEND_URL=http://localhost:8001 npm start
```

Log in, open **Copilot** in the header (`/founder-copilot`).

### Manual pass

1. **Customer Success** — smallest skill, two fields. Confirms auth, routing, and a live model call in one step.
2. **Idea Validation** — confirms the nested `founder_background` object is assembled correctly.
3. **Legal & Compliance** — confirms the checkbox transmits `has_employees: false` rather than omitting it.
4. **Validate → Pitch** — confirms a multi-step workflow survives its own runtime.
5. **Error path** — stop the backend mid-session and submit; the form should surface the error, not hang.

---

## Known gaps

| Gap | Notes |
|---|---|
| Results are session-only | Held in React state; a refresh clears them. No persistence layer yet. |
| No PDF export | Deliberately not built. "Copy JSON" is the only export. |
| Workflow inputs are shared | The backend takes one `WorkflowRequest` for all steps; per-step inputs are not supported by the API. |
| Response shape unconfirmed | `SkillResult` renders whatever `data` contains generically; it has never seen a real payload. |
| Unparseable output is a hard failure | By design. If a model reliably wraps JSON in prose, the fix is prompt or parser work — not a placeholder response. |

---

## Merge criteria

Mechanical checks above are green. Merging still depends on at least one live
skill call succeeding — until then the UI is proven to compile, route, and
build valid request bodies, but is unproven end to end.

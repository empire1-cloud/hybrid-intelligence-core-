"""
Contract tests: frontend skill catalog vs. Startup Copilot input models.

The React dashboard builds its request bodies from
frontend/src/components/startup-copilot/skills.js. If a field is required by a
Pydantic input model but the catalog never collects it, every submission for
that skill fails validation at runtime. These tests fail instead.
"""

import re
import sys
import types
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
CATALOG = BACKEND.parent / "frontend/src/components/startup-copilot/skills.js"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def _stub_llm():
    """Import routes without the LLM transport installed."""
    for name in (
        "emergentintegrations",
        "emergentintegrations.llm",
        "emergentintegrations.llm.chat",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))
    chat = sys.modules["emergentintegrations.llm.chat"]
    if not hasattr(chat, "LlmChat"):
        class _Stub:
            def __init__(self, *a, **k):
                pass

            def with_model(self, *a, **k):
                return self

        chat.LlmChat = _Stub
        chat.UserMessage = _Stub


_stub_llm()

from services.startup_copilot_models import (  # noqa: E402
    BusinessModelInput,
    FinanceInput,
    FundraisingInput,
    GTMInput,
    GrowthInput,
    HealthScoreInput,
    IdeaValidationInput,
    LegalInput,
    MarketingInput,
    OperationsInput,
    ProductInput,
    SalesInput,
)

ENDPOINT_MODELS = {
    "validate-idea": IdeaValidationInput,
    "design-business-model": BusinessModelInput,
    "create-fundraising-strategy": FundraisingInput,
    "create-gtm-strategy": GTMInput,
    "create-product-strategy": ProductInput,
    "create-sales-strategy": SalesInput,
    "create-marketing-strategy": MarketingInput,
    "create-growth-strategy": GrowthInput,
    "create-operations-strategy": OperationsInput,
    "create-financial-model": FinanceInput,
    "create-customer-success-strategy": HealthScoreInput,
    "create-legal-strategy": LegalInput,
}

# Catalog fields the skill's buildPayload() folds into one nested model field.
NESTED_FIELDS = {
    "validate-idea": {
        "founder_background": {
            "years_experience",
            "domain",
            "previous_exits",
            "industry_relationships",
        }
    }
}


def _parse_catalog():
    """endpoint -> set of field names the form always transmits."""
    source = CATALOG.read_text()
    # Drop option lists so the remaining braces are flat field objects.
    source = re.sub(r"options:\s*\[.*?\n\s*\],", "", source, flags=re.S)

    catalog, endpoint = {}, None
    for chunk in re.finditer(r"endpoint:\s*'([^']+)'|\{[^{}]*\}", source, flags=re.S):
        text = chunk.group(0)
        if chunk.group(1):
            endpoint = chunk.group(1)
            catalog[endpoint] = set()
            continue
        if endpoint is None:
            continue
        # A checkbox always transmits a boolean, so it satisfies a required
        # bool field even though the form does not mark it required.
        collected = "required: true" in text or "type: 'checkbox'" in text
        if not collected:
            continue
        name = re.search(r"name:\s*'([^']+)'", text)
        if name:
            catalog[endpoint].add(name.group(1))
    return catalog


def _required_model_fields(model):
    return {n for n, f in model.model_fields.items() if f.is_required()}


@pytest.fixture(scope="module")
def catalog():
    assert CATALOG.exists(), f"skill catalog not found at {CATALOG}"
    parsed = _parse_catalog()
    assert parsed, "parsed no skills from the catalog"
    return parsed


def test_catalog_covers_every_endpoint(catalog):
    assert set(ENDPOINT_MODELS) <= set(catalog), (
        f"endpoints missing from catalog: {sorted(set(ENDPOINT_MODELS) - set(catalog))}"
    )


@pytest.mark.parametrize("endpoint,model", sorted(ENDPOINT_MODELS.items()))
def test_form_collects_every_required_field(endpoint, model, catalog):
    collected = set(catalog[endpoint])
    for target, sources in NESTED_FIELDS.get(endpoint, {}).items():
        if collected & sources:
            collected.add(target)

    missing = _required_model_fields(model) - collected
    assert not missing, (
        f"{endpoint}: {model.__name__} requires {sorted(missing)}, "
        "but the form never collects it — every submission would 422"
    )


def test_router_is_not_double_prefixed():
    """server.py mounts this router under an /api parent; the router must not repeat it."""
    from routes.startup_copilot_routes import router

    assert not router.prefix.startswith("/api"), (
        f"router prefix {router.prefix!r} is mounted under /api and would resolve to "
        f"/api{router.prefix}"
    )


# ---------------------------------------------------------------------------
# Output handling
#
# Engines previously returned hardcoded guidance whenever a model response
# failed to parse — a founder would see invented unit economics (LTV/CAC 10.0,
# CAC $1,500) rendered as a completed analysis. They must raise instead.
# ---------------------------------------------------------------------------

import asyncio  # noqa: E402
import json  # noqa: E402

from services.startup_copilot_engines import (  # noqa: E402
    BusinessModelEngine,
    IdeaValidationEngine,
    LegalEngine,
    SkillOutputError,
)

MALFORMED = [
    pytest.param('Sure! Here is the analysis:\n\n{"model_pattern": "marketplace"}', id="preamble"),
    pytest.param('{"model_pattern": "marketplace", "unit_economics": {"ltv": 9000}}', id="wrong-shape"),
    pytest.param('{"model_pattern": "marketplace", "revenue_streams": [{"name": "take', id="truncated"),
    pytest.param("", id="empty"),
]

ENGINE_CALLS = [
    pytest.param(
        BusinessModelEngine,
        "design_model",
        {"product_description": "x", "target_market": "y"},
        id="business-model",
    ),
    pytest.param(
        IdeaValidationEngine,
        "validate",
        {
            "founder_background": {"years_experience": 5, "domain": "fintech"},
            "market_problem": "x",
        },
        id="idea-validation",
    ),
    pytest.param(
        LegalEngine,
        "create_legal_strategy",
        {
            "entity_type": "c_corp",
            "jurisdictions": ["Delaware"],
            "stage": "seed",
            "has_employees": False,
        },
        id="legal",
    ),
]


def _model_for(method_name):
    from routes import startup_copilot_routes as routes  # noqa: WPS433

    return {
        "design_model": routes.BusinessModelInput,
        "validate": routes.IdeaValidationInput,
        "create_legal_strategy": routes.LegalInput,
    }[method_name]


@pytest.mark.parametrize("engine_cls,method,payload", ENGINE_CALLS)
@pytest.mark.parametrize("response_text", MALFORMED)
def test_unparseable_response_raises_instead_of_fabricating(
    engine_cls, method, payload, response_text, monkeypatch
):
    async def fake_ask(*_args, **_kwargs):
        return response_text

    monkeypatch.setattr(engine_cls, "_ask", classmethod(fake_ask))
    engine = engine_cls()
    model = _model_for(method)(**payload)

    with pytest.raises(SkillOutputError):
        asyncio.run(getattr(engine, method)(model))


def test_engines_use_no_bare_except():
    """A bare except also swallows KeyboardInterrupt and masks real failures."""
    source = (BACKEND / "services/startup_copilot_engines.py").read_text()
    offenders = [
        i + 1
        for i, line in enumerate(source.splitlines())
        if line.strip() == "except:"
    ]
    assert not offenders, f"bare except on lines {offenders}"


def test_well_formed_response_is_returned_unchanged(monkeypatch):
    """The happy path must pass the model's own answer through, not a default."""
    payload = {
        "model_pattern": "marketplace",
        "revenue_streams": [],
        "unit_economics": {
            "revenue_per_customer": 5000,
            "gross_margin_percent": 70,
            "customer_acquisition_cost": 1500,
            "lifetime_value": 15000,
            "ltv_cac_ratio": 10.0,
            "payback_period_months": 3.6,
        },
        "target_segments": ["freelancers"],
        "pricing_tiers": [],
        "expansion_opportunities": [],
        "risks": [],
    }

    async def fake_ask(*_args, **_kwargs):
        return json.dumps(payload)

    monkeypatch.setattr(BusinessModelEngine, "_ask", classmethod(fake_ask))
    from routes.startup_copilot_routes import BusinessModelInput

    result = asyncio.run(
        BusinessModelEngine().design_model(
            BusinessModelInput(product_description="x", target_market="y")
        )
    )
    assert result.model_pattern == "marketplace"
    assert result.target_segments == ["freelancers"]

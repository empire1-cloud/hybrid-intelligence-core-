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

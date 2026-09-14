# Startup Copilot Implementation Guide

## Overview

**Startup Copilot** is a complete founder intelligence system integrated into HIC as **Engines 1-12**. It provides end-to-end guidance from idea validation through scaling via 12 specialized AI skills.

**Status:** Phase 1 & 2 Complete
- ✅ Documentation (STARTUP_COPILOT_SKILLS.md)
- ✅ Backend Implementation (3 new service files)
- ✅ API Endpoints (12 skills + 2 workflows)
- 🔄 Frontend UI (coming in Phase 3)
- 🔄 Advanced Analytics (coming in Phase 4)

---

## Architecture

### Files Created

```
/backend/
├── services/
│   ├── startup_copilot_models.py       # Pydantic models for all 12 skills
│   ├── startup_copilot_engines.py      # Engine implementations
│   └── (existing engines)
├── routes/
│   ├── startup_copilot_routes.py       # FastAPI endpoints
│   └── (existing route files)
└── server.py                           # Updated with router integration

/documentation/
├── STARTUP_COPILOT_SKILLS.md           # Framework documentation (Phase 1)
└── STARTUP_COPILOT_IMPLEMENTATION.md   # This file
```

### Data Models

12 input/output model pairs covering:

| Skill | Input Model | Output Model |
|-------|-------------|--------------|
| 1. Idea Validation | `IdeaValidationInput` | `IdeaValidationOutput` |
| 2. Business Model | `BusinessModelInput` | `BusinessModelOutput` |
| 3. Fundraising | `FundraisingInput` | `FundraisingOutput` |
| 4. GTM | `GTMInput` | `GTMOutput` |
| 5. Product | `ProductInput` | `ProductOutput` |
| 6. Sales | `SalesInput` | `SalesOutput` |
| 7. Marketing | `MarketingInput` | `MarketingOutput` |
| 8. Growth | `GrowthInput` | `GrowthOutput` |
| 9. Operations | `OperationsInput` | `OperationsOutput` |
| 10. Finance | `FinanceInput` | `FinanceOutput` |
| 11. Customer Success | `HealthScoreInput` | `HealthScoreOutput` |
| 12. Legal | `LegalInput` | `LegalOutput` |

---

## API Endpoints

All endpoints are protected with `engine_dependencies` (require JWT workspace or `hic_` API key).

### Base Path
```
POST /api/startup-copilot/{skill-endpoint}
```

### Individual Skills (12 endpoints)

```bash
# 1. Idea Validation
POST /api/startup-copilot/validate-idea
Body: {
  "founder_background": {
    "years_experience": 5,
    "domain": "fintech",
    "previous_exits": 1,
    "industry_relationships": ["regulators", "processors"]
  },
  "market_problem": "Freelancers in LatAm can't receive USD",
  "existing_solutions": ["Payoneer", "Wise"],
  "interviews_conducted": 10
}
Response: {
  "verdict": "go|pivot|kill",
  "confidence": 0.85,
  "findings": [...],
  "founder_market_fit_score": 8.5,
  "next_steps": [...]
}

# 2. Business Model Design
POST /api/startup-copilot/design-business-model
Body: {
  "product_description": "Stablecoin bank for freelancers",
  "target_market": "Freelancers in LatAm/Africa",
  "market_size_tam": 1000000000,
  "existing_business_models": ["Wise (8.9% take)", "Payoneer (2% + fees)"]
}
Response: {
  "model_pattern": "transactional_fintech",
  "revenue_streams": [...],
  "unit_economics": {
    "ltv_cac_ratio": 2.5,
    "payback_period_months": 3.6
  },
  "pricing_tiers": [...]
}

# 3. Fundraising Strategy
POST /api/startup-copilot/create-fundraising-strategy
Body: {
  "current_stage": "seed",
  "target_raise": 500000,
  "use_of_funds": "Product dev + GTM + Nigeria expansion",
  "runway_months": 12
}
Response: {
  "pitch_deck": [10 slides],
  "investor_targets": [100 VCs],
  "investor_count": 100,
  "estimated_timeline_weeks": 8
}

# 4. Go-to-Market Strategy
POST /api/startup-copilot/create-gtm-strategy
Body: {
  "product_type": "B2B fintech",
  "target_acv": 5000,
  "target_customers": 100,
  "founder_background": "5 years at Flutterwave"
}
Response: {
  "recommended_motion": "hybrid|plg|sales_led",
  "channels": [...],
  "phase_1_days": 30,
  "phase_2_days": 30,
  "phase_3_days": 30
}

# 5. Product Strategy
POST /api/startup-copilot/create-product-strategy
Body: {
  "problem_statement": "...",
  "target_user": "Freelance developers in Nigeria",
  "key_features": ["USD wallet", "Instant payout", "No fees"],
  "success_metrics": ["DAU growth", "NPS > 50"]
}
Response: {
  "prd_sections": {...},
  "user_stories": [...],
  "top_3_priorities": ["Core wallet", "Payout UX", "KYC flow"],
  "rice_scores": {...}
}

# 6. Sales Strategy
POST /api/startup-copilot/create-sales-strategy
Body: {
  "deal_complexity": "moderate",
  "acv": 5000,
  "buyer_profile": "CFO/Finance Director at SaaS"
}
Response: {
  "recommended_methodology": "MEDDIC|BANT|Challenger",
  "cold_email_sequences": [...],
  "target_response_rate": 0.02,
  "target_conversion_rate": 0.005
}

# 7. Marketing Strategy
POST /api/startup-copilot/create-marketing-strategy
Body: {
  "brand_positioning": "The stablecoin bank for global freelancers",
  "target_audience": "Freelance developers, designers, writers",
  "competition_level": "medium"
}
Response: {
  "brand_voice_attributes": ["Data-driven", "Irreverent", "Action-oriented"],
  "content_pillars": [...],
  "target_keywords": [30 SEO keywords],
  "monthly_content_plan": [...]
}

# 8. Growth Strategy
POST /api/startup-copilot/create-growth-strategy
Body: {
  "current_product_stage": "mvp_beta",
  "primary_metric": "DAU",
  "target_metric_value": 10000,
  "time_horizon_months": 6
}
Response: {
  "north_star_metric": "Daily Active Users",
  "aarrr_metrics": [...],
  "retention_curve_target": {...},
  "recommended_experiments": [...]
}

# 9. Operations Strategy
POST /api/startup-copilot/create-operations-strategy
Body: {
  "current_headcount": 2,
  "target_headcount": 8,
  "timeline_months": 6,
  "budget": 500000
}
Response: {
  "hiring_plan": [...],
  "interview_scorecard": {...},
  "okrs": [...]
}

# 10. Financial Model
POST /api/startup-copilot/create-financial-model
Body: {
  "current_cash": 250000,
  "monthly_burn_rate": 30000,
  "headcount": 2,
  "months_ahead": 12
}
Response: {
  "cash_flow_projection": [12 months],
  "projected_runway_months": 8.3,
  "next_fundraising_deadline": "2027-05-15"
}

# 11. Customer Success Strategy
POST /api/startup-copilot/create-customer-success-strategy
Body: {
  "product_type": "plg|sales_led",
  "customer_segment": "Freelance developers"
}
Response: {
  "onboarding_milestones": [...],
  "health_score_formula": "...",
  "nps_target": 50,
  "churn_prevention_tactics": [...]
}

# 12. Legal Strategy
POST /api/startup-copilot/create-legal-strategy
Body: {
  "entity_type": "c_corp",
  "jurisdictions": ["Delaware"],
  "stage": "seed",
  "has_employees": true
}
Response: {
  "recommended_entity": "C-Corp",
  "cap_table_template": [...],
  "key_documents_checklist": [...],
  "vesting_recommendation": "4-year vest with 1-year cliff"
}
```

### Multi-Skill Workflows (2 endpoints)

Workflows chain skills together for complete founder journeys:

```bash
# Workflow 1: Validate → Business Model → Pitch Deck
POST /api/startup-copilot/workflow/validate-to-pitch
Body: {
  "workflow_type": "validate-to-pitch",
  "founder_background": {...},
  "product_description": "Stablecoin bank for freelancers",
  "target_market": "LatAm freelancers"
}
Response: {
  "workflow_type": "validate-to-pitch",
  "steps": [
    {"step": 1, "skill": "idea-validation", "verdict": "go"},
    {"step": 2, "skill": "business-model", "ltv_cac_ratio": 2.5},
    {"step": 3, "skill": "fundraising", "investor_count": 100}
  ],
  "final_output": {
    "validation_verdict": "go",
    "business_model": "transactional_fintech",
    "pitch_deck_ready": true
  }
}

# Workflow 2: Validate → Business Model → GTM → Product
POST /api/startup-copilot/workflow/validate-to-launch
Body: {
  "workflow_type": "validate-to-launch",
  "founder_background": {...},
  "product_description": "...",
  "target_market": "..."
}
Response: {
  "workflow_type": "validate-to-launch",
  "steps": [
    {"step": 1, "skill": "idea-validation", "verdict": "go"},
    {"step": 2, "skill": "gotomarket", "recommended_motion": "hybrid"},
    {"step": 3, "skill": "product", "top_3_priorities": [...]}
  ],
  "final_output": {
    "validation_verdict": "go",
    "gtm_motion": "hybrid",
    "ready_to_build": true
  }
}
```

### Metadata Endpoints

```bash
# List all skills and workflows
GET /api/startup-copilot/skills

# Health check
GET /api/startup-copilot/health
```

---

## Engine Architecture

### Base Class: `StartupCopilotEngine`

```python
class StartupCopilotEngine:
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    DEFAULT_MODEL = "claude-sonnet-4.5"  # Claude for founder guidance
```

### Each Skill Engine

Example: `IdeaValidationEngine`

```python
class IdeaValidationEngine(StartupCopilotEngine):
    PURPOSE = "Validate founder-market fit and market viability"
    
    MOM_TEST_CRITERIA = {
        "founder_market_fit": {...},
        "market_viability": {...},
        "timing": {...}
    }
    
    async def validate(self, input_data: IdeaValidationInput) -> IdeaValidationOutput:
        # 1. Construct validation prompt with frameworks
        # 2. Call LLM (Claude/GPT/Gemini via emergentintegrations)
        # 3. Parse structured output
        # 4. Return IdeaValidationOutput
```

### LLM Integration

Uses `emergentintegrations.llm.chat`:

```python
llm = LlmChat(
    model_name="claude-sonnet-4.5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = await llm.complete_chat_async(
    messages=[UserMessage(content=prompt)]
)

result_json = json.loads(response.message.content)
return OutputModel(**result_json)
```

---

## Usage Examples

### Example 1: Validate a Stablecoin Bank Idea

```python
import asyncio
from backend.services.startup_copilot_engines import IdeaValidationEngine
from backend.services.startup_copilot_models import (
    FounderBackground, IdeaValidationInput
)

async def main():
    engine = IdeaValidationEngine()
    
    founder = FounderBackground(
        years_experience=5,
        domain="fintech",
        previous_exits=1,
        industry_relationships=["regulators", "payment processors"]
    )
    
    validation_input = IdeaValidationInput(
        founder_background=founder,
        market_problem="Freelancers in LatAm can't receive USD easily",
        existing_solutions=["Payoneer (expensive)", "Wise (doesn't work in some countries)"],
        interviews_conducted=10
    )
    
    result = await engine.validate(validation_input)
    
    print(f"Verdict: {result.verdict}")
    print(f"Confidence: {result.confidence}")
    print(f"Founder-Market Fit Score: {result.founder_market_fit_score}")
    print(f"Next Steps: {result.next_steps}")

asyncio.run(main())
```

### Example 2: API Call (cURL)

```bash
curl -X POST http://localhost:8001/api/startup-copilot/validate-idea \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "founder_background": {
      "years_experience": 5,
      "domain": "fintech",
      "previous_exits": 1,
      "industry_relationships": ["regulators", "processors"]
    },
    "market_problem": "Freelancers in LatAm cant receive USD",
    "existing_solutions": ["Payoneer", "Wise"],
    "interviews_conducted": 10
  }'
```

### Example 3: Chained Workflow (Validation → Pitch)

```bash
curl -X POST http://localhost:8001/api/startup-copilot/workflow/validate-to-pitch \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "validate-to-pitch",
    "founder_background": {...},
    "product_description": "Stablecoin bank for freelancers",
    "target_market": "LatAm freelancers"
  }'
```

---

## Framework References Built In

Each skill encodes proven methodologies:

1. **Idea Validation:** Mom Test (ask right questions), GO/PIVOT/KILL
2. **Business Model:** 55 patterns library, LTV/CAC calculations
3. **Fundraising:** VC decision research (63% prefer multiples), Sequoia deck
4. **GTM:** Product-Led Growth vs. Sales-Led decision tree, Racecar framework
5. **Product:** INVEST user stories, RICE prioritization
6. **Sales:** MEDDIC (enterprise), BANT (SMB), Challenger (differentiated)
7. **Marketing:** 80/20 distribution rule, content pillar clusters, SEO playbook
8. **Growth:** AARRR metrics, North Star, cohort retention analysis
9. **Operations:** OKR framework, interview scorecards, bias reduction
10. **Finance:** Burn rate, runway calculation, cash flow modeling
11. **Customer Success:** Onboarding milestones (D0-M2), health scoring
12. **Legal:** Entity selection, cap table management, compliance checklists

---

## Integration with HIC

### Pipeline Composer

Startup Copilot skills integrate with the existing Pipeline Composer:

```python
from services.pipeline_composer import PipelineComposerEngine

composer = PipelineComposerEngine()

# Automatically discovers Startup Copilot skills
# Can chain them in custom workflows:
# validate-idea → business-model → fundraising → gtm → product
```

### Billing & Metering

Each skill execution counts against monthly allowances (like other HIC engines):

- Free plan: 100 executions/month
- HIC Pro: 5,000 executions/month
- Enterprise: Negotiated capacity

Tracked via `SubscriptionUsageMiddleware`.

### Team & Workspace Access

Founder guidance is available to all team members with API access:
- JWT workspace authentication
- `hic_` API keys
- Team usage limits enforced per workspace

---

## Phase Roadmap

### ✅ Phase 1 (Complete): Documentation
- STARTUP_COPILOT_SKILLS.md with all frameworks
- 25+ knowledge artifacts (templates, calculators)
- Real-world example (stablecoin bank)

### ✅ Phase 2 (Complete): Backend Implementation
- 12 skill engines with LLM integration
- Pydantic models for all inputs/outputs
- FastAPI endpoints + 2 workflows
- Full server.py integration

### 🔄 Phase 3 (Coming): Frontend UI & Advanced Features
- Founder dashboard (multi-step form → results)
- Real-time collaboration (multiple founders)
- Export to PDF (pitch deck, PRD, etc.)
- Artifact storage (save & version results)

### 🔄 Phase 4 (Coming): Enterprise & Analytics
- White-label for accelerators (Y Combinator, TechStars)
- Cohort analytics (which frameworks work by industry)
- Revenue-share model with accelerators
- Founder success metrics tracking

---

## Testing & Validation

### Manual Testing (cURL)

```bash
# Test idea validation endpoint
curl -X POST http://localhost:8001/api/startup-copilot/validate-idea \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Response should match IdeaValidationOutput schema
```

### Automated Tests (Coming in Phase 3)

```python
def test_idea_validation_engine():
    engine = IdeaValidationEngine()
    input_data = IdeaValidationInput(...)
    result = asyncio.run(engine.validate(input_data))
    
    assert result.verdict in ["go", "pivot", "kill"]
    assert 0 <= result.confidence <= 1.0
    assert len(result.findings) > 0
```

---

## Deployment Notes

### Environment Variables Required

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (GPT)
OPENAI_API_KEY=sk-...

# (Optional) Gemini
GOOGLE_API_KEY=...
```

### Dependencies

```python
# In requirements.txt (add if not present):
emergentintegrations>=1.0.0
pydantic>=2.0.0
fastapi>=0.100.0
```

### Starting the Server

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

Server starts with Startup Copilot endpoints ready at `/api/startup-copilot/`.

---

## Next Steps

1. **Frontend UI** (Phase 3)
   - React components for each skill
   - Multi-step forms collecting input
   - Results visualization
   - PDF export

2. **Advanced Analytics** (Phase 4)
   - Track which skills are used most
   - Cohort analysis by industry/stage
   - Founder success metrics
   - Feature usage dashboard

3. **Accelerator Integration**
   - White-label version for Y Combinator
   - Custom frameworks per accelerator
   - Cohort-level insights
   - Revenue-share model

---

## API Reference

**Base URL:** `http://localhost:8001/api/startup-copilot/`

**Authentication:** JWT workspace token or `hic_` API key (via header `Authorization: Bearer TOKEN`)

**Response Format:** All responses wrapped in `SkillResponse`:
```json
{
  "skill": "skill-name",
  "status": "success|error",
  "data": {...},
  "error": null,
  "metadata": {...}
}
```

**Rate Limits:** Enforced per workspace (see HIC billing tiers)

---

## Support & Questions

- Framework methodology questions: See STARTUP_COPILOT_SKILLS.md
- Implementation details: See code comments in engines
- API usage: POST to endpoints with schema-matching input
- Integration: Startup Copilot follows standard HIC engine patterns

---

Generated with Claude Code | Startup Copilot v1.0.0

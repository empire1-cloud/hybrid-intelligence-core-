# Engine Contract Specification

## Overview

Every engine in the Hybrid Intelligence Core (HIC) must expose a standardized **Engine Contract** that describes:
- What it does
- What it expects (inputs)
- What it produces (outputs)
- Performance characteristics (latency, cost)
- Quality metrics (confidence, reliability)
- Provider and model information
- Canonical behavior and output shape

This contract allows the HIC to:
- Route requests intelligently
- Compose pipelines automatically
- Monitor for drift and quality issues
- Track cost and performance
- Prove differentiation between engines
- Build evidence over time

---

## Engine Contract Schema

```json
{
  "engine_id": "strategy",
  "engine_name": "Strategy Engine",
  "version": "1.0.0",
  "category": "business_intelligence",
  "description": "Generates actionable strategies for any goal",
  
  "capabilities": [
    "strategic planning",
    "risk analysis",
    "goal decomposition",
    "action prioritization"
  ],
  
  "input_schema": {
    "type": "object",
    "required": ["goal"],
    "properties": {
      "goal": {
        "type": "string",
        "description": "The strategic objective to analyze"
      },
      "context": {
        "type": "string",
        "description": "Additional context or constraints"
      },
      "tone": {
        "type": "string",
        "enum": ["direct", "analytical", "creative"],
        "default": "direct"
      }
    }
  },
  
  "output_schema": {
    "type": "object",
    "required": ["summary", "steps", "risks", "resources", "next_action"],
    "properties": {
      "summary": {
        "type": "string",
        "description": "High-level strategy overview"
      },
      "steps": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Execution steps in order"
      },
      "risks": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Identified risks and blind spots"
      },
      "resources": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Required resources and capabilities"
      },
      "next_action": {
        "type": "string",
        "description": "Immediate next step"
      }
    }
  },
  
  "provider": {
    "name": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "alternative_models": [
      "gpt-5.2",
      "gpt-4o"
    ]
  },
  
  "performance": {
    "latency_p50_ms": 1200,
    "latency_p95_ms": 2500,
    "latency_p99_ms": 3500,
    "cost_per_execution_usd": 0.045
  },
  
  "quality": {
    "confidence": 0.92,
    "reliability": 0.98,
    "canon_compliance_rate": 0.96
  },
  
  "canonical": {
    "required_fields": ["summary", "steps", "risks", "resources", "next_action"],
    "forbidden_phrases": [
      "As an AI",
      "I cannot",
      "I'm sorry but"
    ],
    "output_format": "json",
    "min_steps": 3,
    "min_summary_length": 50
  },
  
  "evidence_state": {
    "executions_tracked": 1247,
    "success_rate": 0.97,
    "average_output_quality": 0.91,
    "last_updated": "2026-09-09T10:22:00Z"
  }
}
```

---

## Engine Categories

The 19 engines are organized into 5 strategic categories:

### 🧠 Orchestration Layer
- **Hybrid Intelligence Core** (`/core/execute`)
- **Routing Engine** (Task → Model decision)
- **Pipeline Composer** (Multi-engine orchestration)

### ⚙️ Business Intelligence Engines
- **Strategy Engine** - High-level strategic thinking
- **Plan Builder** - Goal → Execution timeline
- **Analysis Engine** - SWOT / Deep analysis
- **Opportunity Mapper** - High-leverage opportunities
- **Evaluator Engine** - Scoring and viability
- **Pricing Engine** - Monetization structures
- **Blueprint Engine** - System architecture
- **Persona Engine** - User/customer profiles
- **Money Pipeline Engine** - Idea → Revenue (killer vertical)

### 🎨 Creative Engines (Genesis Vertical)
- **Anime Character Engine** - Original characters
- **Anime Lore Engine** - World-building
- **Anime Story Engine** - Narrative structures
- **Art Direction Engine** - Visual direction

### 🛡️ Governance Layer
- **Canon Enforcer** - Output normalization + rules
- **Drift Monitor** - Quality tracking
- **Error Handler** - Structured error handling

### 📊 System Layer
- **Analytics Engine** - Metrics and reporting
- **Execution Logger** - Action tracking

---

## Engine Discovery API

Every engine exposes its contract via:

```
GET /engine/{engine_id}/contract
```

Response:
```json
{
  "engine_id": "strategy",
  "engine_name": "Strategy Engine",
  "version": "1.0.0",
  "category": "business_intelligence",
  "capabilities": [...],
  "input_schema": {...},
  "output_schema": {...},
  "provider": {...},
  "performance": {...},
  "quality": {...},
  "canonical": {...},
  "evidence_state": {...}
}
```

---

## Composition Rules

Engines compose via:

1. **Output feed forward** - Engine A's output becomes Engine B's input
2. **Schema matching** - Output fields map to input parameters
3. **Evidence accumulation** - Each step adds to the evidence state
4. **Canonical validation** - Each output must pass Canon enforcement
5. **Drift monitoring** - Quality tracked per engine per model

---

## Evidence State Tracking

Each engine tracks:
- Total executions
- Success rate
- Average output quality (0-1 score)
- Error rate by type
- Cost per execution
- Latency distribution
- Model performance comparison
- Last execution timestamp
- Provider/model decision history

---

## Contract Versioning

Engines maintain multiple versions:
- `engine_id:1.0` - Stable, production version
- `engine_id:1.1` - Minor enhancements
- `engine_id:2.0` - Major capability changes

Migration path: Older contracts supported but deprecated.

---

## Governance Integration

### Canon Rules (Per Engine)
- Forbidden phrases
- Required output fields
- Field type validation
- Minimum/maximum content lengths
- Format requirements

### Drift Monitoring (Per Engine)
- Output quality baseline
- Behavioral change detection
- Provider performance comparison
- Cost vs. quality tradeoff

### Evidence Accumulation (Per Engine)
- Execution history
- Success/failure patterns
- Provider reliability
- Model comparison data

---

## Money Pipeline Contract (Example of Structured Output)

The **Money Pipeline** engine follows this enhanced contract:

```json
{
  "input": {
    "idea": "string",
    "context": "string",
    "industry": "string",
    "target_revenue": "string",
    "constraints": ["string"]
  },
  
  "output": {
    "market_analysis": {
      "target_segments": ["string"],
      "pain_points": ["string"],
      "demand_drivers": ["string"],
      "competitive_landscape": ["string"],
      "positioning_opportunity": "string"
    },
    
    "customer": {
      "description": "string",
      "problem_statement": "string",
      "willingness_to_pay": "string"
    },
    
    "offer": {
      "core_value_prop": "string",
      "differentiation": "string",
      "go_to_market": "string"
    },
    
    "pricing": {
      "model": "string",
      "tiers": [
        {
          "name": "string",
          "price": "string",
          "features": ["string"]
        }
      ],
      "metrics": ["string"]
    },
    
    "acquisition": {
      "channels": ["string"],
      "strategy": "string",
      "cap_required": "string"
    },
    
    "delivery": {
      "model": "string",
      "unit_economics": {
        "cogs": "string",
        "margin": "string",
        "payback_period": "string"
      }
    },
    
    "revenue_event": {
      "type": "string",
      "frequency": "string",
      "average_value": "string"
    },
    
    "unit_economics": {
      "customer_lifetime_value": "string",
      "customer_acquisition_cost": "string",
      "payback_period": "string",
      "gross_margin": "string"
    },
    
    "execution_plan": {
      "phase_1": ["string"],
      "phase_2": ["string"],
      "phase_3": ["string"],
      "critical_path": ["string"]
    }
  }
}
```

This contract proves that Money Pipeline is a **killer engine** because:
1. It's not generic output — it's highly structured
2. It can feed directly into other engines (Blueprint, Pricing, Persona, etc.)
3. It's vertically differentiated (SaaS vs. Service vs. E-commerce)
4. It proves monetization thinking, not just ideation

---

## Next Steps

1. ✅ Define Engine Contract schema (this document)
2. ⬜ Create `EngineContract` Pydantic model
3. ⬜ Add contract exposure to each engine
4. ⬜ Build `GET /engine/{id}/contract` endpoint
5. ⬜ Create Engine Discovery/Registry service
6. ⬜ Enhance Drift/Canon with contract awareness
7. ⬜ Build orchestration dashboard
8. ⬜ Document "one system thinking" vs. "19 engines thinking"

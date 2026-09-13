"""
Engine Discovery and Registry API Endpoints

Exposes engine contracts and orchestration metadata.
Implements the Engine Contract pattern from the architectural review.
"""

from fastapi import APIRouter
from typing import List, Dict, Any, Optional

from services.engine_registry import get_registry
from models.engine_contract import EngineCategory

router = APIRouter(tags=["engine-discovery"], prefix="/engines")


# === DISCOVERY ENDPOINTS ===

@router.get("/discovery")
async def engine_discovery() -> Dict[str, Any]:
    """
    Get discovery list of all available engines.

    Returns minimal info for dashboard/UI:
    - Engine ID, name, category, capabilities
    - Quick overview without full contract details
    """
    registry = get_registry()
    return registry.discovery_list()


@router.get("/{engine_id}/contract")
async def get_engine_contract(engine_id: str) -> Dict[str, Any]:
    """
    Get complete contract for a specific engine.

    Returns:
    - Input/output schemas
    - Performance metrics
    - Quality metrics
    - Canonical rules
    - Provider info
    - Evidence state
    """
    registry = get_registry()
    contract = registry.get_contract(engine_id)

    if not contract:
        return {
            "error": f"Engine '{engine_id}' not found",
            "status": 404
        }

    return contract.model_dump(mode='json')


@router.get("/contracts/all")
async def list_all_contracts() -> Dict[str, Any]:
    """List all engine contracts (full details)."""
    registry = get_registry()
    contracts = registry.list_all_contracts()

    return {
        "total_engines": len(contracts),
        "contracts": [c.model_dump(mode='json') for c in contracts]
    }


# === CATEGORY FILTERING ===

@router.get("/by-category/{category}")
async def engines_by_category(category: str) -> Dict[str, Any]:
    """Get engines in a specific category."""
    registry = get_registry()

    try:
        category_enum = EngineCategory(category)
    except ValueError:
        return {
            "error": f"Invalid category: {category}",
            "valid_categories": [c.value for c in EngineCategory],
            "status": 400
        }

    contracts = registry.list_by_category(category_enum)

    return {
        "category": category,
        "count": len(contracts),
        "engines": [
            {
                "engine_id": c.engine_id,
                "engine_name": c.engine_name,
                "description": c.description,
                "capabilities": c.capabilities
            }
            for c in contracts
        ]
    }


@router.get("/categories")
async def list_categories() -> Dict[str, Any]:
    """Get all engine categories and engine counts."""
    registry = get_registry()
    status = registry.get_system_status()

    return {
        "categories": status["by_category"],
        "total_engines": status["total_engines"]
    }


# === CAPABILITY FILTERING ===

@router.get("/by-capability/{capability}")
async def engines_by_capability(capability: str) -> Dict[str, Any]:
    """Get engines that provide a specific capability."""
    registry = get_registry()
    contracts = registry.list_by_capability(capability)

    return {
        "capability": capability,
        "count": len(contracts),
        "engines": [
            {
                "engine_id": c.engine_id,
                "engine_name": c.engine_name,
                "provider": c.provider.model,
                "cost_per_execution": c.performance.cost_per_execution_usd
            }
            for c in contracts
        ]
    }


# === TAG-BASED FILTERING ===

@router.get("/by-tag/{tag}")
async def engines_by_tag(tag: str) -> Dict[str, Any]:
    """Get engines with a specific tag."""
    registry = get_registry()
    contracts = registry.find_by_tag(tag)

    return {
        "tag": tag,
        "count": len(contracts),
        "engines": [c.engine_id for c in contracts]
    }


@router.get("/killer-engines")
async def get_killer_engines() -> Dict[str, Any]:
    """
    Get high-value 'killer' engines.

    These are commercially significant engines:
    - money_pipeline: Idea → Revenue
    - pipeline_composer: Multi-engine orchestration
    """
    registry = get_registry()
    killer_engines = registry.get_killer_engines()

    return {
        "killer_engines": len(killer_engines),
        "engines": [
            {
                "engine_id": c.engine_id,
                "engine_name": c.engine_name,
                "description": c.description,
                "capabilities": c.capabilities,
                "cost_per_execution": c.performance.cost_per_execution_usd
            }
            for c in killer_engines
        ]
    }


# === ORCHESTRATION INFORMATION ===

@router.get("/orchestration-catalog")
async def get_orchestration_catalog() -> Dict[str, Any]:
    """
    Get orchestration catalog for pipeline composition.

    Formatted for pipeline orchestration (input/output keys, routing info).
    """
    registry = get_registry()
    return registry.orchestration_catalog()


@router.get("/orchestration/templates")
async def get_pipeline_templates() -> Dict[str, Any]:
    """
    Get available pipeline composition templates.

    Returns pre-built orchestration patterns.
    """
    return {
        "templates": {
            "full_business_plan": {
                "name": "Full Business Plan",
                "description": "Strategy → Analysis → Opportunities → Execution Plan → Pricing → Evaluation",
                "engines": ["strategy", "analysis", "opportunity", "plan_builder", "pricing", "evaluator"],
                "output": "Complete business strategy with pricing and execution roadmap"
            },
            "product_launch": {
                "name": "Product Launch",
                "description": "Personas → Strategy → Pricing → Launch Plan",
                "engines": ["persona", "strategy", "pricing", "plan_builder"],
                "output": "Product launch strategy with go-to-market plan"
            },
            "startup_validation": {
                "name": "Startup Validation",
                "description": "Analysis → Personas → Opportunities → Viability Score",
                "engines": ["analysis", "persona", "opportunity", "evaluator"],
                "output": "Startup viability assessment and market analysis"
            },
            "system_design": {
                "name": "System Design",
                "description": "Strategy → Architecture → Build Plan → Review",
                "engines": ["strategy", "blueprint", "plan_builder", "evaluator"],
                "output": "Complete system architecture with implementation plan"
            },
            "idea_to_money": {
                "name": "Idea to Money (MONEY PIPELINE)",
                "description": "Money Pipeline → Personas → Architecture → Viability",
                "engines": ["money_pipeline", "persona", "blueprint", "evaluator"],
                "output": "Complete monetization system with unit economics",
                "category": "killer_vertical"
            },
            "anime_full_concept": {
                "name": "Anime Full Concept",
                "description": "Lore → Story → Characters → Art Direction",
                "engines": ["anime_lore", "anime_story", "anime_character", "art_direction"],
                "output": "Complete anime concept with world, story, characters, and visual direction",
                "category": "creative"
            }
        }
    }


# === PERFORMANCE & COST ANALYSIS ===

@router.get("/performance/comparison")
async def engine_performance_comparison() -> Dict[str, Any]:
    """
    Compare performance metrics across engines.

    Returns latency, cost, and quality for routing decisions.
    """
    registry = get_registry()
    contracts = registry.list_all_contracts()

    performance_data = []
    for contract in contracts:
        performance_data.append({
            "engine_id": contract.engine_id,
            "engine_name": contract.engine_name,
            "latency_p50": contract.performance.latency_p50_ms,
            "latency_p95": contract.performance.latency_p95_ms,
            "cost_per_execution": contract.performance.cost_per_execution_usd,
            "confidence": contract.quality.confidence,
            "reliability": contract.quality.reliability,
            "provider": contract.provider.model
        })

    # Sort by cost
    performance_data.sort(key=lambda x: x["cost_per_execution"])

    return {
        "total_engines": len(performance_data),
        "engines": performance_data,
        "cost_summary": {
            "min": min(e["cost_per_execution"] for e in performance_data),
            "max": max(e["cost_per_execution"] for e in performance_data),
            "average": sum(e["cost_per_execution"] for e in performance_data) / len(performance_data)
        }
    }


# === SYSTEM STATUS ===

@router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get overall system status.

    Returns engine health, categories, capabilities overview.
    """
    registry = get_registry()
    return registry.get_system_status()


# === INTELLIGENCE SUMMARY ===

@router.get("/summary")
async def engine_system_summary() -> Dict[str, Any]:
    """
    Executive summary of the Hybrid Intelligence Core.

    Demonstrates architecture from review: "19 governed intelligence engines · unified execution · composable pipelines"
    """
    registry = get_registry()
    status = registry.get_system_status()
    killer_engines = registry.get_killer_engines()
    all_contracts = registry.list_all_contracts()

    # Calculate aggregate metrics
    total_cost = sum(c.performance.cost_per_execution_usd for c in all_contracts)
    avg_latency = sum(c.performance.latency_p50_ms for c in all_contracts) / len(all_contracts)
    avg_reliability = sum(c.quality.reliability for c in all_contracts) / len(all_contracts)

    return {
        "system": "Hybrid Intelligence Core (HIC)",
        "description": "19 governed intelligence engines · unified execution · composable pipelines",
        "architecture": {
            "orchestration_layer": {
                "count": 3,
                "engines": ["hybrid_intelligence_core", "routing", "pipeline_composer"],
                "purpose": "Unified execution and multi-engine orchestration"
            },
            "business_intelligence": {
                "count": 9,
                "engines": [
                    "strategy", "plan_builder", "analysis", "opportunity",
                    "evaluator", "pricing", "blueprint", "persona", "money_pipeline"
                ],
                "purpose": "Strategic thinking and monetization"
            },
            "creative_vertical": {
                "count": 4,
                "engines": ["anime_character", "anime_lore", "anime_story", "art_direction"],
                "purpose": "Creative generation and world-building"
            },
            "governance_layer": {
                "count": 3,
                "engines": ["canon_enforcer", "drift_monitor", "error_handler"],
                "purpose": "Output normalization, quality tracking, error handling"
            }
        },
        "killer_engines": {
            "count": len(killer_engines),
            "primary": "money_pipeline (Idea → Revenue)",
            "secondary": "pipeline_composer (Multi-engine orchestration)"
        },
        "capabilities": {
            "total_unique": status["capabilities"],
            "examples": [
                "strategic planning", "execution planning", "monetization",
                "pricing", "market analysis", "risk assessment",
                "character generation", "world-building", "story design"
            ]
        },
        "performance": {
            "total_engines": status["total_engines"],
            "active_engines": status["active_engines"],
            "average_latency_ms": round(avg_latency),
            "aggregate_cost_per_execution": round(total_cost, 3),
            "average_reliability": round(avg_reliability, 3)
        },
        "evidence_tracking": {
            "implemented": True,
            "tracks": [
                "execution count", "success rate", "output quality",
                "provider performance", "model performance", "drift",
                "cost per execution", "error rates"
            ]
        },
        "governance": {
            "canon_enforcement": True,
            "drift_monitoring": True,
            "error_handling": True,
            "model_policy": "approved-non-google-only"
        }
    }

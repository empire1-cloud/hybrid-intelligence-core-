"""
Engine Registry Service

Central registry for all engine contracts in HIC.
Enables discovery, routing, orchestration, and governance.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from models.engine_contract import (
    EngineContract,
    EngineCategory,
    ProviderConfig,
    PerformanceMetrics,
    QualityMetrics,
    CanonicalRules,
    EvidenceState,
    InputSchema,
    OutputSchema
)


class EngineRegistry:
    """
    Central registry managing all 19 engine contracts.

    Provides:
    - Engine discovery and introspection
    - Dynamic routing
    - Pipeline composition
    - Governance and drift tracking
    - Cost and performance analysis
    """

    # Singleton instance
    _instance = None
    _contracts: Dict[str, EngineContract] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._contracts = {}
        self._category_index: Dict[EngineCategory, List[str]] = {}
        self._capability_index: Dict[str, List[str]] = {}

        # Initialize with all 19 engines
        self._initialize_contracts()

    def _initialize_contracts(self):
        """Initialize all 19 engine contracts."""

        # === ORCHESTRATION LAYER ===

        self.register(EngineContract(
            engine_id="hybrid_intelligence_core",
            engine_name="Hybrid Intelligence Core",
            category=EngineCategory.ORCHESTRATION,
            description="Master orchestrator coordinating all engines through unified execution pipeline",
            capabilities=["routing", "orchestration", "governance", "execution", "logging"],
            input_schema=InputSchema(
                required=["prompt"],
                properties={
                    "prompt": {"type": "string", "description": "User input or task"},
                    "task_type": {"type": "string", "description": "Task classification"},
                    "context": {"type": "string", "description": "Additional context"}
                }
            ),
            output_schema=OutputSchema(
                required=["success", "data", "metadata"],
                properties={
                    "success": {"type": "boolean"},
                    "data": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            ),
            provider=ProviderConfig(name="hybrid", model="orchestrator", alternative_models=[]),
            performance=PerformanceMetrics(
                latency_p50_ms=1500,
                latency_p95_ms=3500,
                latency_p99_ms=5000,
                cost_per_execution_usd=0.0
            ),
            quality=QualityMetrics(confidence=0.99, reliability=0.99, canon_compliance_rate=1.0),
            canonical=CanonicalRules(
                required_fields=["success", "data"],
                output_format="json"
            ),
            tags=["orchestration", "critical"]
        ))

        self.register(EngineContract(
            engine_id="routing",
            engine_name="Routing Engine",
            category=EngineCategory.ORCHESTRATION,
            description="Routes tasks to appropriate models and engines based on task characteristics",
            capabilities=["task routing", "model selection", "classification"],
            input_schema=InputSchema(
                required=["task"],
                properties={"task": {"type": "string"}, "force_model": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["model", "reason"],
                properties={"model": {"type": "string"}, "reason": {"type": "string"}}
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=300, latency_p95_ms=800, latency_p99_ms=1200,
                cost_per_execution_usd=0.01
            ),
            quality=QualityMetrics(confidence=0.98, reliability=0.99, canon_compliance_rate=0.99),
            tags=["routing", "orchestration"]
        ))

        self.register(EngineContract(
            engine_id="pipeline_composer",
            engine_name="Pipeline Composer",
            category=EngineCategory.ORCHESTRATION,
            description="Orchestrates multi-engine workflows and sequences",
            capabilities=["pipeline composition", "engine sequencing", "output routing", "template management"],
            input_schema=InputSchema(
                required=["objective"],
                properties={
                    "objective": {"type": "string"},
                    "template": {"type": "string"},
                    "engines": {"type": "array"}
                }
            ),
            output_schema=OutputSchema(
                required=["pipeline", "results"],
                properties={
                    "pipeline": {"type": "array"},
                    "results": {"type": "object"}
                }
            ),
            provider=ProviderConfig(
                name="openai",
                model="gpt-5.2",
                alternative_models=["claude-sonnet-4-5-20250929"]
            ),
            performance=PerformanceMetrics(
                latency_p50_ms=2000,
                latency_p95_ms=4000,
                latency_p99_ms=6000,
                cost_per_execution_usd=0.08
            ),
            quality=QualityMetrics(confidence=0.95, reliability=0.96, canon_compliance_rate=0.94),
            tags=["orchestration", "monster_engine"]
        ))

        # === BUSINESS INTELLIGENCE ===

        self.register(EngineContract(
            engine_id="strategy",
            engine_name="Strategy Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Generates actionable strategies for any goal",
            capabilities=["strategic planning", "risk analysis", "goal decomposition", "action prioritization"],
            input_schema=InputSchema(
                required=["goal"],
                properties={"goal": {"type": "string"}, "context": {"type": "string"}, "tone": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["summary", "steps", "risks", "resources", "next_action"],
                properties={
                    "summary": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "risks": {"type": "array", "items": {"type": "string"}},
                    "resources": {"type": "array", "items": {"type": "string"}},
                    "next_action": {"type": "string"}
                }
            ),
            provider=ProviderConfig(
                name="anthropic",
                model="claude-sonnet-4-5-20250929",
                alternative_models=["gpt-5.2"]
            ),
            performance=PerformanceMetrics(
                latency_p50_ms=1200, latency_p95_ms=2500, latency_p99_ms=3500,
                cost_per_execution_usd=0.045
            ),
            quality=QualityMetrics(confidence=0.92, reliability=0.98, canon_compliance_rate=0.96),
            tags=["strategy", "core", "business_intelligence"]
        ))

        self.register(EngineContract(
            engine_id="plan_builder",
            engine_name="Plan Builder Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Converts goals and strategies into executable plans with timelines",
            capabilities=["execution planning", "timeline generation", "milestone definition", "phase decomposition"],
            input_schema=InputSchema(
                required=["goal"],
                properties={"goal": {"type": "string"}, "strategy": {"type": "object"}, "context": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["objective", "phases", "milestones", "critical_path"],
                properties={
                    "objective": {"type": "string"},
                    "phases": {"type": "array"},
                    "milestones": {"type": "array"},
                    "critical_path": {"type": "array"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1400, latency_p95_ms=2800, latency_p99_ms=4000,
                cost_per_execution_usd=0.052
            ),
            quality=QualityMetrics(confidence=0.90, reliability=0.97, canon_compliance_rate=0.95),
            tags=["planning", "execution", "business_intelligence"]
        ))

        self.register(EngineContract(
            engine_id="analysis",
            engine_name="Analysis Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Performs deep SWOT and analytical assessments",
            capabilities=["swot analysis", "competitive analysis", "risk assessment", "opportunity identification"],
            input_schema=InputSchema(
                required=["subject"],
                properties={"subject": {"type": "string"}, "context": {"type": "string"}, "focus": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["overview", "strengths", "weaknesses", "opportunities", "threats"],
                properties={
                    "overview": {"type": "string"},
                    "strengths": {"type": "array"},
                    "weaknesses": {"type": "array"},
                    "opportunities": {"type": "array"},
                    "threats": {"type": "array"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1300, latency_p95_ms=2600, latency_p99_ms=3800,
                cost_per_execution_usd=0.048
            ),
            quality=QualityMetrics(confidence=0.91, reliability=0.97, canon_compliance_rate=0.94),
            tags=["analysis", "strategy"]
        ))

        self.register(EngineContract(
            engine_id="opportunity",
            engine_name="Opportunity Mapper Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Identifies high-leverage opportunities from situations",
            capabilities=["opportunity identification", "leverage analysis", "priority ranking"],
            input_schema=InputSchema(
                required=["situation"],
                properties={"situation": {"type": "string"}, "constraints": {"type": "array"}}
            ),
            output_schema=OutputSchema(
                required=["opportunities", "top_3"],
                properties={"opportunities": {"type": "array"}, "top_3": {"type": "array"}}
            ),
            provider=ProviderConfig(name="openai", model="gpt-5.2"),
            performance=PerformanceMetrics(
                latency_p50_ms=1100, latency_p95_ms=2400, latency_p99_ms=3200,
                cost_per_execution_usd=0.042
            ),
            quality=QualityMetrics(confidence=0.89, reliability=0.96, canon_compliance_rate=0.93),
            tags=["opportunity", "analysis"]
        ))

        self.register(EngineContract(
            engine_id="evaluator",
            engine_name="Evaluator Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Scores and evaluates ideas, businesses, and strategies against criteria",
            capabilities=["scoring", "evaluation", "viability assessment", "go/no-go decisions"],
            input_schema=InputSchema(
                required=["subject"],
                properties={"subject": {"type": "string"}, "criteria": {"type": "array"}}
            ),
            output_schema=OutputSchema(
                required=["score", "strengths", "weaknesses", "go_no_go"],
                properties={
                    "score": {"type": "number"},
                    "strengths": {"type": "array"},
                    "weaknesses": {"type": "array"},
                    "go_no_go": {"type": "string"}
                }
            ),
            provider=ProviderConfig(name="openai", model="gpt-4o"),
            performance=PerformanceMetrics(
                latency_p50_ms=1000, latency_p95_ms=2200, latency_p99_ms=3000,
                cost_per_execution_usd=0.038
            ),
            quality=QualityMetrics(confidence=0.93, reliability=0.98, canon_compliance_rate=0.97),
            tags=["evaluation", "scoring"]
        ))

        self.register(EngineContract(
            engine_id="pricing",
            engine_name="Pricing Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Generates pricing structures and monetization models",
            capabilities=["pricing structure generation", "tier definition", "market positioning", "revenue modeling"],
            input_schema=InputSchema(
                required=["product"],
                properties={"product": {"type": "string"}, "market": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["model", "tiers"],
                properties={"model": {"type": "string"}, "tiers": {"type": "array"}}
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1150, latency_p95_ms=2400, latency_p99_ms=3300,
                cost_per_execution_usd=0.045
            ),
            quality=QualityMetrics(confidence=0.90, reliability=0.96, canon_compliance_rate=0.94),
            tags=["pricing", "monetization"]
        ))

        self.register(EngineContract(
            engine_id="blueprint",
            engine_name="Blueprint Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Creates system architecture blueprints and technical designs",
            capabilities=["architecture design", "system design", "component definition", "data flow modeling"],
            input_schema=InputSchema(
                required=["system"],
                properties={"system": {"type": "string"}, "requirements": {"type": "array"}}
            ),
            output_schema=OutputSchema(
                required=["components", "data_flows"],
                properties={"components": {"type": "array"}, "data_flows": {"type": "array"}}
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1300, latency_p95_ms=2700, latency_p99_ms=3900,
                cost_per_execution_usd=0.050
            ),
            quality=QualityMetrics(confidence=0.88, reliability=0.95, canon_compliance_rate=0.92),
            tags=["architecture", "design"]
        ))

        self.register(EngineContract(
            engine_id="persona",
            engine_name="Persona Engine",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Generates detailed user and customer personas",
            capabilities=["persona generation", "user modeling", "customer profiling", "behavior prediction"],
            input_schema=InputSchema(
                required=["audience"],
                properties={"audience": {"type": "string"}, "context": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["name", "role", "background", "goals", "pains"],
                properties={
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "background": {"type": "string"},
                    "goals": {"type": "array"},
                    "pains": {"type": "array"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1200, latency_p95_ms=2500, latency_p99_ms=3500,
                cost_per_execution_usd=0.045
            ),
            quality=QualityMetrics(confidence=0.91, reliability=0.97, canon_compliance_rate=0.95),
            tags=["persona", "user_research"]
        ))

        self.register(EngineContract(
            engine_id="money_pipeline",
            engine_name="Money Pipeline Engine (KILLER VERTICAL)",
            category=EngineCategory.BUSINESS_INTELLIGENCE,
            description="Transforms any idea into complete, monetizable, execution-ready system",
            capabilities=[
                "idea monetization", "revenue modeling", "market analysis",
                "business model generation", "execution planning", "unit economics"
            ],
            input_schema=InputSchema(
                required=["idea"],
                properties={
                    "idea": {"type": "string"},
                    "context": {"type": "string"},
                    "industry": {"type": "string"},
                    "target_revenue": {"type": "string"}
                }
            ),
            output_schema=OutputSchema(
                required=["market_analysis", "opportunity_map", "pricing_model", "business_model",
                         "product_blueprint", "execution_plan", "forecast", "unit_economics"],
                properties={
                    "market_analysis": {"type": "object"},
                    "opportunity_map": {"type": "object"},
                    "pricing_model": {"type": "object"},
                    "business_model": {"type": "object"},
                    "product_blueprint": {"type": "object"},
                    "execution_plan": {"type": "object"},
                    "forecast": {"type": "object"},
                    "unit_economics": {"type": "object"}
                }
            ),
            provider=ProviderConfig(
                name="anthropic",
                model="claude-sonnet-4-5-20250929",
                alternative_models=["gpt-5.2"]
            ),
            performance=PerformanceMetrics(
                latency_p50_ms=2500,
                latency_p95_ms=5000,
                latency_p99_ms=7000,
                cost_per_execution_usd=0.120
            ),
            quality=QualityMetrics(confidence=0.94, reliability=0.97, canon_compliance_rate=0.96),
            canonical=CanonicalRules(
                required_fields=["market_analysis", "opportunity_map", "pricing_model", "business_model",
                                "product_blueprint", "execution_plan", "forecast", "unit_economics"]
            ),
            tags=["monetization", "killer_vertical", "high_value"]
        ))

        # === CREATIVE ENGINES ===

        self.register(EngineContract(
            engine_id="anime_character",
            engine_name="Anime Character Engine",
            category=EngineCategory.CREATIVE,
            description="Generates original anime characters with personality, abilities, and arcs",
            capabilities=["character creation", "personality modeling", "ability generation", "backstory creation"],
            input_schema=InputSchema(
                required=["concept"],
                properties={"concept": {"type": "string"}, "genre": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["name", "personality", "abilities", "backstory"],
                properties={
                    "name": {"type": "string"},
                    "personality": {"type": "object"},
                    "abilities": {"type": "array"},
                    "backstory": {"type": "string"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1500, latency_p95_ms=3000, latency_p99_ms=4200,
                cost_per_execution_usd=0.055
            ),
            quality=QualityMetrics(confidence=0.89, reliability=0.95, canon_compliance_rate=0.92),
            tags=["creative", "anime", "character_design"]
        ))

        self.register(EngineContract(
            engine_id="anime_lore",
            engine_name="Anime Lore Engine",
            category=EngineCategory.CREATIVE,
            description="Creates anime world-building, mythology, and factions",
            capabilities=["world-building", "lore creation", "mythology design", "faction development"],
            input_schema=InputSchema(
                required=["world_concept"],
                properties={"world_concept": {"type": "string"}, "themes": {"type": "array"}}
            ),
            output_schema=OutputSchema(
                required=["world_name", "mythology", "factions", "locations"],
                properties={
                    "world_name": {"type": "string"},
                    "mythology": {"type": "object"},
                    "factions": {"type": "array"},
                    "locations": {"type": "array"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1600, latency_p95_ms=3200, latency_p99_ms=4500,
                cost_per_execution_usd=0.060
            ),
            quality=QualityMetrics(confidence=0.88, reliability=0.94, canon_compliance_rate=0.91),
            tags=["creative", "anime", "lore", "world_building"]
        ))

        self.register(EngineContract(
            engine_id="anime_story",
            engine_name="Anime Story Engine",
            category=EngineCategory.CREATIVE,
            description="Generates anime narrative structures, story arcs, and plot progressions",
            capabilities=["story design", "narrative structure", "plot generation", "character arc design"],
            input_schema=InputSchema(
                required=["concept"],
                properties={"concept": {"type": "string"}, "episode_count": {"type": "integer"}}
            ),
            output_schema=OutputSchema(
                required=["title", "premise", "story_arcs", "key_plot_points"],
                properties={
                    "title": {"type": "string"},
                    "premise": {"type": "string"},
                    "story_arcs": {"type": "array"},
                    "key_plot_points": {"type": "array"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1700, latency_p95_ms=3400, latency_p99_ms=4800,
                cost_per_execution_usd=0.065
            ),
            quality=QualityMetrics(confidence=0.87, reliability=0.93, canon_compliance_rate=0.90),
            tags=["creative", "anime", "story", "narrative"]
        ))

        self.register(EngineContract(
            engine_id="art_direction",
            engine_name="Art Direction Engine",
            category=EngineCategory.CREATIVE,
            description="Complete art direction for creative projects",
            capabilities=["visual style definition", "color palette design", "mood/tone direction", "aesthetic guidance"],
            input_schema=InputSchema(
                required=["project"],
                properties={"project": {"type": "string"}, "mood": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["visual_style", "color_palette", "character_style"],
                properties={
                    "visual_style": {"type": "string"},
                    "color_palette": {"type": "array"},
                    "character_style": {"type": "string"}
                }
            ),
            provider=ProviderConfig(name="anthropic", model="claude-sonnet-4-5-20250929"),
            performance=PerformanceMetrics(
                latency_p50_ms=1400, latency_p95_ms=2900, latency_p99_ms=4000,
                cost_per_execution_usd=0.052
            ),
            quality=QualityMetrics(confidence=0.86, reliability=0.92, canon_compliance_rate=0.89),
            tags=["creative", "art", "design", "visual"]
        ))

        # === GOVERNANCE LAYER ===

        self.register(EngineContract(
            engine_id="canon_enforcer",
            engine_name="Canon Enforcer",
            category=EngineCategory.GOVERNANCE,
            description="Enforces output normalization and canonicalization rules",
            capabilities=["output normalization", "rule enforcement", "compliance validation", "phrase filtering"],
            input_schema=InputSchema(
                required=["output"],
                properties={"output": {"type": "object"}}
            ),
            output_schema=OutputSchema(
                required=["normalized_output"],
                properties={"normalized_output": {"type": "object"}}
            ),
            provider=ProviderConfig(name="hybrid", model="local_processor"),
            performance=PerformanceMetrics(
                latency_p50_ms=50, latency_p95_ms=150, latency_p99_ms=300,
                cost_per_execution_usd=0.0
            ),
            quality=QualityMetrics(confidence=1.0, reliability=1.0, canon_compliance_rate=1.0),
            tags=["governance", "normalization", "critical"]
        ))

        self.register(EngineContract(
            engine_id="drift_monitor",
            engine_name="Drift Monitor",
            category=EngineCategory.GOVERNANCE,
            description="Monitors engine outputs for behavioral drift and quality degradation",
            capabilities=["drift detection", "quality tracking", "anomaly detection", "baseline comparison"],
            input_schema=InputSchema(
                required=["output"],
                properties={"output": {"type": "object"}, "model": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["drift_status", "metrics"],
                properties={
                    "drift_status": {"type": "string"},
                    "metrics": {"type": "object"}
                }
            ),
            provider=ProviderConfig(name="hybrid", model="local_processor"),
            performance=PerformanceMetrics(
                latency_p50_ms=75, latency_p95_ms=200, latency_p99_ms=400,
                cost_per_execution_usd=0.0
            ),
            quality=QualityMetrics(confidence=0.98, reliability=0.99, canon_compliance_rate=1.0),
            tags=["governance", "monitoring", "quality", "critical"]
        ))

        self.register(EngineContract(
            engine_id="error_handler",
            engine_name="Error Handler",
            category=EngineCategory.GOVERNANCE,
            description="Structures and classifies errors from any pipeline stage",
            capabilities=["error classification", "error structuring", "recovery guidance", "logging"],
            input_schema=InputSchema(
                required=["error"],
                properties={"error": {"type": "object"}, "stage": {"type": "string"}}
            ),
            output_schema=OutputSchema(
                required=["error_type", "message", "stage"],
                properties={
                    "error_type": {"type": "string"},
                    "message": {"type": "string"},
                    "stage": {"type": "string"}
                }
            ),
            provider=ProviderConfig(name="hybrid", model="local_processor"),
            performance=PerformanceMetrics(
                latency_p50_ms=25, latency_p95_ms=100, latency_p99_ms=200,
                cost_per_execution_usd=0.0
            ),
            quality=QualityMetrics(confidence=1.0, reliability=1.0, canon_compliance_rate=1.0),
            tags=["governance", "error_handling", "critical"]
        ))

        # Build indexes
        self._rebuild_indexes()

    def register(self, contract: EngineContract) -> None:
        """Register an engine contract."""
        self._contracts[contract.engine_id] = contract
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild category and capability indexes."""
        self._category_index = {}
        self._capability_index = {}

        for engine_id, contract in self._contracts.items():
            # Category index
            category = contract.category
            if category not in self._category_index:
                self._category_index[category] = []
            self._category_index[category].append(engine_id)

            # Capability index
            for capability in contract.capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = []
                self._capability_index[capability].append(engine_id)

    def get_contract(self, engine_id: str) -> Optional[EngineContract]:
        """Get a single engine contract."""
        return self._contracts.get(engine_id)

    def list_all_contracts(self) -> List[EngineContract]:
        """List all registered contracts."""
        return list(self._contracts.values())

    def list_by_category(self, category: EngineCategory) -> List[EngineContract]:
        """List engines by category."""
        engine_ids = self._category_index.get(category, [])
        return [self._contracts[eid] for eid in engine_ids if eid in self._contracts]

    def list_by_capability(self, capability: str) -> List[EngineContract]:
        """List engines by capability."""
        engine_ids = self._capability_index.get(capability, [])
        return [self._contracts[eid] for eid in engine_ids if eid in self._contracts]

    def find_by_tag(self, tag: str) -> List[EngineContract]:
        """Find engines by tag."""
        return [c for c in self._contracts.values() if tag in c.tags]

    def discovery_list(self) -> Dict[str, Any]:
        """Generate discovery list (minimal info for dashboard)."""
        return {
            "total_engines": len(self._contracts),
            "categories": {
                category.value: len(engines)
                for category, engines in self._category_index.items()
            },
            "engines": [
                {
                    "engine_id": c.engine_id,
                    "engine_name": c.engine_name,
                    "category": c.category,
                    "capabilities": c.capabilities,
                    "is_active": c.is_active
                }
                for c in self._contracts.values()
            ]
        }

    def orchestration_catalog(self) -> Dict[str, Any]:
        """Generate catalog for pipeline orchestration."""
        return {
            "orchestration": [
                c.to_orchestration_info()
                for c in self.list_by_category(EngineCategory.ORCHESTRATION)
            ],
            "business_intelligence": [
                c.to_orchestration_info()
                for c in self.list_by_category(EngineCategory.BUSINESS_INTELLIGENCE)
            ],
            "creative": [
                c.to_orchestration_info()
                for c in self.list_by_category(EngineCategory.CREATIVE)
            ],
            "governance": [
                c.to_orchestration_info()
                for c in self.list_by_category(EngineCategory.GOVERNANCE)
            ]
        }

    def get_killer_engines(self) -> List[EngineContract]:
        """List high-value 'killer' engines."""
        return self.find_by_tag("killer_vertical") + self.find_by_tag("monster_engine")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        active_engines = [c for c in self._contracts.values() if c.is_active]
        return {
            "total_engines": len(self._contracts),
            "active_engines": len(active_engines),
            "categories": len(self._category_index),
            "capabilities": len(self._capability_index),
            "killer_engines": len(self.get_killer_engines()),
            "by_category": {
                k: len(v) for k, v in self._category_index.items()
            }
        }


def get_registry() -> EngineRegistry:
    """Get singleton registry instance."""
    return EngineRegistry()

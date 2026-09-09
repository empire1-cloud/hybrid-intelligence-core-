"""
Engine Contract Model

Standardized interface/metadata for every engine in HIC.
Allows dynamic discovery, orchestration, and governance.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class EngineCategory(str, Enum):
    """Engine classification categories."""
    ORCHESTRATION = "orchestration"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CREATIVE = "creative"
    GOVERNANCE = "governance"
    SYSTEM = "system"


class ProviderConfig(BaseModel):
    """Provider and model information."""
    name: str = Field(..., description="Provider name (anthropic, openai, google)")
    model: str = Field(..., description="Primary model ID")
    alternative_models: List[str] = Field(default_factory=list, description="Fallback models")


class PerformanceMetrics(BaseModel):
    """Performance characteristics."""
    latency_p50_ms: int = Field(..., description="50th percentile latency")
    latency_p95_ms: int = Field(..., description="95th percentile latency")
    latency_p99_ms: int = Field(..., description="99th percentile latency")
    cost_per_execution_usd: float = Field(..., description="Average cost per execution")
    throughput_rps: Optional[float] = Field(None, description="Requests per second")


class QualityMetrics(BaseModel):
    """Quality and reliability metrics."""
    confidence: float = Field(..., ge=0, le=1, description="Output confidence (0-1)")
    reliability: float = Field(..., ge=0, le=1, description="Execution success rate")
    canon_compliance_rate: float = Field(..., ge=0, le=1, description="Canon rule compliance")
    average_output_quality: Optional[float] = Field(None, ge=0, le=1)


class CanonicalRules(BaseModel):
    """Output canonicalization rules."""
    required_fields: List[str] = Field(default_factory=list)
    forbidden_phrases: List[str] = Field(default_factory=list)
    output_format: str = Field(default="json", description="json, text, structured")
    min_summary_length: Optional[int] = None
    max_summary_length: Optional[int] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    custom_rules: Optional[Dict[str, Any]] = None


class EvidenceState(BaseModel):
    """Tracked evidence and observability data."""
    executions_tracked: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    average_output_quality: float = Field(default=0.0)
    error_rate: float = Field(default=0.0)
    cost_total_usd: float = Field(default=0.0)
    last_execution_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    provider_performance: Optional[Dict[str, float]] = None
    model_performance: Optional[Dict[str, float]] = None


class InputSchema(BaseModel):
    """Input schema definition."""
    type: str = Field(default="object")
    required: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class OutputSchema(BaseModel):
    """Output schema definition."""
    type: str = Field(default="object")
    required: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class EngineContract(BaseModel):
    """
    Standardized contract for every engine in Hybrid Intelligence Core.

    This contract allows HIC to:
    - Dynamically discover and list engines
    - Route requests intelligently
    - Compose multi-engine pipelines
    - Monitor for drift and quality issues
    - Track cost and performance
    - Prove engine differentiation
    - Build evidence over time
    """

    # Identity
    engine_id: str = Field(..., description="Unique engine identifier (lowercase, snake_case)")
    engine_name: str = Field(..., description="Human-readable engine name")
    version: str = Field(default="1.0.0", description="Semantic version")
    category: EngineCategory = Field(..., description="Strategic category")

    # Description
    description: str = Field(..., description="What this engine does")
    capabilities: List[str] = Field(default_factory=list, description="Key capabilities")

    # I/O
    input_schema: InputSchema = Field(..., description="Input specification")
    output_schema: OutputSchema = Field(..., description="Output specification")

    # Implementation
    provider: ProviderConfig = Field(..., description="Provider and model info")

    # Performance & Cost
    performance: PerformanceMetrics = Field(..., description="Latency and cost metrics")

    # Quality
    quality: QualityMetrics = Field(..., description="Quality and reliability metrics")

    # Governance
    canonical: CanonicalRules = Field(default_factory=CanonicalRules, description="Canon rules")

    # Evidence & Observability
    evidence_state: EvidenceState = Field(default_factory=EvidenceState, description="Tracked metrics")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

    # Status
    is_active: bool = Field(default=True, description="Engine operational status")
    deprecation_notice: Optional[str] = Field(None, description="Deprecation message if applicable")

    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "engine_id": "strategy",
                "engine_name": "Strategy Engine",
                "version": "1.0.0",
                "category": "business_intelligence",
                "description": "Generates actionable strategies for any goal",
                "capabilities": ["strategic planning", "risk analysis", "goal decomposition"],
                "input_schema": {
                    "type": "object",
                    "required": ["goal"],
                    "properties": {
                        "goal": {"type": "string", "description": "Strategic objective"}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "required": ["summary", "steps", "risks", "resources", "next_action"],
                    "properties": {
                        "summary": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "string"}},
                        "risks": {"type": "array", "items": {"type": "string"}},
                        "resources": {"type": "array", "items": {"type": "string"}},
                        "next_action": {"type": "string"}
                    }
                },
                "provider": {
                    "name": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "alternative_models": ["gpt-5.2", "gpt-4o"]
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
                }
            }
        }

    def to_discovery_response(self) -> Dict[str, Any]:
        """Format contract for discovery API."""
        return {
            "engine_id": self.engine_id,
            "engine_name": self.engine_name,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "capabilities": self.capabilities,
            "provider": self.provider.model_dump(),
            "performance": self.performance.model_dump(),
            "quality": self.quality.model_dump(),
            "is_active": self.is_active
        }

    def to_orchestration_info(self) -> Dict[str, Any]:
        """Format contract for pipeline orchestration."""
        return {
            "engine_id": self.engine_id,
            "engine_name": self.engine_name,
            "category": self.category,
            "input_keys": list(self.input_schema.properties.keys()),
            "output_keys": list(self.output_schema.properties.keys()),
            "required_inputs": self.input_schema.required,
            "required_outputs": self.output_schema.required,
            "provider": self.provider.model,
            "cost_per_execution": self.performance.cost_per_execution_usd
        }

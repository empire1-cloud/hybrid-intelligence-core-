"""
Startup Copilot Data Models

Pydantic models for all 12 founder skills.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 1. IDEA VALIDATION ENGINE
# ============================================================================

class FounderBackground(BaseModel):
    """Founder's relevant experience."""
    years_experience: int = Field(..., description="Years in adjacent domain")
    domain: str = Field(..., description="Industry/domain expertise")
    previous_exits: int = Field(default=0, description="Number of exits")
    industry_relationships: List[str] = Field(default=[], description="Key relationships held")


class IdeaValidationInput(BaseModel):
    """Input for idea validation."""
    founder_background: FounderBackground
    market_problem: str = Field(..., description="Problem statement")
    existing_solutions: List[str] = Field(default=[], description="Competing solutions")
    interviews_conducted: int = Field(default=0, description="# of customer interviews")
    search_volume: Optional[str] = Field(default=None, description="Google search volume")


class ValidationFinding(BaseModel):
    """Single validation criterion."""
    criterion: str
    status: str  # pass | fail | warning
    evidence: str
    weight: float


class IdeaValidationOutput(BaseModel):
    """Validation decision and reasoning."""
    verdict: str  # go | pivot | kill
    confidence: float  # 0-1.0
    findings: List[ValidationFinding]
    summary: str
    next_steps: List[str]
    founder_market_fit_score: float  # 0-10


# ============================================================================
# 2. BUSINESS MODEL ENGINE
# ============================================================================

class UnitEconomics(BaseModel):
    """Core unit economics."""
    revenue_per_customer: float = Field(..., description="ARPU or ACV")
    gross_margin_percent: float = Field(..., description="Gross margin %")
    customer_acquisition_cost: float = Field(..., description="CAC")
    lifetime_value: float = Field(..., description="LTV")
    ltv_cac_ratio: float = Field(..., description="LTV/CAC ratio")
    payback_period_months: float = Field(..., description="Months to payback")


class RevenueStream(BaseModel):
    """Single revenue stream."""
    name: str
    model_type: str  # subscription | transactional | licensing | freemium
    take_rate_percent: Optional[float] = Field(default=None, description="Take rate %")
    monthly_recurring_revenue: Optional[float] = Field(default=None, description="MRR estimate")


class BusinessModelInput(BaseModel):
    """Input for business model design."""
    product_description: str
    target_market: str
    market_size_tam: Optional[float] = Field(default=None, description="TAM in $")
    existing_business_models: List[str] = Field(default=[], description="Competitive models")
    founder_preferences: Optional[str] = Field(default=None)


class BusinessModelOutput(BaseModel):
    """Business model canvas and unit economics."""
    model_pattern: str  # Which of 55 patterns
    revenue_streams: List[RevenueStream]
    unit_economics: UnitEconomics
    target_segments: List[str]
    pricing_tiers: List[Dict[str, Any]]
    expansion_opportunities: List[str]
    risks: List[str]


# ============================================================================
# 3. FUNDRAISING ENGINE
# ============================================================================

class PitchDeckSlide(BaseModel):
    """Single pitch deck slide."""
    slide_number: int
    title: str
    content: str
    key_visuals: List[str]


class VCProfile(BaseModel):
    """VC firm profile for targeting."""
    name: str
    focus_areas: List[str]
    check_size_min: float
    check_size_max: float
    contact_email: Optional[str] = Field(
        default=None,
        description=(
            "No verified VC contact database is wired into this engine. "
            "Must be null unless the model is highly confident the address "
            "is current and public — never a guessed or invented address."
        ),
    )


class FundraisingInput(BaseModel):
    """Input for fundraising strategy."""
    current_stage: str  # pre_seed | seed | series_a | series_b
    target_raise: float  # In $
    use_of_funds: str
    runway_months: float
    traction: Optional[str] = Field(default=None, description="Current traction")


class FundraisingOutput(BaseModel):
    """Pitch deck, investor targets, strategy."""
    pitch_deck: List[PitchDeckSlide]
    investor_targets: List[VCProfile]
    investor_count: int  # Recommended # to target
    vc_outreach_sequence: List[str]  # Email sequence steps
    estimated_timeline_weeks: int
    key_narrative_hooks: List[str]
    disclaimer: str = Field(
        default=(
            "AI-generated starting list — verify every firm and contact "
            "independently before outreach; do not treat emails/contacts as "
            "confirmed."
        ),
        description=(
            "Set unconditionally by FundraisingEngine after parsing the model "
            "response, so it is always present regardless of what the model "
            "returns — see startup_copilot_engines.py."
        ),
    )


# ============================================================================
# 4. GO-TO-MARKET ENGINE
# ============================================================================

class GTMChannel(BaseModel):
    """Single GTM channel."""
    name: str
    channel_type: str  # plg | sales_led | content | paid | partnership
    estimated_cac: float
    estimated_conversion_rate: float
    timeline_to_first_customer_days: int


class GTMInput(BaseModel):
    """Input for GTM strategy."""
    product_type: str
    target_acv: float  # Annual Contract Value
    target_customers: int  # First 100 customers
    founder_background: str
    market_context: Optional[str] = None


class GTMOutput(BaseModel):
    """90-day GTM roadmap."""
    recommended_motion: str  # plg | sales_led | hybrid
    channels: List[GTMChannel]
    phase_1_days: int  # Pre-launch
    phase_2_days: int  # Launch
    phase_3_days: int  # Growth to 100
    waitlist_target: int
    launch_date_recommendation: str
    key_messaging: List[str]


# ============================================================================
# 5. PRODUCT ENGINE
# ============================================================================

class UserStory(BaseModel):
    """INVEST-format user story."""
    role: str
    action: str
    benefit: str
    acceptance_criteria: List[str]


class ProductInput(BaseModel):
    """Input for product strategy."""
    problem_statement: str
    target_user: str
    key_features: List[str]
    success_metrics: List[str]


class ProductOutput(BaseModel):
    """PRD, roadmap, priorities."""
    prd_sections: Dict[str, str]  # problem, solution, metrics, etc.
    user_stories: List[UserStory]
    roadmap_phases: List[Dict[str, Any]]
    rice_scores: Dict[str, float]  # feature_name -> score
    top_3_priorities: List[str]
    non_goals: List[str]


# ============================================================================
# 6. SALES ENGINE
# ============================================================================

class SalesSequenceStep(BaseModel):
    """Single step in sales sequence."""
    step_number: int
    action: str
    template: str
    timing_days: int
    expected_response_rate: float


class SalesInput(BaseModel):
    """Input for sales strategy."""
    deal_complexity: str  # simple | moderate | complex
    acv: float
    buyer_profile: str
    competitive_landscape: Optional[str] = None


class SalesOutput(BaseModel):
    """Sales methodology and sequences."""
    recommended_methodology: str  # BANT | MEDDIC | Challenger
    qualification_criteria: List[str]
    cold_email_sequences: List[SalesSequenceStep]
    target_response_rate: float
    target_conversion_rate: float
    pipeline_target: float


# ============================================================================
# 7. MARKETING & BRAND ENGINE
# ============================================================================

class ContentPillar(BaseModel):
    """Content pillar (topic cluster)."""
    topic: str
    estimated_monthly_volume: int
    difficulty: str  # easy | medium | hard
    pillar_articles: int
    sub_articles: int


class MarketingInput(BaseModel):
    """Input for marketing strategy."""
    brand_positioning: str
    target_audience: str
    competition_level: str  # low | medium | high
    budget: Optional[float] = None


class MarketingOutput(BaseModel):
    """Brand guide, content strategy, SEO plan."""
    brand_voice_attributes: List[str]
    content_pillars: List[ContentPillar]
    target_keywords: List[str]
    monthly_content_plan: List[str]
    pr_angles: List[str]
    social_strategy: Dict[str, str]  # platform -> strategy


# ============================================================================
# 8. GROWTH & ANALYTICS ENGINE
# ============================================================================

class AAARRRMetric(BaseModel):
    """AARRR pirate metric."""
    stage: str  # Acquisition | Activation | Retention | Revenue | Referral
    metric_name: str
    current_value: float
    target_value: float
    unit: str


class GrowthInput(BaseModel):
    """Input for growth strategy."""
    current_product_stage: str
    primary_metric: str
    target_metric_value: float
    time_horizon_months: int
    constraints: Optional[str] = None


class GrowthOutput(BaseModel):
    """AARRR metrics, North Star, experiments."""
    north_star_metric: str
    aarrr_metrics: List[AAARRRMetric]
    retention_curve_target: Dict[str, float]  # day -> retention %
    recommended_experiments: List[str]
    growth_initiatives: List[Dict[str, Any]]


# ============================================================================
# 9. OPERATIONS ENGINE
# ============================================================================

class HiringRole(BaseModel):
    """Role to hire for."""
    title: str
    seniority: str
    expected_salary: float
    timeline_weeks: int
    key_competencies: List[str]


class OKR(BaseModel):
    """Single OKR (Objective + Key Results)."""
    objective: str
    key_results: List[str]
    owner: str
    quarter: str


class OperationsInput(BaseModel):
    """Input for operations planning."""
    current_headcount: int
    target_headcount: int
    timeline_months: int
    budget: float


class OperationsOutput(BaseModel):
    """Hiring plan, OKRs, board structure."""
    hiring_plan: List[HiringRole]
    interview_scorecard: Dict[str, float]  # competency -> weight
    okrs: List[OKR]
    board_composition_recommendation: str


# ============================================================================
# 10. FINANCE & ACCOUNTING ENGINE
# ============================================================================

class CashFlowMonth(BaseModel):
    """Monthly cash flow projection."""
    month: int
    revenue: float
    expenses: float
    net_cash_flow: float
    cumulative_cash: float


class FinanceInput(BaseModel):
    """Input for financial modeling."""
    current_cash: float
    monthly_burn_rate: float
    projected_revenue_monthly: Optional[float] = None
    headcount: int
    months_ahead: int = 12


class FinanceOutput(BaseModel):
    """Cash flow projections, runway analysis."""
    cash_flow_projection: List[CashFlowMonth]
    monthly_burn_rate: float
    projected_runway_months: float
    unit_economics_monthly: UnitEconomics
    cash_reserve_recommendation: float
    next_fundraising_deadline: Optional[str] = None


# ============================================================================
# 11. CUSTOMER SUCCESS ENGINE
# ============================================================================

class OnboardingMilestone(BaseModel):
    """Onboarding milestone."""
    day: int
    objective: str
    key_action: str
    success_metric: str


class HealthScoreInput(BaseModel):
    """Input for health scoring."""
    product_type: str  # plg | sales_led
    customer_segment: str


class HealthScoreOutput(BaseModel):
    """Customer health scoring framework."""
    onboarding_milestones: List[OnboardingMilestone]
    health_score_formula: str
    red_zone_criteria: List[str]
    yellow_zone_criteria: List[str]
    green_zone_criteria: List[str]
    nps_target: int
    churn_prevention_tactics: List[str]


# ============================================================================
# 12. LEGAL & COMPLIANCE ENGINE
# ============================================================================

class CapTableEntry(BaseModel):
    """Cap table row."""
    holder: str
    shares: int
    percentage: float
    strike_price: float
    type: str  # founder | employee | investor


class LegalInput(BaseModel):
    """Input for legal/compliance."""
    entity_type: str  # c_corp | llc | s_corp
    jurisdictions: List[str]
    stage: str  # pre_seed | seed | series_a
    has_employees: bool


class LegalOutput(BaseModel):
    """Entity selection, docs checklist, cap table."""
    recommended_entity: str
    cap_table_template: List[CapTableEntry]
    key_documents_checklist: List[str]
    compliance_checklist: List[str]
    vesting_recommendation: str
    tax_optimization_tips: List[str]

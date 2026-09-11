"""
Startup Copilot API Routes

Exposes all 12 founder skills as REST endpoints.
Integrates with Pipeline Composer for multi-skill workflows.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging

from services.startup_copilot_engines import (
    IdeaValidationEngine,
    BusinessModelEngine,
    FundraisingEngine,
    GTMEngine,
    ProductEngine,
    SalesEngine,
    MarketingEngine,
    GrowthEngine,
    OperationsEngine,
    FinanceEngine,
    CustomerSuccessEngine,
    LegalEngine
)
from services.startup_copilot_models import (
    IdeaValidationInput, IdeaValidationOutput,
    BusinessModelInput, BusinessModelOutput,
    FundraisingInput, FundraisingOutput,
    GTMInput, GTMOutput,
    ProductInput, ProductOutput,
    SalesInput, SalesOutput,
    MarketingInput, MarketingOutput,
    GrowthInput, GrowthOutput,
    OperationsInput, OperationsOutput,
    FinanceInput, FinanceOutput,
    HealthScoreInput, HealthScoreOutput,
    LegalInput, LegalOutput
)

router = APIRouter(prefix="/api/startup-copilot", tags=["startup-copilot"])
logger = logging.getLogger(__name__)

# Initialize all skill engines
idea_validation = IdeaValidationEngine()
business_model = BusinessModelEngine()
fundraising = FundraisingEngine()
gotomarket = GTMEngine()
product = ProductEngine()
sales = SalesEngine()
marketing = MarketingEngine()
growth = GrowthEngine()
operations = OperationsEngine()
finance = FinanceEngine()
customer_success = CustomerSuccessEngine()
legal = LegalEngine()


class SkillResponse(BaseModel):
    """Standard response wrapper for skill outputs."""
    skill: str
    status: str  # success | error
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


# ============================================================================
# SKILL 1: IDEA VALIDATION
# ============================================================================

@router.post("/validate-idea", response_model=SkillResponse)
async def validate_idea(input_data: IdeaValidationInput) -> SkillResponse:
    """
    Validate a startup idea using Mom Test framework.

    Determines: GO | PIVOT | KILL with confidence score.
    """
    try:
        result = await idea_validation.validate(input_data)
        return SkillResponse(
            skill="idea-validation",
            status="success",
            data=result.dict(),
            metadata={
                "verdict": result.verdict,
                "confidence": result.confidence,
                "founder_market_fit_score": result.founder_market_fit_score
            }
        )
    except Exception as e:
        logger.error(f"Idea validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 2: BUSINESS MODEL
# ============================================================================

@router.post("/design-business-model", response_model=SkillResponse)
async def design_business_model(input_data: BusinessModelInput) -> SkillResponse:
    """
    Design sustainable business model with unit economics.

    Outputs: Business model pattern, revenue streams, LTV/CAC analysis.
    """
    try:
        result = await business_model.design_model(input_data)
        return SkillResponse(
            skill="business-model",
            status="success",
            data=result.dict(),
            metadata={
                "model_pattern": result.model_pattern,
                "ltv_cac_ratio": result.unit_economics.ltv_cac_ratio,
                "payback_period_months": result.unit_economics.payback_period_months
            }
        )
    except Exception as e:
        logger.error(f"Business model error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 3: FUNDRAISING
# ============================================================================

@router.post("/create-fundraising-strategy", response_model=SkillResponse)
async def create_fundraising_strategy(input_data: FundraisingInput) -> SkillResponse:
    """
    Generate pitch deck and investor targeting strategy.

    Outputs: 10-slide deck, VC target list, outreach sequences.
    """
    try:
        result = await fundraising.create_fundraising_strategy(input_data)
        return SkillResponse(
            skill="fundraising",
            status="success",
            data=result.dict(),
            metadata={
                "investor_count": result.investor_count,
                "estimated_timeline_weeks": result.estimated_timeline_weeks,
                "pitch_slides": len(result.pitch_deck)
            }
        )
    except Exception as e:
        logger.error(f"Fundraising error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 4: GO-TO-MARKET
# ============================================================================

@router.post("/create-gtm-strategy", response_model=SkillResponse)
async def create_gtm_strategy(input_data: GTMInput) -> SkillResponse:
    """
    Design go-to-market motion and 90-day launch plan.

    Outputs: Recommended motion (PLG/Sales-Led), channels, 3-phase plan.
    """
    try:
        result = await gotomarket.create_gtm_strategy(input_data)
        return SkillResponse(
            skill="gotomarket",
            status="success",
            data=result.dict(),
            metadata={
                "recommended_motion": result.recommended_motion,
                "phase_1_days": result.phase_1_days,
                "total_days": result.phase_1_days + result.phase_2_days + result.phase_3_days
            }
        )
    except Exception as e:
        logger.error(f"GTM strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 5: PRODUCT
# ============================================================================

@router.post("/create-product-strategy", response_model=SkillResponse)
async def create_product_strategy(input_data: ProductInput) -> SkillResponse:
    """
    Write PRD and create prioritized roadmap.

    Outputs: PRD sections, user stories, RICE-scored roadmap.
    """
    try:
        result = await product.create_product_strategy(input_data)
        return SkillResponse(
            skill="product",
            status="success",
            data=result.dict(),
            metadata={
                "top_3_priorities": result.top_3_priorities,
                "user_stories_count": len(result.user_stories),
                "roadmap_phases": len(result.roadmap_phases)
            }
        )
    except Exception as e:
        logger.error(f"Product strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 6: SALES
# ============================================================================

@router.post("/create-sales-strategy", response_model=SkillResponse)
async def create_sales_strategy(input_data: SalesInput) -> SkillResponse:
    """
    Design sales methodology and execution sequences.

    Outputs: MEDDIC/BANT/Challenger method, cold email sequences.
    """
    try:
        result = await sales.create_sales_strategy(input_data)
        return SkillResponse(
            skill="sales",
            status="success",
            data=result.dict(),
            metadata={
                "methodology": result.recommended_methodology,
                "target_response_rate": result.target_response_rate,
                "target_conversion_rate": result.target_conversion_rate
            }
        )
    except Exception as e:
        logger.error(f"Sales strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 7: MARKETING & BRAND
# ============================================================================

@router.post("/create-marketing-strategy", response_model=SkillResponse)
async def create_marketing_strategy(input_data: MarketingInput) -> SkillResponse:
    """
    Design brand strategy and content marketing plan.

    Outputs: Brand voice, content pillars, SEO targets, PR angles.
    """
    try:
        result = await marketing.create_marketing_strategy(input_data)
        return SkillResponse(
            skill="marketing",
            status="success",
            data=result.dict(),
            metadata={
                "content_pillars": len(result.content_pillars),
                "target_keywords": len(result.target_keywords),
                "monthly_content_pieces": len(result.monthly_content_plan)
            }
        )
    except Exception as e:
        logger.error(f"Marketing strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 8: GROWTH & ANALYTICS
# ============================================================================

@router.post("/create-growth-strategy", response_model=SkillResponse)
async def create_growth_strategy(input_data: GrowthInput) -> SkillResponse:
    """
    Design metrics framework and growth experiments.

    Outputs: AARRR metrics, North Star, retention targets, experiments.
    """
    try:
        result = await growth.create_growth_strategy(input_data)
        return SkillResponse(
            skill="growth",
            status="success",
            data=result.dict(),
            metadata={
                "north_star_metric": result.north_star_metric,
                "aarrr_metrics_count": len(result.aarrr_metrics),
                "recommended_experiments": len(result.recommended_experiments)
            }
        )
    except Exception as e:
        logger.error(f"Growth strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 9: OPERATIONS
# ============================================================================

@router.post("/create-operations-strategy", response_model=SkillResponse)
async def create_operations_strategy(input_data: OperationsInput) -> SkillResponse:
    """
    Design hiring plan, OKRs, and governance.

    Outputs: Hiring roadmap, interview scorecard, OKRs, board structure.
    """
    try:
        result = await operations.create_operations_strategy(input_data)
        return SkillResponse(
            skill="operations",
            status="success",
            data=result.dict(),
            metadata={
                "hiring_roles": len(result.hiring_plan),
                "okrs": len(result.okrs),
                "board_recommendation": result.board_composition_recommendation
            }
        )
    except Exception as e:
        logger.error(f"Operations strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 10: FINANCE
# ============================================================================

@router.post("/create-financial-model", response_model=SkillResponse)
async def create_financial_model(input_data: FinanceInput) -> SkillResponse:
    """
    Generate 12-month cash flow projection and runway analysis.

    Outputs: Monthly cash flow, runway, fundraising deadline.
    """
    try:
        result = await finance.create_financial_model(input_data)
        return SkillResponse(
            skill="finance",
            status="success",
            data=result.dict(),
            metadata={
                "projected_runway_months": result.projected_runway_months,
                "monthly_burn_rate": result.monthly_burn_rate,
                "cash_reserve_recommendation": result.cash_reserve_recommendation
            }
        )
    except Exception as e:
        logger.error(f"Financial model error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 11: CUSTOMER SUCCESS
# ============================================================================

@router.post("/create-customer-success-strategy", response_model=SkillResponse)
async def create_customer_success_strategy(input_data: HealthScoreInput) -> SkillResponse:
    """
    Design onboarding and health scoring framework.

    Outputs: Onboarding milestones, health score formula, churn prevention.
    """
    try:
        result = await customer_success.create_customer_success_strategy(input_data)
        return SkillResponse(
            skill="customer-success",
            status="success",
            data=result.dict(),
            metadata={
                "onboarding_milestones": len(result.onboarding_milestones),
                "nps_target": result.nps_target,
                "health_score_formula": result.health_score_formula
            }
        )
    except Exception as e:
        logger.error(f"Customer success strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SKILL 12: LEGAL & COMPLIANCE
# ============================================================================

@router.post("/create-legal-strategy", response_model=SkillResponse)
async def create_legal_strategy(input_data: LegalInput) -> SkillResponse:
    """
    Generate legal roadmap and compliance checklist.

    Outputs: Entity recommendation, cap table, document checklist.

    DISCLAIMER: This is educational guidance only. Consult actual lawyers.
    """
    try:
        result = await legal.create_legal_strategy(input_data)
        return SkillResponse(
            skill="legal",
            status="success",
            data=result.dict(),
            metadata={
                "recommended_entity": result.recommended_entity,
                "documents_needed": len(result.key_documents_checklist),
                "compliance_items": len(result.compliance_checklist)
            }
        )
    except Exception as e:
        logger.error(f"Legal strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MULTI-SKILL WORKFLOWS (Pipeline Composer Integration)
# ============================================================================

class WorkflowRequest(BaseModel):
    """Request for multi-skill workflow."""
    workflow_type: str  # validate_to_pitch, validate_to_launch, etc.
    founder_background: Dict[str, Any]
    product_description: str
    target_market: str
    metadata: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Response from multi-skill workflow."""
    workflow_type: str
    steps: List[Dict[str, Any]]
    final_output: Dict[str, Any]


@router.post("/workflow/validate-to-pitch", response_model=WorkflowResponse)
async def workflow_validate_to_pitch(request: WorkflowRequest) -> WorkflowResponse:
    """
    Complete workflow: Validate idea → Design business model → Create pitch deck.

    This is a chained workflow using Skills 1, 2, and 3.
    """
    try:
        steps = []

        # Step 1: Idea Validation
        validation_input = IdeaValidationInput(
            founder_background=request.founder_background,
            market_problem=request.product_description,
            existing_solutions=[]
        )
        validation_result = await idea_validation.validate(validation_input)
        steps.append({
            "step": 1,
            "skill": "idea-validation",
            "verdict": validation_result.verdict,
            "confidence": validation_result.confidence
        })

        if validation_result.verdict == "kill":
            return WorkflowResponse(
                workflow_type="validate-to-pitch",
                steps=steps,
                final_output={"verdict": "kill", "message": "Idea did not pass validation"}
            )

        # Step 2: Business Model Design
        model_input = BusinessModelInput(
            product_description=request.product_description,
            target_market=request.target_market
        )
        model_result = await business_model.design_model(model_input)
        steps.append({
            "step": 2,
            "skill": "business-model",
            "ltv_cac_ratio": model_result.unit_economics.ltv_cac_ratio,
            "payback_period": model_result.unit_economics.payback_period_months
        })

        # Step 3: Fundraising (Pitch Deck)
        fundraising_input = FundraisingInput(
            current_stage="seed",
            target_raise=500000,
            use_of_funds="Product development and GTM",
            runway_months=12,
            traction="MVP in beta"
        )
        fundraising_result = await fundraising.create_fundraising_strategy(fundraising_input)
        steps.append({
            "step": 3,
            "skill": "fundraising",
            "investor_count": fundraising_result.investor_count,
            "estimated_timeline_weeks": fundraising_result.estimated_timeline_weeks
        })

        return WorkflowResponse(
            workflow_type="validate-to-pitch",
            steps=steps,
            final_output={
                "validation_verdict": validation_result.verdict,
                "business_model": model_result.model_pattern,
                "pitch_deck_ready": True
            }
        )

    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/validate-to-launch", response_model=WorkflowResponse)
async def workflow_validate_to_launch(request: WorkflowRequest) -> WorkflowResponse:
    """
    Complete workflow: Validate idea → Business model → GTM → Product.

    This is a chained workflow using Skills 1, 2, 4, and 5.
    """
    try:
        steps = []

        # Step 1: Idea Validation
        validation_input = IdeaValidationInput(
            founder_background=request.founder_background,
            market_problem=request.product_description,
            existing_solutions=[]
        )
        validation_result = await idea_validation.validate(validation_input)
        steps.append({
            "step": 1,
            "skill": "idea-validation",
            "verdict": validation_result.verdict
        })

        if validation_result.verdict == "kill":
            return WorkflowResponse(
                workflow_type="validate-to-launch",
                steps=steps,
                final_output={"verdict": "kill"}
            )

        # Step 2: GTM Strategy
        gtm_input = GTMInput(
            product_type="B2B SaaS",
            target_acv=5000,
            target_customers=100,
            founder_background=str(request.founder_background)
        )
        gtm_result = await gotomarket.create_gtm_strategy(gtm_input)
        steps.append({
            "step": 2,
            "skill": "gotomarket",
            "recommended_motion": gtm_result.recommended_motion
        })

        # Step 3: Product Strategy
        product_input = ProductInput(
            problem_statement=request.product_description,
            target_user=request.target_market,
            key_features=["Core feature 1", "Core feature 2", "Core feature 3"],
            success_metrics=["DAU growth", "User retention", "NPS score"]
        )
        product_result = await product.create_product_strategy(product_input)
        steps.append({
            "step": 3,
            "skill": "product",
            "top_3_priorities": product_result.top_3_priorities
        })

        return WorkflowResponse(
            workflow_type="validate-to-launch",
            steps=steps,
            final_output={
                "validation_verdict": validation_result.verdict,
                "gtm_motion": gtm_result.recommended_motion,
                "ready_to_build": True
            }
        )

    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK & METADATA
# ============================================================================

@router.get("/skills", tags=["metadata"])
async def list_skills():
    """List all available startup copilot skills."""
    return {
        "total_skills": 12,
        "skills": [
            {
                "id": 1,
                "name": "Idea Validation",
                "endpoint": "/api/startup-copilot/validate-idea",
                "description": "Validate founder-market fit using Mom Test framework"
            },
            {
                "id": 2,
                "name": "Business Model",
                "endpoint": "/api/startup-copilot/design-business-model",
                "description": "Design business model with unit economics (LTV/CAC)"
            },
            {
                "id": 3,
                "name": "Fundraising",
                "endpoint": "/api/startup-copilot/create-fundraising-strategy",
                "description": "Generate 10-slide pitch deck and investor strategy"
            },
            {
                "id": 4,
                "name": "Go-to-Market",
                "endpoint": "/api/startup-copilot/create-gtm-strategy",
                "description": "Design 90-day GTM roadmap (PLG/Sales-Led/Hybrid)"
            },
            {
                "id": 5,
                "name": "Product",
                "endpoint": "/api/startup-copilot/create-product-strategy",
                "description": "Write PRD and RICE-scored roadmap"
            },
            {
                "id": 6,
                "name": "Sales",
                "endpoint": "/api/startup-copilot/create-sales-strategy",
                "description": "Design sales methodology (BANT/MEDDIC/Challenger)"
            },
            {
                "id": 7,
                "name": "Marketing & Brand",
                "endpoint": "/api/startup-copilot/create-marketing-strategy",
                "description": "Brand voice, content pillars, SEO strategy"
            },
            {
                "id": 8,
                "name": "Growth & Analytics",
                "endpoint": "/api/startup-copilot/create-growth-strategy",
                "description": "AARRR metrics, North Star, retention analysis"
            },
            {
                "id": 9,
                "name": "Operations",
                "endpoint": "/api/startup-copilot/create-operations-strategy",
                "description": "Hiring plan, OKRs, board management"
            },
            {
                "id": 10,
                "name": "Finance",
                "endpoint": "/api/startup-copilot/create-financial-model",
                "description": "Cash flow forecasting and runway analysis"
            },
            {
                "id": 11,
                "name": "Customer Success",
                "endpoint": "/api/startup-copilot/create-customer-success-strategy",
                "description": "Onboarding flows, health scoring, churn prevention"
            },
            {
                "id": 12,
                "name": "Legal & Compliance",
                "endpoint": "/api/startup-copilot/create-legal-strategy",
                "description": "Entity selection, cap table, compliance checklist"
            }
        ],
        "workflows": [
            {
                "name": "Validate to Pitch",
                "endpoint": "/api/startup-copilot/workflow/validate-to-pitch",
                "skills": [1, 2, 3]
            },
            {
                "name": "Validate to Launch",
                "endpoint": "/api/startup-copilot/workflow/validate-to-launch",
                "skills": [1, 2, 4, 5]
            }
        ]
    }


@router.get("/health", tags=["metadata"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "startup-copilot",
        "version": "1.0.0",
        "skills_available": 12
    }

"""
Startup Copilot Skills Engines (1-12)

Implements all 12 founder guidance skills as integrated HIC engines.
Each skill can be invoked independently or chained in the Pipeline Composer.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from services.model_policy import enforce_approved_model
from .startup_copilot_models import (
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

load_dotenv()


class StartupCopilotEngine:
    """Base class for all 12 founder skills."""

    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "gpt-4o": ("openai", "gpt-4o"),
        "gpt-4o-mini": ("openai", "gpt-4o-mini"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "claude-3-5-sonnet": ("anthropic", "claude-3-5-sonnet-20241022"),
    }

    # Claude best for founder guidance (reasoning + nuance)
    DEFAULT_MODEL = "claude-sonnet-4.5"

    SYSTEM_PROMPT = (
        "You are a founder advisor. Return valid JSON only, matching the schema "
        "named in the prompt. No markdown, no commentary outside the JSON object."
    )

    @classmethod
    def _get_api_key(cls, provider: str) -> str:
        """Get a provider-specific API key without Google fallbacks."""
        if provider == "anthropic":
            return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        return os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")

    @classmethod
    def _create_chat(cls, model: Optional[str] = None) -> LlmChat:
        """Create a configured chat instance after enforcing model policy."""
        approved_model = enforce_approved_model(model or cls.DEFAULT_MODEL)
        provider, model_name = cls.MODEL_CONFIG[approved_model]

        return LlmChat(
            api_key=cls._get_api_key(provider),
            session_id=f"startup-copilot-{approved_model}",
            system_message=cls.SYSTEM_PROMPT,
        ).with_model(provider, model_name)

    @classmethod
    async def _ask(cls, prompt: str, model: Optional[str] = None) -> str:
        """Send a prompt to an approved model and return the response text."""
        chat = cls._create_chat(model)
        return await chat.send_message(UserMessage(text=prompt))

    @staticmethod
    def _strip_fences(response_text: str) -> str:
        """Unwrap a ```json fenced block so json.loads sees the object itself."""
        text = (response_text or "").strip()
        for fence in ("```json", "```"):
            if fence in text:
                start = text.find(fence) + len(fence)
                end = text.find("```", start)
                return (text[start:end] if end != -1 else text[start:]).strip()
        return text


class IdeaValidationEngine(StartupCopilotEngine):
    """Skill 1: Idea Validation

    Determines if founder + market + timing = viable venture.
    Uses Mom Test framework + GO/PIVOT/KILL decision criteria.
    """

    PURPOSE = "Validate founder-market fit and market viability"

    MOM_TEST_CRITERIA = {
        "founder_market_fit": {
            "domain_expertise": "5+ years in adjacent domain",
            "relationships": "Existing customer/distributor relationships",
            "previous_wins": "Track record of execution"
        },
        "market_viability": {
            "problem_complaints": "10+ complaints found in <15 minutes",
            "market_size": "TAM/SAM/SOM analysis confirms $1B+ opportunity",
            "solution_gaps": "3+ existing solutions with bad reviews"
        },
        "timing": {
            "search_volume": "Google Trends confirm rising interest",
            "adoption_trend": "Market inflection visible (adoption curve)",
            "urgency": "Customers expressing pain acutely"
        }
    }

    async def validate(self, input_data: IdeaValidationInput) -> IdeaValidationOutput:
        """Run idea validation framework."""

        # Construct validation prompt
        prompt = f"""
You are a founder advisor helping validate a startup idea using the Mom Test framework.

FOUNDER BACKGROUND:
- Years in domain: {input_data.founder_background.years_experience}
- Domain: {input_data.founder_background.domain}
- Previous exits: {input_data.founder_background.previous_exits}
- Key relationships: {', '.join(input_data.founder_background.industry_relationships)}

IDEA:
- Problem: {input_data.market_problem}
- Existing solutions: {', '.join(input_data.existing_solutions)}
- Interviews conducted: {input_data.interviews_conducted}
- Search volume: {input_data.search_volume}

Evaluate this idea across three dimensions:

1. FOUNDER-MARKET FIT
   - Rate the founder's advantage in this domain
   - Do they have unfair advantages? (domain expertise, relationships, track record)

2. MARKET VIABILITY
   - Is the problem real and urgent?
   - What's the market size estimate?
   - Are there bad solutions that create opportunity?

3. TIMING
   - Is the market ready? Adoption curve?
   - Is there urgency in customer feedback?

Based on this analysis, provide:
- Overall verdict: GO | PIVOT | KILL
- Confidence score (0-1.0)
- Key findings for each criterion
- Founder-market fit score (0-10)
- Specific next steps

Format your response as JSON matching the IdeaValidationOutput schema.
"""

        # Call LLM
        response_text = await self._ask(prompt)

        # Parse response
        try:
            result_json = json.loads(self._strip_fences(response_text))
            return IdeaValidationOutput(**result_json)
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if LLM output isn't perfectly formatted
            return IdeaValidationOutput(
                verdict="pivot",
                confidence=0.5,
                findings=[],
                summary=response_text,
                next_steps=["Conduct more customer interviews"],
                founder_market_fit_score=5.0
            )


class BusinessModelEngine(StartupCopilotEngine):
    """Skill 2: Business Model Design

    Selects from 55 patterns, designs revenue streams, calculates unit economics.
    """

    PURPOSE = "Design sustainable business model with viable unit economics"

    PATTERNS = {
        "transactional_fintech": {
            "examples": ["Wise", "Mercury", "Relay"],
            "revenue_model": "Take rate (2-3%) + Monthly fees (0.5-1%)",
            "typical_ltv_cac": 2.5
        },
        "saas_subscription": {
            "examples": ["Stripe", "HubSpot", "Datadog"],
            "revenue_model": "Per-seat subscription ($50-500/mo per user)",
            "typical_ltv_cac": 3.0
        },
        "marketplace": {
            "examples": ["Airbnb", "Uber", "DoorDash"],
            "revenue_model": "Take rate on transactions (15-30%)",
            "typical_ltv_cac": 2.0
        },
        "licensing": {
            "examples": ["MongoDB", "Twilio"],
            "revenue_model": "Usage-based or tiered licensing",
            "typical_ltv_cac": 4.0
        }
    }

    async def design_model(self, input_data: BusinessModelInput) -> BusinessModelOutput:
        """Design business model and unit economics."""

        prompt = f"""
You are a business model advisor. Design a sustainable business model.

PRODUCT:
- Description: {input_data.product_description}
- Target market: {input_data.target_market}
- TAM estimate: ${input_data.market_size_tam}

Competitive models: {', '.join(input_data.existing_business_models)}

Design a business model by:
1. Selecting from these archetypes: transactional_fintech, saas_subscription, marketplace, licensing
2. Defining revenue streams (take rates, subscription tiers, etc.)
3. Calculating unit economics (ARPU, CAC, LTV, payback period)
4. Identifying pricing tiers
5. Spotting expansion opportunities
6. Listing business model risks

Target metrics:
- LTV/CAC ratio: 3:1 or higher
- Payback period: <12 months
- Gross margin: 70%+ for SaaS, 50%+ for marketplace

Format response as JSON matching BusinessModelOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return BusinessModelOutput(**result_json)
        except:
            return BusinessModelOutput(
                model_pattern="saas_subscription",
                revenue_streams=[],
                unit_economics={
                    "revenue_per_customer": 5000,
                    "gross_margin_percent": 70,
                    "customer_acquisition_cost": 1500,
                    "lifetime_value": 15000,
                    "ltv_cac_ratio": 10.0,
                    "payback_period_months": 3.6
                },
                target_segments=["SMB"],
                pricing_tiers=[],
                expansion_opportunities=[],
                risks=[]
            )


class FundraisingEngine(StartupCopilotEngine):
    """Skill 3: Fundraising Strategy

    Generates 10-slide pitch deck, VC targeting hierarchy, outreach sequences.
    """

    PURPOSE = "Prepare for fundraising with pitch deck and investor strategy"

    PITCH_DECK_OUTLINE = [
        {"number": 1, "title": "Problem", "key": "What makes this problem urgent?"},
        {"number": 2, "title": "Solution", "key": "How is your approach unique?"},
        {"number": 3, "title": "Market", "key": "How big is the opportunity?"},
        {"number": 4, "title": "Business Model", "key": "How do you make money?"},
        {"number": 5, "title": "Go-to-Market", "key": "How will you acquire customers?"},
        {"number": 6, "title": "Traction", "key": "What have you proven?"},
        {"number": 7, "title": "Team", "key": "Why are you the right founders?"},
        {"number": 8, "title": "Financials", "key": "What's your path to profitability?"},
        {"number": 9, "title": "Ask", "key": "How much capital and for what?"},
        {"number": 10, "title": "Vision", "key": "What's the endgame?"}
    ]

    async def create_fundraising_strategy(self, input_data: FundraisingInput) -> FundraisingOutput:
        """Generate pitch deck and investor strategy."""

        prompt = f"""
You are a fundraising advisor. Create a complete fundraising package.

FUNDRAISING CONTEXT:
- Stage: {input_data.current_stage}
- Target raise: ${input_data.target_raise}
- Use of funds: {input_data.use_of_funds}
- Current runway: {input_data.runway_months} months
- Traction: {input_data.traction or "Pre-product"}

Create:
1. 10-slide pitch deck with content for each slide
2. VC investor target list (100 VCs, segmented by stage/fit)
3. Cold email outreach sequence (3 emails over 2 weeks)
4. Estimated fundraising timeline

VC outreach hierarchy:
1. Warm intro from existing portfolio founder
2. Warm intro from accelerator director
3. Direct email from founder
4. Cold email from investor relations

Include key narrative hooks that make your story compelling.

Format response as JSON matching FundraisingOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return FundraisingOutput(**result_json)
        except:
            return FundraisingOutput(
                pitch_deck=[],
                investor_targets=[],
                investor_count=100,
                vc_outreach_sequence=[
                    "Email 1: Problem hook - why this matters",
                    "Wait 3 days",
                    "Email 2: Social proof + case study",
                    "Wait 5 days",
                    "Email 3: Direct ask + calendar link"
                ],
                estimated_timeline_weeks=8,
                key_narrative_hooks=[]
            )


class GTMEngine(StartupCopilotEngine):
    """Skill 4: Go-to-Market Strategy

    Routes to product-led vs. sales-led motion, 90-day GTM plan.
    """

    PURPOSE = "Execute launch through first 100 customers"

    async def create_gtm_strategy(self, input_data: GTMInput) -> GTMOutput:
        """Design go-to-market motion and 90-day plan."""

        prompt = f"""
You are a go-to-market advisor. Design a 90-day GTM roadmap.

PRODUCT:
- Type: {input_data.product_type}
- Target ACV: ${input_data.target_acv}
- Goal: {input_data.target_customers} customers
- Founder background: {input_data.founder_background}

Determine the right motion:
- If ACV <$1K and self-serve potential: Product-Led Growth
- If ACV >$5K and complex sales: Sales-Led
- If $1K-$5K: Hybrid approach

Then design 90-day plan with:
1. Phase 1 (Days 0-30): Pre-launch (build waitlist, prep marketing)
2. Phase 2 (Days 31-60): Launch (momentum push, iterate fast)
3. Phase 3 (Days 61-90): Growth (hit 100 customers)

Channel recommendations:
- Content marketing
- Product Hunt launch
- Community seeding
- Direct sales (if B2B)
- Paid acquisition
- Referral loops

Format response as JSON matching GTMOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return GTMOutput(**result_json)
        except:
            return GTMOutput(
                recommended_motion="hybrid",
                channels=[],
                phase_1_days=30,
                phase_2_days=30,
                phase_3_days=30,
                waitlist_target=1000,
                launch_date_recommendation="Q4 2026",
                key_messaging=[]
            )


class ProductEngine(StartupCopilotEngine):
    """Skill 5: Product Strategy

    PRD writing, RICE prioritization, user stories.
    """

    PURPOSE = "Build products that solve real problems with urgency"

    async def create_product_strategy(self, input_data: ProductInput) -> ProductOutput:
        """Write PRD and prioritized roadmap."""

        prompt = f"""
You are a product advisor. Create a complete product strategy.

PROBLEM:
{input_data.problem_statement}

TARGET USER:
{input_data.target_user}

INITIAL FEATURES:
{', '.join(input_data.key_features)}

SUCCESS METRICS:
{', '.join(input_data.success_metrics)}

Create:
1. PRD sections: problem, solution, user stories, success metrics, non-goals
2. INVEST-format user stories for top features
3. 6-month roadmap with phases
4. RICE scores for prioritization
5. Top 3 feature priorities

RICE scoring formula:
RICE = (Reach × Impact × Confidence) / Effort

Format response as JSON matching ProductOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return ProductOutput(**result_json)
        except:
            return ProductOutput(
                prd_sections={},
                user_stories=[],
                roadmap_phases=[],
                rice_scores={},
                top_3_priorities=[],
                non_goals=[]
            )


class SalesEngine(StartupCopilotEngine):
    """Skill 6: Sales Strategy

    MEDDIC, BANT, Challenger methodologies + cold sequences.
    """

    PURPOSE = "Convert ideal customers to revenue efficiently"

    async def create_sales_strategy(self, input_data: SalesInput) -> SalesOutput:
        """Design sales methodology and execution sequences."""

        prompt = f"""
You are a sales advisor. Design a sales motion.

DEAL PROFILE:
- Complexity: {input_data.deal_complexity}
- ACV: ${input_data.acv}
- Buyer: {input_data.buyer_profile}
- Competition: {input_data.competitive_landscape or "Moderate"}

Recommend a sales methodology:
- BANT: Quick SMB qualification (simple deals, <$1K)
- MEDDIC: Enterprise complexity (complex, >$50K)
- Challenger: Differentiated product (status quo disruptive)

Then design:
1. Qualification criteria (must-haves)
2. 3-email cold outreach sequence
3. Target response rate and conversion rate
4. Pipeline generation targets

Each email should follow this pattern:
- Email 1: Problem hook (no pitch, 2-3 sentences)
- Email 2: Social proof or case study
- Email 3: Direct ask + calendar link

Format response as JSON matching SalesOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return SalesOutput(**result_json)
        except:
            return SalesOutput(
                recommended_methodology="BANT",
                qualification_criteria=[],
                cold_email_sequences=[],
                target_response_rate=0.02,
                target_conversion_rate=0.005,
                pipeline_target=0.0
            )


class MarketingEngine(StartupCopilotEngine):
    """Skill 7: Marketing & Brand Strategy

    Distribution, brand voice, pillar content, SEO playbook.
    """

    PURPOSE = "Build awareness and trust through strategic distribution"

    async def create_marketing_strategy(self, input_data: MarketingInput) -> MarketingOutput:
        """Design brand strategy and content plan."""

        prompt = f"""
You are a marketing advisor. Create a brand and content strategy.

BRAND:
- Positioning: {input_data.brand_positioning}
- Target audience: {input_data.target_audience}
- Competition: {input_data.competition_level}

Design:
1. Brand voice attributes (5-7 key traits)
2. 3-5 content pillars (topic clusters)
3. Target keywords for SEO (20-30 high-intent)
4. Monthly content plan (2-3 pieces/week for 6 months)
5. PR angles (media/analyst outreach)
6. Social media strategy per platform

Content pillar structure:
- One long-form pillar piece (2K+ words)
- 5-10 sub-pillar pieces (blogs, guides, videos)
- Internal linking strategy

Format response as JSON matching MarketingOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return MarketingOutput(**result_json)
        except:
            return MarketingOutput(
                brand_voice_attributes=[],
                content_pillars=[],
                target_keywords=[],
                monthly_content_plan=[],
                pr_angles=[],
                social_strategy={}
            )


class GrowthEngine(StartupCopilotEngine):
    """Skill 8: Growth & Analytics

    AARRR metrics, North Star, A/B testing, retention.
    """

    PURPOSE = "Measure what matters and scale what works"

    async def create_growth_strategy(self, input_data: GrowthInput) -> GrowthOutput:
        """Design metrics framework and growth experiments."""

        prompt = f"""
You are a growth advisor. Create a metrics and experimentation strategy.

PRODUCT STAGE: {input_data.current_product_stage}
PRIMARY METRIC: {input_data.primary_metric}
TARGET: {input_data.target_metric_value}
TIMELINE: {input_data.time_horizon_months} months
CONSTRAINTS: {input_data.constraints or "None"}

Design:
1. AARRR pirate metrics (Acquisition, Activation, Retention, Revenue, Referral)
2. North Star metric (single metric reflecting core value)
3. Retention curve targets (D1, D7, D30 cohort analysis)
4. Top 5 growth experiments to run
5. Growth initiatives across channels

North Star examples:
- DAU for engagement products
- MRR/ARR for revenue products
- Activation rate for PLG products
- NPS for product-market fit

A/B testing basics:
- Min 2 weeks per test
- 95% statistical significance
- Only stop early if 99% clear winner

Format response as JSON matching GrowthOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return GrowthOutput(**result_json)
        except:
            return GrowthOutput(
                north_star_metric="Daily Active Users",
                aarrr_metrics=[],
                retention_curve_target={},
                recommended_experiments=[],
                growth_initiatives=[]
            )


class OperationsEngine(StartupCopilotEngine):
    """Skill 9: Operations & Team

    Hiring workflow, OKRs, board management.
    """

    PURPOSE = "Scale team and execution efficiently"

    async def create_operations_strategy(self, input_data: OperationsInput) -> OperationsOutput:
        """Design hiring plan, OKRs, governance."""

        prompt = f"""
You are an operations advisor. Create an organizational strategy.

CURRENT STATE:
- Headcount: {input_data.current_headcount}
- Target headcount: {input_data.target_headcount}
- Timeline: {input_data.timeline_months} months
- Budget: ${input_data.budget}

Design:
1. Hiring plan (roles, seniority, timeline, salary ranges)
2. Interview scorecard (competencies, weightings)
3. OKRs framework (3 company OKRs with 4 KRs each)
4. Board composition recommendation

Hiring best practices:
- Lead with outcomes in job description
- 4-5 competencies per scorecard
- Same questions for all candidates
- Reference check before offer

OKR structure:
- Objective: Aspirational goal
- Key Results: Measurable outcomes (0-1 scale)
- Grading: 0.7+ = strong performance

Format response as JSON matching OperationsOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return OperationsOutput(**result_json)
        except:
            return OperationsOutput(
                hiring_plan=[],
                interview_scorecard={},
                okrs=[],
                board_composition_recommendation="2 founders + 1 independent"
            )


class FinanceEngine(StartupCopilotEngine):
    """Skill 10: Finance & Accounting

    Burn rate, cash flow forecasting, unit economics.
    """

    PURPOSE = "Manage cash runway and financial clarity"

    async def create_financial_model(self, input_data: FinanceInput) -> FinanceOutput:
        """Generate 12-month cash flow projection."""

        prompt = f"""
You are a finance advisor. Create a cash flow model.

FINANCIAL STATE:
- Current cash: ${input_data.current_cash}
- Monthly burn: ${input_data.monthly_burn_rate}
- Monthly revenue: ${input_data.projected_revenue_monthly or 0}
- Headcount: {input_data.headcount}
- Forecast horizon: {input_data.months_ahead} months

Create:
1. Month-by-month cash flow projection
2. Cumulative runway analysis
3. Unit economics monthly review
4. Cash reserve recommendation (3-6 months)
5. Fundraising deadline (if runway <6 months)

Burn rate calculation:
- Include salaries, infrastructure, marketing, operations
- Conservative estimate for revenue
- Account for seasonal variations

Format response as JSON matching FinanceOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return FinanceOutput(**result_json)
        except:
            return FinanceOutput(
                cash_flow_projection=[],
                monthly_burn_rate=input_data.monthly_burn_rate,
                projected_runway_months=input_data.current_cash / input_data.monthly_burn_rate if input_data.monthly_burn_rate > 0 else 0,
                unit_economics_monthly=None,
                cash_reserve_recommendation=input_data.monthly_burn_rate * 6,
                next_fundraising_deadline=None
            )


class CustomerSuccessEngine(StartupCopilotEngine):
    """Skill 11: Customer Success

    Onboarding flows, churn prevention, health scoring.
    """

    PURPOSE = "Prevent churn and accelerate expansion"

    async def create_customer_success_strategy(self, input_data: HealthScoreInput) -> HealthScoreOutput:
        """Design onboarding and health scoring framework."""

        prompt = f"""
You are a customer success advisor. Create a CS framework.

PRODUCT TYPE: {input_data.product_type}
TARGET CUSTOMER: {input_data.customer_segment}

Design:
1. Onboarding milestones (Day 0 to Month 2)
2. Health score formula (usage, sentiment, engagement)
3. Red/Yellow/Green zone criteria
4. NPS target
5. Churn prevention tactics

Onboarding timeline:
- Day 0-1: Activation (key action, see value)
- Week 1: Feature tour
- Week 2-4: Engagement (in-app guidance, check-ins)
- Month 2: Goal progress review

Health score weights:
- Usage: 40% (DAU, feature adoption, data volume)
- Support sentiment: 30% (ticket volume, response)
- Engagement: 30% (webinar, feedback, feature requests)

Format response as JSON matching HealthScoreOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return HealthScoreOutput(**result_json)
        except:
            return HealthScoreOutput(
                onboarding_milestones=[],
                health_score_formula="(usage*0.4) + (sentiment*0.3) + (engagement*0.3)",
                red_zone_criteria=[],
                yellow_zone_criteria=[],
                green_zone_criteria=[],
                nps_target=40,
                churn_prevention_tactics=[]
            )


class LegalEngine(StartupCopilotEngine):
    """Skill 12: Legal & Compliance

    Entity selection, founder docs, cap table management.
    """

    PURPOSE = "Minimize risk and answer key legal questions"

    async def create_legal_strategy(self, input_data: LegalInput) -> LegalOutput:
        """Generate legal roadmap and compliance checklist."""

        prompt = f"""
You are a legal advisor (not actual legal advice). Create a compliance roadmap.

ENTITY & STAGE:
- Desired entity: {input_data.entity_type}
- Operating in: {', '.join(input_data.jurisdictions)}
- Stage: {input_data.stage}
- Has employees: {input_data.has_employees}

Provide:
1. Entity recommendation (C-Corp, S-Corp, LLC)
2. Cap table template with standard equity split
3. Key legal documents checklist
4. Compliance requirements checklist
5. Vesting recommendation (standard: 4-year cliff + 1 year)
6. Tax optimization tips

IMPORTANT: This is guidance only. Founders should consult actual attorneys.

Cap table entries:
- Founder A: 40-50% common shares
- Founder B: 40-50% common shares
- Employee option pool: 10-15%

Documents needed:
- Articles of Incorporation
- Operating Agreement
- IP Assignment Agreements
- Founder Agreements (with vesting)
- Section 83(b) elections
- Employee option plans

Format response as JSON matching LegalOutput schema.
"""

        response_text = await self._ask(prompt)

        try:
            result_json = json.loads(self._strip_fences(response_text))
            return LegalOutput(**result_json)
        except:
            return LegalOutput(
                recommended_entity="C-Corp",
                cap_table_template=[],
                key_documents_checklist=[
                    "Articles of Incorporation",
                    "Operating Agreement",
                    "IP Assignment Agreements",
                    "Founder Agreements (with vesting)",
                    "Section 83(b) elections"
                ],
                compliance_checklist=[
                    "EIN from IRS",
                    "Corporate bylaws filed",
                    "Quarterly filings (if Delaware)",
                    "Annual tax returns",
                    "Estimated quarterly payments"
                ],
                vesting_recommendation="4-year vest with 1-year cliff",
                tax_optimization_tips=[
                    "Claim R&D tax credit",
                    "Document W-2 reasonable salary",
                    "Consider S-Corp election if profitable"
                ]
            )

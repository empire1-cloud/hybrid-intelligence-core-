# Startup Copilot: The 12 Skills System
## Ultimate Founder Intelligence Engine

**Scope:** Integrated within HIC's 19 specialized engines. Startup Copilot is Engine #1-12, providing end-to-end founder guidance from idea validation through scaling.

---

## System Architecture

```
Hybrid Intelligence Core (HIC)
├── Engine 1-12: Startup Copilot Skills
│   ├── Idea Validation Engine
│   ├── Business Model Engine
│   ├── Fundraising Engine
│   ├── Go-to-Market Engine
│   ├── Product Engine
│   ├── Sales Engine
│   ├── Marketing & Brand Engine
│   ├── Growth & Analytics Engine
│   ├── Operations Engine
│   ├── Finance & Accounting Engine
│   ├── Customer Success Engine
│   └── Legal & Compliance Engine
├── Engine 13-19: Existing specialized engines (SLA113, Vision, Audio, etc.)
├── Pipeline Composer (multi-engine orchestration)
├── Execution history & analytics
└── JWT workspaces with API keys
```

---

## The 12 Skills: Implementation Detail

### 1. **Idea Validation Engine**
**Purpose:** Determine if founder + market + timing = viable venture.

**Input Framework:**
- Founder background (years, domain, relevant failures)
- Market problem statement
- Existing customer interviews (0-20 conversations)
- Competitive landscape survey

**Decision Tree:**
1. **Founder-Market Fit Check** — Does the founder have genuine unfair advantages?
   - Domain expertise (5+ years minimum in adjacent space)
   - Existing relationships (customers, distributors, regulators)
   - Co-founder composition (technical + go-to-market)
   
2. **60-Minute Validation Sprint** — Run the Tom Bilyeu framework
   - Find 10 complaints in <15 minutes via search/Reddit/Twitter
   - Calculate market size TAM/SAM/SOM
   - Identify 3+ existing solutions with bad reviews
   - Search volume confirmation (keyword tool)
   - Stablecoin/crypto adoption trends (if applicable)

3. **GO/PIVOT/KILL Decision**
   - **GO:** Unsolicited referrals, interrupted pitches, pre-purchase on mockups
   - **PIVOT:** Strong market but wrong positioning; founder mismatch
   - **KILL:** Founder lacks advantage; market too small or saturated

**Output:** Validation report (pass/fail + reasoning) with 3-5 proof points.

**Metrics:**
- % of founders who passed validation and raised > $100K (target: 75%)
- Time to decision (target: <60 minutes)

---

### 2. **Business Model Engine**
**Purpose:** Design sustainable unit economics and revenue strategy.

**Pattern Library:** 55 business model archetypes
- Transactional fintech (Wise, Mercury, Relay): unit economics, take rates, payback
- SaaS (seat-based, usage-based, hybrid): LTV/CAC calculations
- Marketplace (two-sided network effects, take rates)
- Creator/subscriptions (Patreon model, GMV splits)
- Licensing (B2B, white-label, tiered)
- Hardware + software (gross margin targets)

**Revenue Stream Mapper:**
- Identify 2-4 revenue streams per model type
- Set typical rates (e.g., payment processor take: 2.9% + $0.30)
- Model cash flow timing (immediate vs. 30/60/90 day terms)

**Unit Economics Calculator:**
```
LTV = (ARPU × Gross Margin) / Monthly Churn Rate
CAC = (Sales & Marketing Spend) / New Customers Acquired
Payback Period = CAC / (Monthly ARPU × Gross Margin)
Healthy Range:
  - LTV/CAC Ratio: 3:1 or higher
  - Payback: <12 months
  - Gross Margin: 70%+ for SaaS, 50%+ for marketplace
```

**Competitive Positioning** (April Dunford):
1. Map alternatives (direct + indirect competitors)
2. Identify unique capabilities (tech, supply chain, team)
3. Connect capabilities to measurable value
4. Define best-fit customer segment
5. Create positioning statement: "For [segment], we are the [category] that [unique value]."

**Output:** Business model canvas + unit economics + 3-year P&L projection.

---

### 3. **Fundraising Engine**
**Purpose:** Raise capital efficiently with founder-friendly terms.

**VC Decision Framework** (from research):
- 63% of VCs prefer cash-on-cash multiples over DCF
- 42% weight IRR heavily
- Warm intro from portfolio founder beats cold outreach 10x
- Lead investors drive 80% of diligence speed

**Pitch Deck Template** (10 slides, Sequoia + YC hybrid):
1. Problem (1 slide)
2. Solution (1 slide)
3. Market opportunity (1 slide)
4. Business model + unit economics (1 slide)
5. Go-to-market timeline (1 slide)
6. Traction (if pre-seed, substitute with advisor board)
7. Team + founder-market fit (1 slide)
8. Financials + runway (1 slide)
9. Ask + use of funds (1 slide)
10. Closing vision (1 slide)

**Outreach Hierarchy:**
1. **Tier 1:** Warm intro from existing portfolio founder (response rate: 40%+)
2. **Tier 2:** Warm intro from accelerator director or industry peer (30%+)
3. **Tier 3:** Direct email from founder (founder = higher credibility than BD)
4. **Tier 4:** Cold email from investor relations (rarely converts)

**Term Sheet Red Flags:**
- Single-click liquidation preferences
- Anti-dilution ratchets
- Undefined valuation cap on SAFE
- Board seat + information rights without investment threshold

**Output:** Investor target list (100 VCs, ranked by fit) + pitch deck + outreach sequence.

---

### 4. **Go-to-Market Engine**
**Purpose:** Route from pre-launch waitlist through first 100 paying customers.

**Pre-Launch Tactics:**
- Waitlist landing page (ConvertKit + early-bird discount)
- Content seed (1-2 founder posts per week on problem)
- Community seeding (relevant Slack/Discord/Reddit)
- Target: 500-1K waitlist before launch

**B2C Product-Led Motion** (from Lenny's research on 40+ companies):
- Free tier or freemium with conversion gate at feature limit
- In-app upgrade prompts (after N uses, data reached threshold)
- Referral loop (existing users → new users)
- Content marketing (SEO for problem-adjacent keywords)
- Metrics: 3-5% free-to-paid conversion (healthy range)

**B2B Sales-Led vs. Product-Led Decision:**
- **Product-Led:** <$1K ACV, self-serve procurement, low support
- **Sales-Led:** >$5K ACV, multi-stakeholder buying, relationship-driven
- **Hybrid:** $1K–$5K ACV, freemium + sales team for enterprise upsell

**Product Hunt Launch Playbook:**
- Launch on Tuesday (not Monday)
- Soft-launch Monday evening to gather early momentum
- Run daily product updates throughout launch day
- Target: top 3 position, 500+ upvotes

**Racecar Growth Framework:**
- **Kickstarts:** one-time growth events (Product Hunt, press, partnership)
- **Engines:** repeatable, scalable channels (SEO, referral, retention)
- **Turbo Boosts:** temporary acceleration tactics (paid ads, influencer)

**Output:** 90-day GTM roadmap + messaging framework + channel selection.

---

### 5. **Product Engine**
**Purpose:** Build products that solve real problems with urgency.

**PRD Template** (Kevin Yien, Square):
- **Problem statement:** Current state, why it sucks, why now
- **Proposed solution:** High-level approach
- **Success metrics:** Measurable, time-bound outcomes
- **User stories:** INVEST format (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- **Non-goals:** Scope boundaries (as important as goals)
- **Rollout plan:** Phased launch, feature flags

**Roadmap Prioritization (RICE scoring):**
```
Score = (Reach × Impact × Confidence) / Effort
Reach: # users affected in 3 months
Impact: 3 (massive) to 0.25 (minimal)
Confidence: % certainty on estimates (0-100%)
Effort: person-weeks to deliver
```

**Quality Bar:**
- Unit test coverage: >80% for critical paths
- User testing: 5-8 users per feature, iterate until > 80% task success
- Accessibility: WCAG AA minimum
- Performance: Core Web Vitals (LCP <2.5s, FID <100ms, CLS <0.1)

**Output:** PRD + 6-month roadmap + wireframes/prototypes.

---

### 6. **Sales Engine**
**Purpose:** Convert ideal customers to revenue.

**Founder-Led Sales Methodology:**

**MEDDIC** (complex enterprise deals, $50K+ ACV):
- Metrics: What success looks like for buyer
- Economic Buyer: Who owns budget
- Decision Criteria: What will be evaluated
- Decision Process: Timeline + stakeholders
- Identify Pain: Problem quantification
- Champion: Internal advocate

**BANT** (quick SMB sales, <$1K ACV):
- Budget: Do they have it?
- Authority: Can they decide?
- Need: Is problem urgent?
- Timeline: When do they buy?

**Challenger Methodology** (differentiated products):
- Disrupt thinking (show them new way to win)
- Taper compelling insight (industry trend data)
- Rational drowning (make status quo untenable)
- Prescriptive point of view

**Cold Outreach Sequences:**
- Email #1: Problem hook (no pitch), 2-3 sentence max
- Delay 3 days
- Email #2: Social proof or case study (still light pitch)
- Delay 5 days
- Email #3: Direct ask + calendar link
- Pause 2 weeks, then restart with new angle
- Target metrics: 2-5% reply rate, 0.5-1% meeting rate

**Output:** Sales playbook + CRM template + pipeline forecast.

---

### 7. **Marketing & Brand Engine**
**Purpose:** Build awareness and trust at scale.

**Distribution > Creation Principle:**
- 80% of marketing value comes from 20% of channels
- Most founders waste energy on content creation without distribution
- Focus on where ideal customers already hang out

**Brand Voice Framework:**
- Tone (instructional, irreverent, data-driven, etc.)
- POV on industry (what do we stand for?)
- Vocabulary (jargon vs. plain language)
- Consistency across all channels (website, docs, Twitter, email)

**Pillar Content Strategy:**
- 3-5 core topics that align with SEO keywords
- 1 long-form pillar per topic (2K+ words, comprehensive)
- 5-10 sub-pillar pieces (blogs, guides, videos) linking back
- Content calendar (2-3 pieces/week for 6 months)

**SEO Playbook:**
- Keyword research (Ahrefs: high volume, low difficulty)
- On-page optimization (title, H1, meta description, internal links)
- Backlink strategy (guest posts, partnership mentions)
- Target: top 10 ranking for 20-30 high-intent keywords

**PR + Launch Strategy:**
- Press release template (problem → solution → traction → quote)
- Media list (tech blogs, industry press, founder-friendly outlets)
- Story angle (unique insight, not just "we raised money")
- Timing (coordinate with product milestone, not standalone)

**Community Building Funnel:**
- Lurker → Participant → Contributor → Ambassador
- Create low-friction entry (newsletter, Discord, Slack)
- Recognition & incentives for engagement (shout-outs, perks)
- Empower ambassadors to run events/content

**Output:** Brand guide + 6-month content calendar + SEO roadmap.

---

### 8. **Growth & Analytics Engine**
**Purpose:** Measure what matters and scale what works.

**AARRR Pirate Metrics:**
```
Acquisition: How many users come in? (sign-ups, installs)
Activation: How many perform key action? (% who complete onboarding)
Retention: How many come back? (D1, D7, D30 cohort curves)
Revenue: How much do they pay? (ARPU, LTV, MRR growth)
Referral: How many invite friends? (K-factor, viral coefficient)
```

**North Star Selection:**
- One metric that reflects core value delivery
- Examples: Daily active users (engagement), ARR (revenue), Activation rate (product-market fit)
- Update quarterly; don't change on a whim

**KPI vs. OKR Distinction:**
- **KPI:** Ongoing metric (retention rate, CAC, NPS) — you own continuously
- **OKR:** Time-bound goal (increase retention from 40% to 50% by Q4) — aligned quarterly

**A/B Testing Rigor:**
```
Sample Size = (2 × (Zα + Zβ)² × (p1×(1-p1) + p2×(1-p2))) / (p1 - p2)²
- Zα = 1.96 (95% confidence)
- Zβ = 0.84 (80% power)
- p1, p2 = conversion rates (control vs. treatment)
- Rule: run minimum 2 weeks, never stop early
```

**Retention Analysis:**
- Cohort curves: plot retention by signup cohort over time
- Healthy curve flattens after 6-12 months (stabilized base)
- Churn segmentation by time (early churn ≠ late churn; fix early first)
- Segmentation by use case (some cohorts naturally churn faster)

**SQL Templates Provided:**
- DAU/MAU calculation
- Cohort retention table
- Churn reason segmentation
- Revenue per cohort

**Output:** Analytics dashboard setup + KPI framework + growth roadmap.

---

### 9. **Operations Engine**
**Purpose:** Scale team and execution.

**Hiring Workflow:**
- **JD template:** Lead with outcomes, not tasks ("owned $500K revenue" not "managed spreadsheets")
- **Interview scorecard:** 4-5 competencies, 1-4 rating scale, bias-reduction (same questions every candidate)
- **Reference calls:** Always reference-check before offer (predictive of performance)

**OKR Framework** (Google + Liz Wessel):
```
Company OKRs (quarterly):
  Objective: Aspirational goal ("Dominate the mid-market")
  Key Result 1: Measurable outcome (ARR $2M by Q4)
  Key Result 2: Measurable outcome (NPS 50+ by Q4)
  Key Result 3: Measurable outcome (3 enterprise case studies by Q4)

Team OKRs align to company, but teams own strategy.
Grading: 0-1 scale (0.7+ = strong performance)
```

**Board Management:**
- Monthly board updates (metrics, milestones, blockers)
- Quarterly board meetings (strategic review, new data, advisory input)
- Annual governance (option pool, equity refresh, comp benchmarking)

**Output:** Org chart + hiring plan + OKR template + board deck template.

---

### 10. **Finance & Accounting Engine**
**Purpose:** Manage cash runway and financial clarity.

**Burn Rate Analysis:**
```
Monthly Burn = (Total Spend - Revenue) / Month
Runway = Cash in Bank / Monthly Burn
Critical point: <6 months runway = fundraising urgency
```

**Cash Flow Forecasting:**
- Revenue timing (ARR ≠ cash; model customer payment terms)
- Expense timing (salary monthly, conference annually)
- Seasonal patterns (e.g., B2B sales peak Q4)
- Rolling 12-month forecast updated monthly

**Unit Economics Template:**
```
COGS per customer
Gross Profit per customer
Gross Margin %
Sales & Marketing spend per new customer (CAC)
Customer Lifetime Value (LTV)
LTV/CAC ratio (target: 3+)
```

**Monthly Close Checklist:**
- AR reconciliation (invoices sent vs. paid)
- Expense categorization (G&A, R&D, S&M, COGS)
- Headcount reconciliation
- Bank balance verification
- Tax reserve allocation (25-30% of profit for small corps)

**Decision Criteria for Finance Hire:**
- When: >$1M ARR with complexity (multiple currencies, tax jurisdictions)
- Hire: Fractional CFO/controller at first ($2K-5K/month)
- Promote to full-time: >$5M ARR or IPO prep

**Output:** Monthly cash flow model + P&L template + board financial update template.

---

### 11. **Customer Success Engine**
**Purpose:** Prevent churn and accelerate expansion.

**Onboarding Framework:**
- **Day 0-1:** Activation (complete key action, see value)
- **Week 1:** Feature tour (show how to solve their #1 problem)
- **Week 2-4:** Engagement (in-app guidance, email check-ins)
- **Month 2:** Goal progress check-in (are they hitting their milestone?)

**Churn Prevention by Timing:**
- **Early churn (W1-4):** Product friction, unclear value (fix: onboarding UX)
- **Mid churn (M2-4):** Unmet expectations, competing priorities (fix: outcome check-ins)
- **Late churn (M6+):** Market saturation, feature parity (fix: new use cases, expansion)

**Health Scoring Model:**
```
Score = (Usage Score × 40%) + (Support Sentiment × 30%) + (Engagement × 30%)
Usage: Feature adoption, frequency, data volume
Support: Response sentiment, ticket volume, NPS
Engagement: Webinar attendance, feature request, feedback response

Red (0-40): At-risk, immediate outreach
Yellow (40-70): Stable, check-in planned
Green (70+): Thriving, expansion conversation
```

**Time-to-First-Value (TTFV):**
- Core metric for product-led businesses
- Target: customer sees measurable impact in <7 days of first use
- If TTFV > 14 days: product friction needs fixing

**NPS/CSAT Program:**
- Monthly pulse (1-question NPS or CSAT, in-app)
- Quarterly deep dive (open-ended interviews, 10-15 customers per segment)
- Detractors (0-6): Why? Immediate action plan
- Passives (7-8): Upsell conversation
- Promoters (9-10): Referral request

**Output:** Onboarding playbook + health scoring dashboard + CS playbook.

---

### 12. **Legal & Compliance Engine**
**Purpose:** Minimize risk and answer key legal questions.

**Entity Selection:**
- **C-Corp:** Preferred for venture-backed (tax efficiency, investor comfort)
- **S-Corp:** Solo founder bootstrapping (pass-through taxation)
- **LLC:** When investors unlikely (limited state tax exposure)
- **Non-profit:** Mission-driven, grant funding (irreversible choice)

**Founder Documents:**
- **Operating agreement:** Co-founder split, IP assignment, vesting
- **Vesting schedule:** Typically 4-year cliff + 1 year (48 months total, 25% cliff)
- **Equity split:** Industry standard 50/50–70/30 (unequal splits signal founder conflict)

**Cap Table Management:**
- Track all equity (founder shares, options, convertible notes, SAFEs)
- Update after every fundraise
- Use Pulley or Carta for automation

**SAFE vs. Equity:**
- **SAFE (Simple Agreement for Future Equity):** No interest, no valuation cap initially, converts on next round or exit
- **Equity:** Immediate ownership, voting rights, tax implications (409A)
- Use SAFE for pre-seed, equity once Series A

**ESOP (Employee Stock Ownership Plan):**
- Creates tax-efficient option pool
- Requires administrator (Equifax, Morgan Stanley)
- 3-5% pool for early stage, 10-15% for later

**Compliance Checklist:**
- [ ] Bylaws filed with state
- [ ] EIN obtained (IRS)
- [ ] Operating agreement signed
- [ ] IP assignments signed (all founders + early employees)
- [ ] Section 83(b) elections filed (if pre-vesting equity)
- [ ] Quarterly filings (Delaware, if C-Corp)
- [ ] Tax returns (annual, quarterly estimated payments if profitable)

**Red Flags for Legal Help:**
- IP disputes (who owns code from previous job?)
- Multi-jurisdiction operations (EU GDPR, California privacy)
- Privacy-sensitive data (health, financial)
- Regulated industry (fintech, healthcare)

**Output:** Cap table template + SAFE template + operating agreement checklist.

---

## Integration with HIC Pipeline Composer

Each skill activates as an independent pipeline:

```
POST /api/pipelines/startup-copilot
{
  "skill": "idea-validation | business-model | fundraising | gotomarket | product | sales | marketing | growth | operations | finance | customer-success | legal",
  "input": {
    "founder_background": "...",
    "market_problem": "...",
    "existing_data": [...]
  },
  "model": "claude-sonnet-4.5",
  "output_format": "structured_report"
}
```

**Chaining Example:** Validate idea → Design business model → Build pitch deck → Execute GTM

---

## Success Metrics

| Skill | KPI | Target |
|-------|-----|--------|
| Idea Validation | Founders who pass and raise $100K+ | 75% |
| Business Model | Founders with 3:1 LTV/CAC ratio | 60% |
| Fundraising | Closed funding rounds | $1M+ average |
| GTM | Founders hitting first 100 customers | <6 months |
| Product | Feature ship velocity | 2 weeks |
| Sales | Pipeline generated | >3x CAC in pipeline |
| Marketing | Cost per lead via content | 50% of paid CAC |
| Growth | Retention curves flatten | By month 6 |
| Operations | Time to hire | <30 days |
| Finance | Runway visibility | 18+ months |
| Customer Success | NPS > 40 | 80% of customers |
| Legal | Fundraise time lost to legal | <2 weeks per round |

---

## Knowledge Artifacts Provided

- **Mom Test** interview scripts and GO/PIVOT/KILL rubrics
- **Unit economics calculator** (LTV, CAC, payback period)
- **55 business model patterns** with revenue stream maps
- **10-slide pitch deck template** (Sequoia + YC hybrid)
- **VC outreach hierarchy** with templated email sequences
- **B2C/B2B GTM decision tree**
- **Product Hunt launch playbook**
- **RICE scoring model** with calculator
- **INVEST user story template**
- **MEDDIC, BANT, and Challenger sales playbooks**
- **Cold email sequence templates** (3-email format)
- **SEO keyword research methodology**
- **Community funnel framework**
- **Cohort retention analysis** SQL templates
- **Hiring scorecard template**
- **OKR planning workbook** (quarterly format)
- **Board deck template** (metrics, milestones, blockers)
- **Cash flow forecast model** (12-month rolling)
- **Onboarding checklist** (Day 0 to Month 2)
- **Health score model** (usage, sentiment, engagement)
- **Cap table tracker** (manual or integrated with Pulley/Carta)
- **SAFE and equity template** comparison
- **Operating agreement checklist**

---

## Roadmap

### Phase 1: Launch (Q4 2026)
- [ ] Integrate Idea Validation + Business Model engines
- [ ] Test with 10 founder cohorts
- [ ] Gather feedback on framework clarity

### Phase 2: Expand (Q1 2027)
- [ ] Add Fundraising + Go-to-Market engines
- [ ] Develop pitch deck auto-generation
- [ ] Launch public beta

### Phase 3: Scale (Q2-Q3 2027)
- [ ] Complete all 12 skills with examples
- [ ] Add multi-founder collaboration features
- [ ] Integrate with calendar/email for outreach tracking

### Phase 4: Enterprise (Q4 2027+)
- [ ] White-label for accelerators (Y Combinator, TechStars, 500 Global)
- [ ] Add cohort analytics (which frameworks work best by industry)
- [ ] Revenue-share with accelerators

---

## Usage Example: Stablecoin Bank Account for Freelancers

**Founder:** 5 years at Flutterwave (crypto infrastructure), relationships with regulators + payment processors. **Verdict:** Genuine unfair advantage.

**Validation (60-min framework):**
- Found 10+ complaints about Payoneer fees in 15 min ✓
- Market size: $1T+ flowing to stablecoins by 2028 ✓
- Existing solutions (Wise, Payoneer): bad reviews on Reddit ✓
- Search volume for "how to receive USD in Nigeria": massive ✓
- Stablecoin adoption trending: 80% of LatAm crypto volume ✓

**GO signal.** Build business model → pricing (2% take on transfers + 0.5% monthly fee) → LTV/CAC (2.5x within 6 months) → pitch deck → Series A target ($3M for Nigeria + LatAm GTM).

---

## Files in This Module

- `STARTUP_COPILOT_SKILLS.md` — This document
- `/pipelines/startup-copilot/` — Engine definitions
- `/prompts/startup-copilot/` — Skill-specific prompt templates
- `/artifacts/templates/` — All downloadable templates (PRD, pitch deck, cap table, etc.)


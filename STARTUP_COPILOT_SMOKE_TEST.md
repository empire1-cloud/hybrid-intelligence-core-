# Startup Copilot: End-to-End Smoke Test Plan

## Overview
This document defines the smoke test procedures to verify Startup Copilot works end-to-end before merging PR #9.

**Estimated Duration**: 45 minutes  
**Prerequisites**: API keys configured, dependencies installed, backend + frontend running

---

## Setup (5 minutes)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Verify .env exists with valid API keys
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup  
```bash
cd frontend
npm install
npm run dev
# Should be available at http://localhost:5173 or http://localhost:3000
```

### Verification
- [ ] Backend responds to health check: `curl http://localhost:8000/api/health`
- [ ] Frontend loads without console errors
- [ ] Network tab shows no 404s for startup-copilot routes

---

## Test 1: Dashboard Renders All 12 Skills (10 minutes)

### Steps
1. Navigate to Founder Dashboard
2. Verify all 12 skills are visible with correct icons and descriptions
3. Verify skills are grouped into 5 categories:
   - **Validation** (1): Idea Validation ✓
   - **Funding** (2): Business Model 📊, Fundraising 💰
   - **Execution** (5): Go-to-Market 🚀, Product 🛠, Sales 🤝, Marketing 📢, Growth 📈
   - **Team** (2): Operations ⚙️, Finance 💸
   - **Legal** (1): Legal & Compliance ⚖️
4. Verify workflow shortcuts show (Validate→Pitch, Validate→Launch)

### Verification Checklist
- [ ] All 12 skill cards render with correct names, icons, descriptions
- [ ] Category colors are applied correctly (blue/purple/green/orange/red)
- [ ] No console errors
- [ ] Hover effects work on skill cards
- [ ] Click on a skill opens the form (not an error)

---

## Test 2: Single Skill Form Submission (10 minutes)

### Steps
1. Click on **Idea Validation** skill
2. Form should show 4 fields:
   - Founder Background (object/complex field)
   - Problem Statement (textarea, required)
   - Existing Solutions (array, add multiple)
   - Customer Interviews (number)
3. Fill in sample data:
   ```
   Founder Background: "10 years in fintech, founded 2 previous startups"
   Problem Statement: "Freelancers lack access to banking infrastructure"
   Existing Solutions: ["Stripe Connect", "PayPal", "Traditional Banks"]
   Customer Interviews: 5
   ```
4. Click "Get Results"
5. Should call `/api/startup-copilot/validate-idea` with your data
6. Wait for response (Claude will analyze using Mom Test framework)

### Verification Checklist
- [ ] Form fields render correctly with proper types
- [ ] Required field validation works (submit without Problem Statement → error)
- [ ] Array field works (can add/remove solutions)
- [ ] Form submission sends POST to correct endpoint
- [ ] Network request includes Authorization header
- [ ] Response displays with success message
- [ ] Result shows validation analysis (Mom Test criteria met/gaps)
- [ ] "View & Export" button appears for saved result
- [ ] "New Analysis" button resets form

### Expected Response Structure
```json
{
  "skill": "idea-validation",
  "status": "success",
  "data": {
    "founder_market_fit": "...",
    "market_viability": "...",
    "timing_readiness": "...",
    "recommendations": [...]
  }
}
```

---

## Test 3: All 12 Skills Render Forms (15 minutes)

### Steps
For each skill, click it and verify:
1. Form renders with appropriate fields
2. Form has "Get Results" button (not broken/grayed out)
3. No console errors on form open
4. Click away (back button) doesn't cause errors

### Skill-Specific Checks

| Skill | Key Fields | Expected Response Field |
|-------|-----------|------------------------|
| Idea Validation | founder_background, market_problem | mom_test_analysis |
| Business Model | product_description, target_market | revenue_streams, unit_economics |
| Fundraising | current_stage, target_raise | pitch_deck_outline, investor_targets |
| Go-to-Market | product_type, target_acv | gtm_timeline, channel_strategy |
| Product | problem_statement, target_user | prd_outline, rice_scores |
| Sales | deal_complexity, acv | sales_playbook, methodology |
| Marketing | brand_positioning, target_audience | content_pillars, seo_strategy |
| Growth | current_stage, primary_metric | aarrr_metrics, north_star |
| Operations | current_headcount, target_headcount | hiring_plan, okrs |
| Finance | current_cash, monthly_burn | cash_flow_forecast, runway |
| Customer Success | product_type, segment | onboarding_flow, health_score |
| Legal | entity_type, jurisdictions | compliance_checklist, cap_table |

### Verification Checklist
- [ ] All 12 skills open form without errors
- [ ] Each form has correct field types (text, textarea, number, select, array)
- [ ] No placeholder text masquerading as real functionality
- [ ] All forms have visible "Get Results" buttons
- [ ] Back button returns to skill list

---

## Test 4: Workflow Execution (8 minutes)

### Test 4a: Validate → Pitch Workflow

**Steps**
1. Click workflow shortcut "Validate → Pitch"
2. Should show workflow intro with 3 steps:
   - Step 1: Idea Validation
   - Step 2: Business Model  
   - Step 3: Fundraising
3. Progress bar shows 0% complete
4. Click "Start Idea Validation"
5. Form opens for Idea Validation (same as Test 2)
6. Fill in founder info, submit
7. Progress updates to 33% complete, Step 1 marked done
8. Step 2 unlocks (Business Model)
9. Fill Business Model form
10. Step 3 unlocks (Fundraising)
11. Fill Fundraising form
12. Complete message shows: "All 3 steps completed. Your Validate → Pitch strategy is ready."

### Verification Checklist
- [ ] Workflow intro shows correct steps and expected output
- [ ] Progress bar updates as steps complete
- [ ] Steps lock/unlock in correct order
- [ ] Only current step has "Start" button
- [ ] Completed steps show checkmark ✓
- [ ] Final completion message displays
- [ ] Results can be downloaded/exported

---

## Test 5: Error Handling & Edge Cases (7 minutes)

### Test 5a: Network Error Handling
1. In DevTools, go to Network tab
2. Throttle to "Offline"
3. Try to submit a skill form
4. Should show error message (not hang)
5. Restore network, retry should work

- [ ] Offline error displays gracefully
- [ ] Error message is user-friendly
- [ ] Can retry after network restored

### Test 5b: Validation Errors
1. Open Idea Validation form
2. Try to submit without filling "Problem Statement" (required)
3. Should show inline error "Problem Statement is required"
4. Start typing in field, error clears
5. Complete and submit

- [ ] Required field validation works
- [ ] Error messages are specific (not generic)
- [ ] Errors clear when user starts fixing

### Test 5c: Empty States
1. On dashboard, "Your Results" section shouldn't show until you complete a skill
2. After completing one, result appears in grid

- [ ] Empty results don't show error/broken state
- [ ] Result cards show after skill completion
- [ ] Skill names display correctly in saved results

---

## Test 6: Most Important Founder Workflow (8 minutes)

### Scenario: Pre-seed Founder Validating a Fintech Idea

**Complete this workflow:**
1. Open Dashboard
2. Run "Validate → Pitch" workflow completely
3. Fill with realistic data:
   - **Idea Validation**: "Freelancer banking platform" problem, 8 founder years, 3 interviews
   - **Business Model**: SaaS model, $5k/month ACV, $100M TAM
   - **Fundraising**: Pre-seed stage, raising $500k, using for product + hiring

**Verify at each step:**
- Form accepts realistic data
- API returns substantive analysis (not lorem ipsum)
- Results show actual strategy output (not mocked)
- Workflow progresses smoothly
- Completed workflow accessible in saved results

### Acceptance Criteria
- [ ] Workflow completes without errors
- [ ] Each skill returns substantive analysis
- [ ] No placeholder/demo language ("lorem ipsum", "[PLACEHOLDER]", "TODO")
- [ ] Response time reasonable (<10s per skill)
- [ ] Results display all key sections
- [ ] Can understand next steps from results

---

## Test 7: Dark Mode & Responsive (5 minutes)

### Desktop
- [ ] All components render at 1920x1080
- [ ] Skill cards layout in 3-column grid
- [ ] Forms are readable with proper spacing
- [ ] Buttons are clickable size

### Mobile (responsive)
- [ ] Skill cards stack to 1 column on mobile
- [ ] Form fields are touch-friendly
- [ ] Buttons are adequate size for touch
- [ ] No horizontal scrolling needed

### Dark Mode
- [ ] Toggle dark mode (if available)
- [ ] All colors remain readable
- [ ] Forms don't become unreadable
- [ ] Category color badges visible in both modes

- [ ] Desktop layout works (1920px)
- [ ] Mobile layout works (375px)
- [ ] Dark mode readable
- [ ] Light mode readable

---

## Known Issues & Acceptable Limitations

| Issue | Status | Notes |
|-------|--------|-------|
| PDF export not implemented | Expected | Shows "Export as PDF" button but not yet wired |
| Result versioning | Expected | Results save, but no version history yet |
| Team collaboration | Expected | Phase 4 feature, not in Phase 3 |
| Advanced result filtering | Expected | Phase 4 feature, not in Phase 3 |

---

## Sign-Off Checklist

### Mandatory (Must Pass)
- [ ] All 12 skills render without errors
- [ ] At least one complete skill submission works (API → response)
- [ ] One complete workflow executes end-to-end
- [ ] No placeholder text masquerading as production capability
- [ ] No console JavaScript errors
- [ ] Network requests go to correct endpoints
- [ ] Forms show validation errors appropriately

### Expected (Should Pass)
- [ ] All 12 skills accept form data
- [ ] Results display substantive output (not mocked)
- [ ] Workflow progress tracking works
- [ ] Responsive layout works on mobile
- [ ] Dark mode readable

### Nice-to-Have (Optional)
- [ ] PDF export works
- [ ] Result search/filtering
- [ ] Saved results persistence across sessions

---

## Merge Decision

✅ **MERGE PR #9 if:**
- All mandatory checks pass
- No critical bugs found
- System is production-ready for Phase 3 (UI complete)
- Backend/frontend successfully communicate

❌ **DO NOT MERGE if:**
- Placeholder text appears in production responses
- Forms don't submit to correct endpoints
- Founder workflow breaks before completion
- Unhandled console errors prevent use

---

## Post-Merge (Phase 4 - Optional)

After merging Phase 3, consider:
- [ ] Result versioning and history
- [ ] PDF export implementation
- [ ] Team workspace collaboration
- [ ] Advanced result filtering and search
- [ ] Analytics on which skills are used most
- [ ] Integration with investor CRM (Salesloft, Pipedrive)


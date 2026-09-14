/**
 * Startup Copilot: Skill catalog
 *
 * Each entry mirrors one endpoint on /api/startup-copilot and the Pydantic
 * input model behind it (backend/services/startup_copilot_models.py).
 * Fields marked `required` are the ones the model declares with Field(...);
 * everything else has a server-side default and is omitted when left blank.
 */

export const CATEGORIES = [
  { id: 'validation', title: 'Validate', blurb: 'Confirm the idea is worth pursuing.' },
  { id: 'funding', title: 'Fund', blurb: 'Model the business and raise capital.' },
  { id: 'execution', title: 'Execute', blurb: 'Build, launch, sell, and grow.' },
  { id: 'team', title: 'Operate', blurb: 'Staff the company and manage the money.' },
  { id: 'legal', title: 'Protect', blurb: 'Entity, equity, and compliance.' },
];

export const SKILLS = [
  {
    id: 'idea-validation',
    name: 'Idea Validation',
    endpoint: 'validate-idea',
    category: 'validation',
    icon: '✓',
    framework: 'Mom Test',
    description: 'Pressure-test founder-market fit and decide go / pivot / kill.',
    // IdeaValidationInput nests founder_background as a FounderBackground model.
    buildPayload: ({
      years_experience,
      domain,
      previous_exits,
      industry_relationships,
      ...rest
    }) => ({
      ...rest,
      founder_background: {
        years_experience: years_experience ?? 0,
        domain: domain ?? '',
        ...(previous_exits !== undefined ? { previous_exits } : {}),
        ...(industry_relationships ? { industry_relationships } : {}),
      },
    }),
    fields: [
      { name: 'years_experience', label: 'Years in this domain', type: 'number', required: true, placeholder: '8' },
      { name: 'domain', label: 'Your domain expertise', type: 'text', required: true, placeholder: 'Fintech / payments' },
      { name: 'previous_exits', label: 'Previous exits', type: 'number', placeholder: '0' },
      { name: 'industry_relationships', label: 'Key relationships', type: 'array', placeholder: 'Add a relationship' },
      {
        name: 'market_problem',
        label: 'Problem statement',
        type: 'textarea',
        required: true,
        placeholder: 'Who hurts, how often, and what does it cost them today?',
      },
      { name: 'existing_solutions', label: 'Existing solutions', type: 'array', placeholder: 'Add a competitor' },
      { name: 'interviews_conducted', label: 'Customer interviews done', type: 'number', placeholder: '0' },
    ],
  },
  {
    id: 'business-model',
    name: 'Business Model',
    endpoint: 'design-business-model',
    category: 'funding',
    icon: '📊',
    framework: '55 business model patterns',
    description: 'Pick a revenue model and pressure-test LTV/CAC.',
    fields: [
      { name: 'product_description', label: 'Product description', type: 'textarea', required: true },
      { name: 'target_market', label: 'Target market', type: 'text', required: true, placeholder: 'US freelancers earning $50k+' },
      { name: 'market_size_tam', label: 'TAM estimate ($)', type: 'number', placeholder: '500000000' },
      { name: 'existing_business_models', label: 'Competitor models', type: 'array', placeholder: 'e.g. Stripe: take rate' },
      { name: 'founder_preferences', label: 'Constraints or preferences', type: 'textarea' },
    ],
  },
  {
    id: 'fundraising',
    name: 'Fundraising',
    endpoint: 'create-fundraising-strategy',
    category: 'funding',
    icon: '💰',
    framework: '10-slide pitch deck',
    description: 'Build the deck outline and target the right investors.',
    fields: [
      {
        name: 'current_stage',
        label: 'Stage',
        type: 'select',
        required: true,
        options: [
          { value: 'pre_seed', label: 'Pre-seed' },
          { value: 'seed', label: 'Seed' },
          { value: 'series_a', label: 'Series A' },
          { value: 'series_b', label: 'Series B' },
        ],
      },
      { name: 'target_raise', label: 'Target raise ($)', type: 'number', required: true, placeholder: '500000' },
      { name: 'use_of_funds', label: 'Use of funds', type: 'textarea', required: true },
      { name: 'runway_months', label: 'Current runway (months)', type: 'number', required: true, placeholder: '9' },
      { name: 'traction', label: 'Traction to date', type: 'textarea' },
    ],
  },
  {
    id: 'gtm',
    name: 'Go-to-Market',
    endpoint: 'create-gtm-strategy',
    category: 'execution',
    icon: '🚀',
    framework: 'PLG vs. sales-led',
    description: 'Choose a motion and lay out the first 90 days.',
    fields: [
      {
        name: 'product_type',
        label: 'Product type',
        type: 'select',
        required: true,
        options: [
          { value: 'b2b_saas', label: 'B2B SaaS' },
          { value: 'b2c', label: 'B2C' },
          { value: 'marketplace', label: 'Marketplace' },
        ],
      },
      { name: 'target_acv', label: 'Target ACV ($)', type: 'number', required: true, placeholder: '12000' },
      { name: 'target_customers', label: 'First-customer goal', type: 'number', required: true, placeholder: '100' },
      { name: 'founder_background', label: 'Your relevant background', type: 'textarea', required: true },
      { name: 'market_context', label: 'Market context', type: 'textarea' },
    ],
  },
  {
    id: 'product',
    name: 'Product',
    endpoint: 'create-product-strategy',
    category: 'execution',
    icon: '🛠',
    framework: 'RICE prioritization',
    description: 'Write the PRD and rank the roadmap.',
    fields: [
      { name: 'problem_statement', label: 'Problem statement', type: 'textarea', required: true },
      { name: 'target_user', label: 'Target user', type: 'text', required: true },
      { name: 'key_features', label: 'Key features', type: 'array', required: true, placeholder: 'Add a feature' },
      { name: 'success_metrics', label: 'Success metrics', type: 'array', required: true, placeholder: 'e.g. activation rate' },
    ],
  },
  {
    id: 'sales',
    name: 'Sales',
    endpoint: 'create-sales-strategy',
    category: 'execution',
    icon: '🤝',
    framework: 'MEDDIC / BANT',
    description: 'Pick a qualification method and build the playbook.',
    fields: [
      {
        name: 'deal_complexity',
        label: 'Deal complexity',
        type: 'select',
        required: true,
        options: [
          { value: 'simple', label: 'Simple' },
          { value: 'moderate', label: 'Moderate' },
          { value: 'complex', label: 'Complex' },
        ],
      },
      { name: 'acv', label: 'ACV ($)', type: 'number', required: true, placeholder: '12000' },
      { name: 'buyer_profile', label: 'Buyer profile', type: 'textarea', required: true, placeholder: 'Who signs, who blocks?' },
      { name: 'competitive_landscape', label: 'Competitive landscape', type: 'textarea' },
    ],
  },
  {
    id: 'marketing',
    name: 'Marketing & Brand',
    endpoint: 'create-marketing-strategy',
    category: 'execution',
    icon: '📢',
    framework: 'Pillar content',
    description: 'Set brand voice, content pillars, and SEO plan.',
    fields: [
      { name: 'brand_positioning', label: 'Brand positioning', type: 'textarea', required: true },
      { name: 'target_audience', label: 'Target audience', type: 'text', required: true },
      {
        name: 'competition_level',
        label: 'Competition level',
        type: 'select',
        required: true,
        options: [
          { value: 'low', label: 'Low' },
          { value: 'medium', label: 'Medium' },
          { value: 'high', label: 'High' },
        ],
      },
      { name: 'budget', label: 'Monthly budget ($)', type: 'number' },
    ],
  },
  {
    id: 'growth',
    name: 'Growth & Analytics',
    endpoint: 'create-growth-strategy',
    category: 'execution',
    icon: '📈',
    framework: 'AARRR',
    description: 'Define the North Star and the funnel to move it.',
    fields: [
      {
        name: 'current_product_stage',
        label: 'Product stage',
        type: 'select',
        required: true,
        options: [
          { value: 'idea', label: 'Idea' },
          { value: 'mvp', label: 'MVP' },
          { value: 'beta', label: 'Beta' },
          { value: 'live', label: 'Live' },
        ],
      },
      { name: 'primary_metric', label: 'Primary metric', type: 'text', required: true, placeholder: 'Weekly active teams' },
      { name: 'target_metric_value', label: 'Target value', type: 'number', required: true, placeholder: '1000' },
      { name: 'time_horizon_months', label: 'Time horizon (months)', type: 'number', required: true, placeholder: '6' },
      { name: 'constraints', label: 'Constraints', type: 'textarea' },
    ],
  },
  {
    id: 'operations',
    name: 'Operations',
    endpoint: 'create-operations-strategy',
    category: 'team',
    icon: '⚙️',
    framework: 'OKRs',
    description: 'Plan hiring, set OKRs, run the board.',
    fields: [
      { name: 'current_headcount', label: 'Current headcount', type: 'number', required: true, placeholder: '3' },
      { name: 'target_headcount', label: 'Target headcount', type: 'number', required: true, placeholder: '12' },
      { name: 'timeline_months', label: 'Timeline (months)', type: 'number', required: true, placeholder: '12' },
      { name: 'budget', label: 'Hiring budget ($)', type: 'number', required: true, placeholder: '750000' },
    ],
  },
  {
    id: 'finance',
    name: 'Finance',
    endpoint: 'create-financial-model',
    category: 'team',
    icon: '💸',
    framework: 'Cash flow & runway',
    description: 'Forecast burn, runway, and the next raise date.',
    fields: [
      { name: 'current_cash', label: 'Cash in bank ($)', type: 'number', required: true, placeholder: '400000' },
      { name: 'monthly_burn_rate', label: 'Monthly burn ($)', type: 'number', required: true, placeholder: '45000' },
      { name: 'headcount', label: 'Headcount', type: 'number', required: true, placeholder: '5' },
      { name: 'projected_revenue_monthly', label: 'Monthly revenue ($)', type: 'number' },
      { name: 'months_ahead', label: 'Months to forecast', type: 'number', placeholder: '12' },
    ],
  },
  {
    id: 'customer-success',
    name: 'Customer Success',
    endpoint: 'create-customer-success-strategy',
    category: 'execution',
    icon: '😊',
    framework: 'Health scoring',
    description: 'Design onboarding and catch churn before it happens.',
    fields: [
      {
        name: 'product_type',
        label: 'Motion',
        type: 'select',
        required: true,
        options: [
          { value: 'plg', label: 'Product-led' },
          { value: 'sales_led', label: 'Sales-led' },
        ],
      },
      { name: 'customer_segment', label: 'Customer segment', type: 'text', required: true, placeholder: 'SMB, 10-50 seats' },
    ],
  },
  {
    id: 'legal',
    name: 'Legal & Compliance',
    endpoint: 'create-legal-strategy',
    category: 'legal',
    icon: '⚖️',
    framework: 'Entity & cap table',
    description: 'Entity choice, equity split, and the compliance checklist.',
    fields: [
      {
        name: 'entity_type',
        label: 'Entity type',
        type: 'select',
        required: true,
        options: [
          { value: 'c_corp', label: 'C-Corp' },
          { value: 'llc', label: 'LLC' },
          { value: 's_corp', label: 'S-Corp' },
        ],
      },
      { name: 'jurisdictions', label: 'Operating jurisdictions', type: 'array', required: true, placeholder: 'e.g. Delaware' },
      {
        name: 'stage',
        label: 'Stage',
        type: 'select',
        required: true,
        options: [
          { value: 'pre_seed', label: 'Pre-seed' },
          { value: 'seed', label: 'Seed' },
          { value: 'series_a', label: 'Series A' },
        ],
      },
      { name: 'has_employees', label: 'Employees', type: 'checkbox', checkboxLabel: 'We have W-2 employees' },
    ],
  },
];

export const getSkill = (id) => SKILLS.find((s) => s.id === id);

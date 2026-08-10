import { Link } from 'react-router-dom';

const FOUNDER_EMAIL = 'founder@empire1.cloud';

const APP_PLANS = [
  {
    tag: 'Explore',
    name: 'Free',
    price: '$0',
    cadence: '/month',
    description: 'A real HIC workspace for learning the system and running a small monthly workload.',
    items: ['100 executions / month', '3 team members', '2 API keys', '5 pipelines', 'Basic engines'],
    action: 'Create a free workspace',
    href: '/signup',
  },
  {
    tag: 'Hosted HIC App',
    name: 'HIC Pro',
    price: '$299',
    cadence: '/month',
    description: 'The complete hosted application for builders who want engines, pipelines, history, analytics, API keys, and a team workspace.',
    items: ['5,000 executions / month', '10 team members', '10 API keys', '50 pipelines', 'All approved HIC engines', 'Advanced analytics'],
    action: 'Start with HIC Pro',
    href: '/signup',
    featured: true,
  },
  {
    tag: 'Hosted HIC App',
    name: 'HIC Enterprise App',
    price: 'From $1,500',
    cadence: '/month',
    description: 'A larger hosted workspace with negotiated capacity, governance, priority support, and custom integrations.',
    items: ['Larger included allowance', 'Advanced governance', 'Priority capacity', 'Dedicated support', 'Custom integrations'],
    action: 'Contact the founder',
    href: `mailto:${FOUNDER_EMAIL}?subject=HIC%20Enterprise%20App`,
    external: true,
  },
];

const COMMERCIAL_PATHS = [
  {
    tag: 'One-Time Service',
    name: 'Revenue Sprint',
    price: '$999',
    cadence: 'one time',
    description: 'Done-with-you. The Revenue OS output runs first, then we refine it together until the offer and close path are sharp.',
    items: ['Everything in the Revenue Receipt', 'One custom refinement pass', 'One direct founder session', 'Final close-ready delivery'],
    note: 'No recurring charge. Additional implementation is separate.',
    action: 'Book a Sprint',
    subject: 'Empire-1 Revenue Sprint',
  },
  {
    tag: 'Managed Service',
    name: 'Empire Partnership',
    price: 'From $5,000',
    cadence: '/month',
    description: 'Done-for-you and ongoing. Empire-1 builds, integrates, and operates the customer universe on HIC.',
    items: ['Everything in the Sprint', 'Custom universe build and integration', 'Managed pipelines and operation', 'Direct founder access while active'],
    note: 'Monthly after onboarding. Cancel before the next renewal. Onboarding and custom build work are priced separately.',
    action: 'Discuss a Partnership',
    subject: 'Empire-1 Partnership',
  },
  {
    tag: 'White-Label License',
    name: 'License HIC',
    price: 'From $2,500',
    cadence: '/month',
    description: 'Embed the intelligence layer underneath an existing product. The licensee keeps its own product, customers, name, and customer-facing experience.',
    items: ['Routing Engine', 'Canon Enforcer', 'Format Normalizer', 'Drift Monitor', 'Deployment-scoped engine and pipeline access', 'Zero Empire-1 customer-facing branding'],
    note: 'Month-to-month after activation. One-time implementation starts around $5,000 and depends on deployment scope.',
    action: 'License the Engine',
    subject: 'HIC Engine License',
    featured: true,
  },
  {
    tag: 'Factory License',
    name: 'License SLA113',
    price: 'From $7,500',
    cadence: '/month',
    description: 'Run the full operator platform: console, HIC, specialized engine set, orchestration, dashboards, and branded instance minting.',
    items: ['Everything in the HIC license', 'Full operator console', 'Specialized engine set', 'Pipeline orchestration', 'Revenue and analytics dashboards', 'Self-service branded instance minting'],
    note: 'Month-to-month after implementation. One-time implementation starts around $15,000 and depends on infrastructure and instance scope.',
    action: 'License the Factory',
    subject: 'SLA113 Factory License',
  },
];

const PricingCard = ({ plan, commercial = false }) => {
  const actionHref = commercial
    ? `mailto:${FOUNDER_EMAIL}?subject=${encodeURIComponent(plan.subject)}`
    : plan.href;

  const action = plan.external || commercial ? (
    <a className="license-action" href={actionHref}>{plan.action} →</a>
  ) : (
    <Link className="license-action" to={actionHref}>{plan.action} →</Link>
  );

  return (
    <article className={`license-card${plan.featured ? ' featured' : ''}`}>
      {plan.featured && <div className="recommended-label">RECOMMENDED START</div>}
      <div className="license-tag">{plan.tag}</div>
      <h3>{plan.name}</h3>
      <div className="license-price">
        <strong>{plan.price}</strong>
        <span>{plan.cadence}</span>
      </div>
      <p className="license-description">{plan.description}</p>
      <ul>
        {plan.items.map((item) => <li key={item}>— {item}</li>)}
      </ul>
      {plan.note && <p className="license-note">{plan.note}</p>}
      <div className="license-card-footer">{action}</div>
    </article>
  );
};

const LicensingPage = () => {
  return (
    <div className="page-container licensing-page">
      <header className="licensing-hero">
        <div className="licensing-eyebrow">EMPIRE-1 COMMERCIAL PATHS</div>
        <h1>Use the app. License the engine. License the factory.</h1>
        <p>Each path is priced for what the customer is actually receiving. Hosted HIC is a software subscription. Licensing places Empire-1 infrastructure underneath another company. Partnership means we operate it with them.</p>
        <div className="no-lockin-line"><span /> Monthly services are cancel-anytime with no long-term lock-in.</div>
      </header>

      <section className="licensing-section">
        <div className="section-heading">
          <div>
            <div className="licensing-eyebrow">USE HIC</div>
            <h2>Hosted application subscriptions</h2>
          </div>
          <p>Customers log into the HIC app and use the engines, Pipeline Composer, history, analytics, team workspace, and API keys. They are not licensing the underlying platform.</p>
        </div>
        <div className="app-plan-grid">
          {APP_PLANS.map((plan) => <PricingCard key={plan.name} plan={plan} />)}
        </div>
        <div className="terms-strip">
          <strong>Monthly billing. Cancel anytime.</strong>
          <span>Paid access remains active through the current billing period. Additional usage is agreed before it is charged—no surprise automatic overages.</span>
        </div>
      </section>

      <section className="licensing-section commercial-section">
        <div className="section-heading">
          <div>
            <div className="licensing-eyebrow">BUILD, OPERATE, OR LICENSE</div>
            <h2>Higher-touch Empire-1 paths</h2>
          </div>
          <p>These are not ordinary HIC accounts. They include founder time, integration, managed operation, white-label infrastructure, or the complete factory platform.</p>
        </div>
        <div className="commercial-grid">
          {COMMERCIAL_PATHS.map((plan) => <PricingCard key={plan.name} plan={plan} commercial />)}
        </div>
      </section>

      <section className="difference-panel">
        <div>
          <div className="difference-label">USE HIC</div>
          <h3>Your team works inside our hosted application.</h3>
          <p>Fastest start, self-service workspace, monthly subscription, included usage limits.</p>
        </div>
        <div>
          <div className="difference-label">LICENSE HIC</div>
          <h3>Our intelligence runs underneath your product.</h3>
          <p>Your brand stays customer-facing. Integration and deployment scope are separate from the monthly license.</p>
        </div>
        <div>
          <div className="difference-label">LICENSE SLA113</div>
          <h3>You operate the complete branded factory.</h3>
          <p>Full console, engines, orchestration, dashboards, and instance minting—not merely API access.</p>
        </div>
      </section>

      <section className="license-final-cta">
        <div>
          <div className="licensing-eyebrow">NO TRAP. CLEAR SCOPE.</div>
          <h2>Stay because the system earns its place.</h2>
          <p>Monthly services can be canceled before the next renewal. One-time onboarding, implementation, custom development, infrastructure, and model usage are scoped separately and confirmed before work begins.</p>
        </div>
        <a className="license-action primary" href={`mailto:${FOUNDER_EMAIL}?subject=Empire-1%20Commercial%20Path`}>Talk to the founder →</a>
      </section>

      <style>{`
        .licensing-page{max-width:1180px}.licensing-hero{padding:34px 0 58px;border-bottom:1px solid var(--border-color)}.licensing-eyebrow{font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.17em;text-transform:uppercase;color:var(--gold);margin-bottom:14px}.licensing-hero h1{font-family:'Barlow Condensed',sans-serif;font-size:clamp(42px,7vw,72px);line-height:.95;text-transform:uppercase;max-width:900px;margin:0 0 22px}.licensing-hero>p{max-width:760px;color:var(--ink-3);font-size:15px;line-height:1.75}.no-lockin-line{display:inline-flex;align-items:center;gap:9px;margin-top:18px;padding:10px 13px;border:1px solid rgba(0,212,170,.25);background:rgba(0,212,170,.05);font-family:'JetBrains Mono',monospace;font-size:10.5px;text-transform:uppercase;color:var(--accent-green)}.no-lockin-line span{width:7px;height:7px;border-radius:50%;background:var(--accent-green);box-shadow:0 0 9px rgba(0,212,170,.8)}.licensing-section{padding:58px 0;border-bottom:1px solid var(--border-color)}.section-heading{display:flex;justify-content:space-between;align-items:flex-end;gap:30px;margin-bottom:28px}.section-heading h2,.license-final-cta h2{font-family:'Barlow Condensed',sans-serif;font-size:38px;line-height:1;text-transform:uppercase;margin:0}.section-heading>p{max-width:530px;color:var(--ink-3);font-size:13.5px;line-height:1.65}.app-plan-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.commercial-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.license-card{position:relative;border:1px solid var(--border-color);background:rgba(255,255,255,.018);padding:26px;display:flex;flex-direction:column;min-height:100%}.license-card.featured{border-color:rgba(232,185,35,.58);background:linear-gradient(180deg,rgba(232,185,35,.055),rgba(255,255,255,.012))}.recommended-label{position:absolute;right:0;top:0;padding:7px 9px;background:var(--gold);color:#050505;font-family:'JetBrains Mono',monospace;font-size:8.5px;font-weight:700;letter-spacing:.09em}.license-tag{font-family:'JetBrains Mono',monospace;font-size:9.5px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-4);margin-bottom:13px}.license-card h3{font-family:'Barlow Condensed',sans-serif;font-size:28px;text-transform:uppercase;margin:0}.license-price{display:flex;align-items:baseline;gap:7px;margin:12px 0 15px}.license-price strong{font-family:'Barlow Condensed',sans-serif;font-size:34px}.license-price span{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--gold);text-transform:uppercase}.license-description{font-size:13.5px;color:var(--ink-3);line-height:1.65}.license-card ul{list-style:none;padding:0;margin:4px 0 20px;color:var(--ink-3);font-size:12.5px;line-height:1.75}.license-note{font-size:11.5px;color:var(--ink-4);line-height:1.6;margin-top:auto}.license-card-footer{margin-top:20px}.license-action{display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--border-strong);padding:12px 15px;color:var(--text);text-decoration:none;font-family:'JetBrains Mono',monospace;font-size:10px;text-transform:uppercase;letter-spacing:.07em;transition:.2s}.license-action:hover{border-color:var(--gold);color:var(--gold)}.license-action.primary{background:var(--gold);color:#050505;border-color:var(--gold);font-weight:700}.terms-strip{display:grid;grid-template-columns:250px 1fr;gap:24px;margin-top:16px;padding:18px 20px;border-left:2px solid var(--accent-green);background:rgba(0,212,170,.035)}.terms-strip strong{font-size:13px}.terms-strip span{font-size:12.5px;color:var(--ink-3);line-height:1.6}.difference-panel{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--border-color);border:1px solid var(--border-color);margin:58px 0}.difference-panel>div{background:var(--surface,#0d0d12);padding:28px}.difference-label{font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--gold);letter-spacing:.1em;margin-bottom:14px}.difference-panel h3{font-family:'Barlow Condensed',sans-serif;font-size:24px;text-transform:uppercase;margin:0 0 12px}.difference-panel p{color:var(--ink-3);font-size:12.5px;line-height:1.65}.license-final-cta{display:flex;justify-content:space-between;align-items:center;gap:30px;padding:0 0 60px}.license-final-cta p{max-width:760px;color:var(--ink-3);font-size:13.5px;line-height:1.7}@media(max-width:900px){.app-plan-grid{grid-template-columns:1fr}.commercial-grid{grid-template-columns:1fr}.section-heading,.license-final-cta{flex-direction:column;align-items:flex-start}.difference-panel{grid-template-columns:1fr}.terms-strip{grid-template-columns:1fr}}@media(max-width:520px){.licensing-hero h1{font-size:45px}.license-card{padding:22px}.no-lockin-line{align-items:flex-start}}
      `}</style>
    </div>
  );
};

export default LicensingPage;

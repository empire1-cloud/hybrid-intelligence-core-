import { Link } from "react-router-dom";
import {
  ArrowRight,
  Layers,
  Compass,
  ShieldCheck,
  FileCheck2,
  Lock,
} from "lucide-react";
import "../styles/Landing.css";

/**
 * Public marketing landing page — /welcome.
 *
 * Presentation only: no data fetching, no auth logic, no new API calls.
 * Every plan price/name below mirrors the real values in LicensingPage.jsx
 * (APP_PLANS) and every Startup Copilot skill mirrors the real catalog in
 * components/startup-copilot/skills.js — nothing here is invented product
 * capability, only the framing.
 */

const PROOF_STATS = [
  { num: "19", label: "Production AI engines, one workspace" },
  { num: "12", label: "Founder-advisory skills (Startup Copilot)" },
  { num: "100%", label: "Of executions logged — model, cost, confidence" },
  { num: "0", label: "Silent model substitutions. Policy is enforced, not implied." },
];

const ENGINE_TAGS = [
  "Money Pipeline",
  "Pipeline Composer",
  "Blueprint Engine",
  "Strategy Engine",
  "Persona Engine",
  "Evaluator Engine",
  "Opportunity Mapper",
  "Canon Enforcer",
  "Drift Monitor",
  "+ 10 more",
];

const COPILOT_SKILLS = [
  { name: "Idea Validation", fw: "Mom Test" },
  { name: "Business Model", fw: "55 patterns" },
  { name: "Fundraising", fw: "10-slide deck" },
  { name: "Go-to-Market", fw: "PLG vs. sales-led" },
  { name: "Product", fw: "RICE prioritization" },
  { name: "Sales", fw: "MEDDIC / BANT" },
  { name: "Marketing & Brand", fw: "Pillar content" },
  { name: "Growth & Analytics", fw: "AARRR" },
  { name: "Operations", fw: "OKRs" },
  { name: "Finance", fw: "Cash flow & runway" },
  { name: "Customer Success", fw: "Health scoring" },
  { name: "Legal & Compliance", fw: "Entity & cap table" },
];

const STEPS = [
  {
    n: "01",
    title: "Ask",
    body: "Run an engine or a Startup Copilot skill from the dashboard — no prompt engineering required.",
  },
  {
    n: "02",
    title: "Route",
    body: "The call goes through an enforced model policy. Unapproved or blocked models fail closed, not silently.",
  },
  {
    n: "03",
    title: "Log",
    body: "Every execution records provider, model, tokens, cost, latency, and a confidence score — automatically.",
  },
  {
    n: "04",
    title: "Decide",
    body: "You see the full trail in History and Analytics. The system advises. Your team decides.",
  },
];

const PLANS = [
  {
    tag: "Explore",
    name: "Free",
    price: "$0",
    cadence: "/month",
    description: "A real HIC workspace for learning the system on a small monthly workload.",
    items: ["100 executions / month", "3 team members", "2 API keys", "5 pipelines"],
    cta: "Start free",
    href: "/signup",
  },
  {
    tag: "Hosted HIC App",
    name: "HIC Pro",
    price: "$299",
    cadence: "/month",
    description: "The complete hosted app: engines, pipelines, history, analytics, and a team workspace.",
    items: ["5,000 executions / month", "10 team members", "All approved engines", "Advanced analytics"],
    cta: "Get started",
    href: "/signup",
    featured: true,
  },
  {
    tag: "Hosted HIC App",
    name: "Enterprise",
    price: "From $1,500",
    cadence: "/month",
    description: "Negotiated capacity, governance, priority support, and custom integrations.",
    items: ["Larger included allowance", "Advanced governance", "Priority capacity", "Dedicated support"],
    cta: "Talk to us",
    href: "mailto:founder@empire1.cloud?subject=HIC%20Enterprise",
  },
];

const LandingPage = () => {
  return (
    <div className="landing-page" data-testid="landing-page">
      {/* Hero */}
      <section className="lp-hero">
        <div className="lp-section lp-hero-inner">
          <div className="lp-eyebrow">
            <span className="dot" />
            Hybrid Intelligence Core
          </div>
          <h1>
            Run your company's AI decisions <span className="accent">like an operation</span>, not an experiment.
          </h1>
          <p className="lp-hero-sub">
            HIC gives you a 19-engine AI pipeline and a 12-skill Startup Copilot in one
            workspace — plus a full record of what every AI call actually did. No black
            box, no silent model swaps, no guessing what you paid for.
          </p>
          <div className="lp-hero-ctas">
            <Link to="/signup" className="lp-btn primary" data-testid="lp-hero-cta">
              Start free <ArrowRight size={16} />
            </Link>
            <a href="#pricing" className="lp-btn ghost">
              See pricing
            </a>
          </div>
          <p className="lp-hero-fineprint">Free plan included. Upgrade when you outgrow it.</p>

          <div className="lp-proof">
            {PROOF_STATS.map((s) => (
              <div className="lp-proof-item" key={s.label}>
                <div className="lp-proof-num">{s.num}</div>
                <div className="lp-proof-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Two systems / benefits */}
      <section className="lp-block">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              What you get
            </div>
            <h2>Two systems. One workspace.</h2>
            <p>
              You don't wire up engines or manage prompts. You pick a job to get done, and
              HIC runs it through the right specialized system.
            </p>
          </div>

          <div className="lp-systems">
            <div className="lp-system-card">
              <div className="lp-system-icon">
                <Layers size={22} />
              </div>
              <h3>The Engine Pipeline</h3>
              <p>
                19 specialized engines — turn a raw idea into a monetization plan, a
                blueprint, a brand voice, or a go/no-go call — and chain them together in
                the Pipeline Composer when one pass isn't enough.
              </p>
              <div className="lp-tag-grid">
                {ENGINE_TAGS.map((t) => (
                  <span className="lp-tag" key={t}>
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <div className="lp-system-card">
              <div className="lp-system-icon">
                <Compass size={22} />
              </div>
              <h3>Startup Copilot</h3>
              <p>
                12 founder-advisory skills covering validation through legal — each one
                built on a named operating framework, not generic chat advice.
              </p>
              <div className="lp-skill-list">
                {COPILOT_SKILLS.slice(0, 6).map((s) => (
                  <div className="lp-skill-row" key={s.name}>
                    <span className="lp-skill-name">{s.name}</span>
                    <span className="lp-skill-fw">{s.fw}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Evidence / how it works */}
      <section className="lp-block">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              Why it's trustworthy
            </div>
            <h2>AI advises. Your team decides.</h2>
            <p>
              Every call through HIC is instrumented, not just executed. That's the
              difference between an AI feature and an AI system you can actually run a
              company on.
            </p>
          </div>

          <div className="lp-steps">
            {STEPS.map((s) => (
              <div className="lp-step" key={s.n}>
                <div className="lp-step-num">{s.n}</div>
                <h4>{s.title}</h4>
                <p>{s.body}</p>
              </div>
            ))}
          </div>

          <div className="lp-evidence-note">
            <FileCheck2 size={18} />
            <div>
              <strong>Nothing routes around the record.</strong> Provider, model, tokens,
              cost, and a confidence score are captured for every execution and visible in
              your own History and Analytics — not a vendor's private dashboard.
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="lp-block" id="pricing">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              Pricing
            </div>
            <h2>Priced for what you actually use</h2>
            <p>Start free. Move to Pro when the team needs more room. Talk to us for scale.</p>
          </div>

          <div className="lp-pricing-grid">
            {PLANS.map((plan) => (
              <div className={`lp-price-card${plan.featured ? " featured" : ""}`} key={plan.name}>
                {plan.featured && <div className="lp-price-badge">MOST TEAMS START HERE</div>}
                <div className="lp-price-tag">{plan.tag}</div>
                <h3>{plan.name}</h3>
                <div className="lp-price-value">
                  <strong>{plan.price}</strong>
                  <span>{plan.cadence}</span>
                </div>
                <p style={{ color: "var(--ink-3)", fontSize: 13.5, lineHeight: 1.65, marginBottom: 4 }}>
                  {plan.description}
                </p>
                <ul>
                  {plan.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                {plan.href.startsWith("mailto:") ? (
                  <a href={plan.href} className="lp-btn ghost">
                    {plan.cta} <ArrowRight size={15} />
                  </a>
                ) : (
                  <Link to={plan.href} className={`lp-btn ${plan.featured ? "primary" : "ghost"}`}>
                    {plan.cta} <ArrowRight size={15} />
                  </Link>
                )}
              </div>
            ))}
          </div>

          <div className="lp-trust-strip">
            <span className="dot" />
            Monthly billing. Cancel anytime. No long-term lock-in.
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="lp-final">
        <div className="lp-section">
          <div className="lp-eyebrow" style={{ justifyContent: "center", display: "inline-flex" }}>
            <ShieldCheck size={14} />
            Model policy enforced. Every call logged.
          </div>
          <h2>Put your AI operation on the record.</h2>
          <p>Free plan included, upgrade only when you need more room.</p>
          <div className="lp-hero-ctas">
            <Link to="/signup" className="lp-btn primary">
              Start free <ArrowRight size={16} />
            </Link>
            <Link to="/login" className="lp-btn ghost">
              <Lock size={14} /> Sign in
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

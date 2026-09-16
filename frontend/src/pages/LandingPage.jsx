import { Link } from "react-router-dom";
import {
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  Lock,
  Sparkles,
} from "lucide-react";
import "../styles/Landing.css";

/**
 * Public marketing landing page — /welcome.
 *
 * Presentation only: no data fetching, no auth logic, no new API calls.
 *
 * Grounding for every factual claim below (so copy doesn't drift from the
 * actual product as the backend evolves):
 *  - The 12 skills, categories, names and frameworks mirror the real catalog
 *    in components/startup-copilot/skills.js.
 *  - The "refuses to fabricate" claim mirrors SkillOutputError in
 *    backend/services/startup_copilot_engines.py, which is raised instead of
 *    returning placeholder guidance when a model response can't be parsed
 *    into the skill's output schema.
 *  - The "confidence-scored, itemized findings" claim mirrors the real
 *    output shape in backend/services/startup_copilot_models.py
 *    (e.g. IdeaValidationOutput: verdict, confidence, findings[], next_steps).
 *  - Plan names/prices/limits mirror APP_PLANS in LicensingPage.jsx exactly.
 */

const CATEGORIES = [
  {
    id: "validation",
    title: "Validate",
    blurb: "Confirm the idea is worth pursuing.",
    skills: [{ name: "Idea Validation", fw: "Mom Test" }],
  },
  {
    id: "funding",
    title: "Fund",
    blurb: "Model the business and raise capital.",
    skills: [
      { name: "Business Model", fw: "55 patterns" },
      { name: "Fundraising", fw: "10-slide deck" },
    ],
  },
  {
    id: "execution",
    title: "Execute",
    blurb: "Build, launch, sell, and grow.",
    skills: [
      { name: "Go-to-Market", fw: "PLG vs. sales-led" },
      { name: "Product", fw: "RICE prioritization" },
      { name: "Sales", fw: "MEDDIC / BANT" },
      { name: "Marketing & Brand", fw: "Pillar content" },
      { name: "Growth & Analytics", fw: "AARRR" },
      { name: "Customer Success", fw: "Health scoring" },
    ],
  },
  {
    id: "team",
    title: "Operate",
    blurb: "Staff the company and manage the money.",
    skills: [
      { name: "Operations", fw: "OKRs" },
      { name: "Finance", fw: "Cash flow & runway" },
    ],
  },
  {
    id: "legal",
    title: "Protect",
    blurb: "Entity, equity, and compliance.",
    skills: [{ name: "Legal & Compliance", fw: "Entity & cap table" }],
  },
];

const PAIN_POINTS = [
  { q: "“Is this even worth building?”", a: "Idea Validation" },
  { q: "“Am I raising the right way?”", a: "Fundraising" },
  { q: "“What do I actually say to a customer?”", a: "Sales" },
  { q: "“Am I one bad month from running out of cash?”", a: "Finance" },
];

const STEPS = [
  { n: "01", title: "Ask", body: "Pick a skill. Answer a short, specific form — no prompt engineering." },
  { n: "02", title: "Run", body: "The request goes through an enforced model policy. No silent rerouting." },
  { n: "03", title: "Verify", body: "The response must fit the skill's schema — a verdict, itemized findings, a confidence score." },
  { n: "04", title: "Decide", body: "If it doesn't fit, you get an honest error, not invented guidance. Either way, you decide." },
];

const PLANS = [
  {
    tag: "Try it",
    name: "Free",
    price: "$0",
    cadence: "/month",
    description: "A real workspace to run your first validations before you commit to anything.",
    items: ["100 executions / month", "3 team members", "2 API keys", "5 pipelines"],
    cta: "Start free",
    href: "/signup",
  },
  {
    tag: "Most founders",
    name: "HIC Pro",
    price: "$299",
    cadence: "/month",
    description: "The full Copilot and engine pipeline — for a founder who's past the idea stage.",
    items: ["5,000 executions / month", "10 team members", "All 12 Copilot skills", "Advanced analytics"],
    cta: "Get started",
    href: "/signup",
    featured: true,
  },
  {
    tag: "Scaling up",
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
            Your AI Cofounder
          </div>
          <h1>
            You can build the product alone.
            <br />
            You shouldn't have to <span className="accent">run the company</span> alone.
          </h1>
          <p className="lp-hero-sub">
            Startup Copilot is 12 founder-advisory skills — fundraising, go-to-market, legal,
            finance, and more — each one evidence-backed and confidence-scored. When it isn't
            sure, it says so. It never makes it up.
          </p>
          <div className="lp-hero-ctas">
            <Link to="/signup" className="lp-btn primary" data-testid="lp-hero-cta">
              Meet your Copilot <ArrowRight size={16} />
            </Link>
            <a href="#moat" className="lp-btn ghost">
              See how it stays honest
            </a>
          </div>
          <p className="lp-hero-fineprint">Free plan included. No cofounder equity required.</p>
        </div>
      </section>

      {/* Empathy */}
      <section className="lp-block">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              Sound familiar?
            </div>
            <h2>You're not one founder. You're acting like six.</h2>
            <p>
              You can ship product at midnight. Fundraising, legal, GTM, and finance don't come
              with the same instincts — and there's no cofounder down the hall to sanity-check
              them at 2am.
            </p>
          </div>
          <div className="lp-pain-grid">
            {PAIN_POINTS.map((p) => (
              <div className="lp-pain-card" key={p.q}>
                <p className="lp-pain-q">{p.q}</p>
                <span className="lp-pain-a">→ {p.a} skill has you covered</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Skills — the hero product */}
      <section className="lp-block">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              Your cofounder's skillset
            </div>
            <h2>A whole startup team, on call.</h2>
            <p>
              12 founder-advisory skills, grouped the way a real cofounder would think about your
              company — not a chat window that answers anything about everything.
            </p>
          </div>

          <div className="lp-skill-categories">
            {CATEGORIES.map((cat) => (
              <div className="lp-cat-card" key={cat.id}>
                <div className="lp-cat-head">
                  <h3>{cat.title}</h3>
                  <p>{cat.blurb}</p>
                </div>
                <div className="lp-cat-skills">
                  {cat.skills.map((s) => (
                    <div className="lp-cat-skill" key={s.name}>
                      <span>{s.name}</span>
                      <span className="lp-cat-skill-fw">{s.fw}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The moat: evidence-backed, refuses to fabricate */}
      <section className="lp-block lp-moat" id="moat">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot gold" />
              Why you can trust the answer
            </div>
            <h2>Generic AI makes things up. This one refuses to.</h2>
            <p>
              Ask a chatbot for your LTV/CAC ratio and it will confidently invent one. Startup
              Copilot doesn't. Every skill returns structured, confidence-scored output — a
              verdict, itemized findings, next steps. If the model can't produce something
              reliable, the system raises an honest error instead of a guess.
            </p>
          </div>

          <div className="lp-moat-grid">
            <div className="lp-error-card">
              <div className="lp-error-head">
                <ShieldAlert size={16} />
                SkillOutputError
              </div>
              <p className="lp-error-body">
                A model response could not be parsed into the skill's output schema.
              </p>
              <p className="lp-error-note">
                Raised instead of returning placeholder guidance — a founder acting on invented
                unit economics is worse off than one shown an error.
              </p>
              <div className="lp-error-caption">
                This is a real failure mode built into the system, not a hypothetical.
              </div>
            </div>

            <div className="lp-trust-chips">
              <div className="lp-trust-chip">
                <CheckCircle2 size={18} />
                <div>
                  <strong>Confidence-scored, not vibes-scored</strong>
                  <p>Every verdict ships with a numeric confidence score, not just a tone.</p>
                </div>
              </div>
              <div className="lp-trust-chip">
                <CheckCircle2 size={18} />
                <div>
                  <strong>Itemized findings, not a paragraph</strong>
                  <p>Structured output you can scan and challenge — not a wall of prose.</p>
                </div>
              </div>
              <div className="lp-trust-chip">
                <CheckCircle2 size={18} />
                <div>
                  <strong>Fails closed, never fabricates</strong>
                  <p>An unapproved model or a bad response is rejected, not silently patched over.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="lp-block">
        <div className="lp-section">
          <div className="lp-heading">
            <div className="lp-eyebrow">
              <span className="dot" />
              How it works
            </div>
            <h2>Ask. Run. Verify. Decide.</h2>
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
        </div>
      </section>

      {/* Founder note */}
      <section className="lp-block lp-founder">
        <div className="lp-section">
          <div className="lp-founder-inner">
            <Sparkles size={20} className="lp-founder-icon" />
            <p className="lp-founder-quote">
              "Startup Copilot isn't a chatbot bolted onto a landing page. It's built by an
              operator who needed a cofounder for the parts of running a company that don't come
              with the code — and got tired of asking a generic AI and getting confident-sounding
              nonsense back. If it doesn't know, it says so. That's the whole point."
            </p>
            <div className="lp-founder-label">— Why this exists</div>
          </div>
        </div>
      </section>

      {/* Secondary: license the engine */}
      <section className="lp-block lp-license-strip">
        <div className="lp-section lp-license-inner">
          <div>
            <div className="lp-eyebrow">
              <span className="dot" />
              For larger teams
            </div>
            <h3>Also: license the engine.</h3>
            <p>
              Running a bigger company, or building your own product on proven infrastructure?
              Empire-1 licenses the underlying engine — and the full SLA113 factory platform —
              white-label, under your brand.
            </p>
          </div>
          <a
            href="mailto:founder@empire1.cloud?subject=HIC%20Engine%20License"
            className="lp-btn ghost"
          >
            Talk to us about licensing <ArrowRight size={15} />
          </a>
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
            <h2>Founder-friendly, on purpose</h2>
            <p>Start free. Move to Pro when you're past the idea stage. Talk to us if you're scaling.</p>
          </div>

          <div className="lp-pricing-grid">
            {PLANS.map((plan) => (
              <div className={`lp-price-card${plan.featured ? " featured" : ""}`} key={plan.name}>
                {plan.featured && <div className="lp-price-badge">MOST FOUNDERS START HERE</div>}
                <div className="lp-price-tag">{plan.tag}</div>
                <h3>{plan.name}</h3>
                <div className="lp-price-value">
                  <strong>{plan.price}</strong>
                  <span>{plan.cadence}</span>
                </div>
                <p className="lp-price-desc">{plan.description}</p>
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
            <ShieldAlert size={14} />
            Evidence-backed. Confidence-scored. Never fabricated.
          </div>
          <h2>Stop guessing. Start deciding with backup.</h2>
          <p>Free plan included. Upgrade only when you outgrow it.</p>
          <div className="lp-hero-ctas">
            <Link to="/signup" className="lp-btn primary">
              Meet your Copilot <ArrowRight size={16} />
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

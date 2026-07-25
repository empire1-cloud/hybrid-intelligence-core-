/**
 * Licensing Page — Empire-1 HIC & SLA113 Rate Sheet
 * Cockpit Spec styling
 */

import { Link } from "react-router-dom";

const LicensingPage = () => {
  return (
    <div className="page-container" style={{ maxWidth: 960 }}>
      <div
        className="page-header"
        style={{
          borderBottom: "1px solid var(--border-color)",
          paddingBottom: "1.5rem",
          marginBottom: "2.5rem",
        }}
      >
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "11px",
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--gold)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginBottom: "18px",
          }}
        >
          <span
            style={{
              width: "14px",
              height: "1px",
              background: "var(--gold)",
              display: "inline-block",
            }}
          ></span>
          LICENSING
        </div>
        <h1
          style={{
            fontFamily: "'Barlow Condensed', sans-serif",
            fontWeight: 700,
            fontSize: "clamp(30px, 4.2vw, 46px)",
            lineHeight: 1.05,
            margin: 0,
            textTransform: "uppercase",
          }}
        >
          HIC & SLA113 Rate Sheet
        </h1>
        <p
          style={{
            color: "var(--ink-3)",
            fontSize: "15px",
            lineHeight: 1.7,
            maxWidth: 600,
            marginTop: "12px",
          }}
        >
          Two ways to license the Empire-1 stack. The intelligence core alone,
          or the full factory.
        </p>
      </div>

      {/* OPTION ONE — HIC */}
      <section style={{ marginBottom: "4rem" }}>
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "11px",
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "var(--blue)",
            marginBottom: "18px",
          }}
        >
          OPTION ONE
        </div>

        <h2
          style={{
            fontFamily: "'Barlow Condensed', sans-serif",
            fontWeight: 700,
            fontSize: "32px",
            lineHeight: 1.1,
            margin: "0 0 12px",
            textTransform: "uppercase",
          }}
        >
          Empire-1 HIC
        </h2>
        <p
          style={{
            color: "var(--ink-3)",
            fontSize: "15px",
            lineHeight: 1.7,
            maxWidth: 620,
            marginBottom: "8px",
          }}
        >
          License the intelligence core. Keep your own app.
        </p>
        <p
          style={{
            color: "var(--ink-4)",
            fontSize: "14px",
            lineHeight: 1.7,
            maxWidth: 620,
            marginBottom: "32px",
          }}
        >
          Empire-1 HIC is the standalone intelligence core — routing, canon
          enforcement, a specialized engine set, drift monitoring, and operator
          intelligence. Drop it into your existing product; nothing of ours
          becomes customer-facing.
        </p>
        <p
          style={{
            color: "var(--ink-4)",
            fontSize: "13px",
            fontFamily: "'JetBrains Mono', monospace",
            marginBottom: "28px",
          }}
        >
          Best for: teams with an existing product who want the intelligence
          layer without building it themselves.
        </p>

        {/* HIC Tiers */}
        <div
          style={{
            border: "1px solid var(--border-color)",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "140px 1fr 180px",
              gap: "24px",
              padding: "14px 20px",
              borderBottom: "1px solid var(--border-color)",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "10.5px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--ink-4)",
            }}
          >
            <span>Tier</span>
            <span>Who It's For</span>
            <span style={{ textAlign: "right" }}>Rate</span>
          </div>

          {[
            {
              tier: "Founding Partner",
              who: "First licensees, pre-case-study — early access in exchange for production data and a reference.",
              rate: "$0–$500/mo",
              setup: "or $500–$1,500 setup",
              color: "var(--blue)",
            },
            {
              tier: "Standard",
              who: "Small–mid company, defined monthly request volume.",
              rate: "$1,500–$5,000/mo",
              setup: "or $15K–$50K/yr",
              color: "var(--gold)",
            },
            {
              tier: "Enterprise",
              who: "Larger company, custom routing rules, dedicated support.",
              rate: "$5K–$20K+/mo",
              setup: "or $50K–$250K+/yr",
              color: "var(--gold)",
            },
          ].map((row, i) => (
            <div
              key={i}
              style={{
                display: "grid",
                gridTemplateColumns: "140px 1fr 180px",
                gap: "24px",
                padding: "18px 20px",
                borderBottom:
                  i < 2 ? "1px solid rgba(245,245,247,0.06)" : "none",
                alignItems: "start",
              }}
            >
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: "11.5px",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: row.color,
                  paddingTop: "2px",
                }}
              >
                {row.tier}
              </span>
              <span
                style={{
                  fontSize: "14px",
                  color: "var(--ink-3)",
                  lineHeight: 1.6,
                }}
              >
                {row.who}
              </span>
              <div style={{ textAlign: "right" }}>
                <div
                  style={{
                    fontFamily: "'Barlow Condensed', sans-serif",
                    fontWeight: 700,
                    fontSize: "22px",
                  }}
                >
                  {row.rate}
                </div>
                <div
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: "10.5px",
                    color: "var(--ink-4)",
                    marginTop: "4px",
                  }}
                >
                  {row.setup}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Usage-Based */}
        <div
          style={{
            border: "1px solid var(--border-color)",
            padding: "18px 22px",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "11px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--ink-4)",
              marginBottom: "8px",
            }}
          >
            Usage-Based Alternative
          </div>
          <p
            style={{
              fontSize: "14px",
              color: "var(--ink-3)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Instead of — or alongside — a flat fee: a per-request charge, or a
            15–30% markup over raw model API cost. Best suited to licensees who
            already trust HIC enough to run real production volume through it —
            typically a Standard or Enterprise conversation, not a first deal.
          </p>
        </div>

        <div
          style={{
            borderLeft: "2px solid var(--pink)",
            paddingLeft: "20px",
            marginBottom: "24px",
          }}
        >
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "11px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--pink)",
              margin: "0 0 8px",
            }}
          >
            The Law Applies Here Too
          </p>
          <p
            style={{
              fontSize: "14px",
              color: "var(--ink-3)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Every license exists to prove HIC generates revenue on its own
            terms. Pricing above is a starting point for negotiation, not a
            fixed rate card.
          </p>
        </div>

        <p
          style={{
            fontSize: "12px",
            color: "var(--ink-4)",
            lineHeight: 1.6,
            fontStyle: "italic",
          }}
        >
          Figures are directional estimates based on comparable
          AI-infrastructure licensing patterns, not guarantees or financial
          projections. Empire-1 is not a licensed financial or legal advisor —
          confirm terms with your own counsel before executing any agreement.
        </p>
      </section>

      {/* Divider */}
      <div
        style={{ borderTop: "1px solid var(--border-color)", margin: "4rem 0" }}
      ></div>

      {/* OPTION TWO — SLA113 */}
      <section>
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "11px",
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "var(--pink)",
            marginBottom: "18px",
          }}
        >
          OPTION TWO
        </div>

        <h2
          style={{
            fontFamily: "'Barlow Condensed', sans-serif",
            fontWeight: 700,
            fontSize: "32px",
            lineHeight: 1.1,
            margin: "0 0 12px",
            textTransform: "uppercase",
          }}
        >
          SLA113
        </h2>
        <p
          style={{
            color: "var(--ink-3)",
            fontSize: "15px",
            lineHeight: 1.7,
            maxWidth: 620,
            marginBottom: "8px",
          }}
        >
          License the factory. Mint your own branded platform.
        </p>
        <p
          style={{
            color: "var(--ink-4)",
            fontSize: "14px",
            lineHeight: 1.7,
            maxWidth: 620,
            marginBottom: "12px",
          }}
        >
          SLA113 is the hybrid factory and control plane, built on Empire-1 HIC
          — the system that produces full white-label operating systems,
          platforms, and branded business instances. This isn't hypothetical:
          Southern Lyfestyle, including Southern Arcade OS, is an independent
          experience business running on exactly this factory today.
        </p>
        <p
          style={{
            color: "var(--ink-4)",
            fontSize: "13px",
            fontFamily: "'JetBrains Mono', monospace",
            marginBottom: "16px",
          }}
        >
          Best for: operators launching a new branded platform who want the full
          factory, not just the engine.
        </p>

        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "11px",
            color: "var(--ink-4)",
            lineHeight: 1.8,
            marginBottom: "28px",
          }}
        >
          Included in every SLA113 license — Operator Console · 18+ Specialized
          Engines · Empire-1 HIC · Self-Service Instance Minting
        </div>

        {/* SLA113 Tiers */}
        <div
          style={{
            border: "1px solid var(--border-color)",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "140px 1fr 180px",
              gap: "24px",
              padding: "14px 20px",
              borderBottom: "1px solid var(--border-color)",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "10.5px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--ink-4)",
            }}
          >
            <span>Tier</span>
            <span>Who It's For</span>
            <span style={{ textAlign: "right" }}>Rate</span>
          </div>

          {[
            {
              tier: "Platform Founding Partner",
              who: "First full-platform licensee — discounted for a real production case study and reference.",
              rate: "$1,000–$2,500/mo",
              setup: "or $2K–$5K setup",
              color: "var(--blue)",
            },
            {
              tier: "Platform Standard",
              who: "Operator running one branded instance, standard engine set.",
              rate: "$5,000–$15,000/mo",
              setup: "or $50K–$150K/yr",
              color: "var(--pink)",
            },
            {
              tier: "Platform Enterprise",
              who: "Multi-instance operator, custom engine set, dedicated infrastructure.",
              rate: "$20K+/mo",
              setup: "or $200K+/yr",
              color: "var(--pink)",
            },
          ].map((row, i) => (
            <div
              key={i}
              style={{
                display: "grid",
                gridTemplateColumns: "140px 1fr 180px",
                gap: "24px",
                padding: "18px 20px",
                borderBottom:
                  i < 2 ? "1px solid rgba(245,245,247,0.06)" : "none",
                alignItems: "start",
              }}
            >
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: "11.5px",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: row.color,
                  paddingTop: "2px",
                }}
              >
                {row.tier}
              </span>
              <span
                style={{
                  fontSize: "14px",
                  color: "var(--ink-3)",
                  lineHeight: 1.6,
                }}
              >
                {row.who}
              </span>
              <div style={{ textAlign: "right" }}>
                <div
                  style={{
                    fontFamily: "'Barlow Condensed', sans-serif",
                    fontWeight: 700,
                    fontSize: "22px",
                  }}
                >
                  {row.rate}
                </div>
                <div
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: "10.5px",
                    color: "var(--ink-4)",
                    marginTop: "4px",
                  }}
                >
                  {row.setup}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Why SLA113 Costs More */}
        <div
          style={{
            border: "1px solid var(--border-strong)",
            padding: "22px 24px",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "11px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--ink-4)",
              marginBottom: "12px",
            }}
          >
            Why SLA113 Costs More Than HIC Alone
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
            {[
              "Full operator console — not just an API endpoint to integrate",
              "18+ specialized engines already built, not just routing logic",
              "Self-service white-label minting — spin up new branded instances without touching our team",
              "This is the platform an entire business runs on, not a component inside one",
            ].map((item, i) => (
              <li
                key={i}
                style={{
                  fontSize: "14px",
                  color: "var(--ink-3)",
                  lineHeight: 1.6,
                  padding: "6px 0",
                  paddingLeft: "16px",
                  position: "relative",
                }}
              >
                <span
                  style={{ position: "absolute", left: 0, color: "var(--ok)" }}
                >
                  —
                </span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div
          style={{
            borderLeft: "2px solid var(--pink)",
            paddingLeft: "20px",
            marginBottom: "24px",
          }}
        >
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "11px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--pink)",
              margin: "0 0 8px",
            }}
          >
            The Law Applies Here Too
          </p>
          <p
            style={{
              fontSize: "14px",
              color: "var(--ink-3)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Every license exists to prove the platform generates revenue on its
            own terms. Pricing above is a starting point for negotiation, not a
            fixed rate card.
          </p>
        </div>

        <p
          style={{
            fontSize: "12px",
            color: "var(--ink-4)",
            lineHeight: 1.6,
            fontStyle: "italic",
          }}
        >
          Figures are directional estimates based on comparable
          AI-infrastructure licensing patterns, not guarantees or financial
          projections. Empire-1 is not a licensed financial or legal advisor —
          confirm terms with your own counsel before executing any agreement.
        </p>
      </section>

      {/* Footer */}
      <div
        style={{
          marginTop: "4rem",
          borderTop: "1px solid var(--border-color)",
          paddingTop: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: "10.5px",
          color: "var(--ink-4)",
          letterSpacing: "0.08em",
        }}
      >
        <span>EMPIRE-1 · HIC & SLA113 LICENSING · 2026</span>
        <a
          href="mailto:founder@empire1.cloud"
          style={{ color: "var(--ink-4)", textDecoration: "none" }}
        >
          founder@empire1.cloud
        </a>
      </div>
    </div>
  );
};

export default LicensingPage;

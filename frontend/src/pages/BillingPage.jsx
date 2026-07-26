import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminOnly } from '../components/RoleGate';
import { toast } from 'sonner';
import { PageLoading } from '../components/ui/LoadingState';
import { NoBillingData } from '../components/ui/EmptyState';
import { getErrorMessage } from '../components/ui/ErrorMessage';

const FOUNDER_EMAIL = 'founder@empire1.cloud';

const formatLimit = (value) => value === -1 ? 'Custom' : Number(value || 0).toLocaleString();

const BillingPage = () => {
  const { authAxios, currentTeam } = useAuth();

  const [data, setData] = useState(null);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgradingPlan, setUpgradingPlan] = useState('');
  const [error, setError] = useState('');

  const fetchBillingData = useCallback(async () => {
    if (!currentTeam) return;

    setLoading(true);
    setError('');
    try {
      const [billingRes, plansRes] = await Promise.all([
        authAxios().get('/billing/team'),
        authAxios().get('/billing/plans'),
      ]);

      setData(billingRes.data);
      setPlans(plansRes.data.plans || []);
    } catch (e) {
      console.error('Failed to fetch billing:', e);
      setError(getErrorMessage(e));
      toast.error('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  }, [authAxios, currentTeam]);

  useEffect(() => {
    fetchBillingData();
  }, [fetchBillingData]);

  const handleUpgrade = async (planKey) => {
    setUpgradingPlan(planKey);
    try {
      const res = await authAxios().post('/billing/checkout-session', { plan: planKey });
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      } else {
        toast.info('Stripe checkout is not configured yet.');
      }
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setUpgradingPlan('');
    }
  };

  const handleManageBilling = async () => {
    try {
      const res = await authAxios().post('/billing/portal-session', {});
      if (res.data.portal_url) {
        window.location.href = res.data.portal_url;
      } else {
        toast.info('Stripe billing portal is not configured yet.');
      }
    } catch (e) {
      toast.error(getErrorMessage(e));
    }
  };

  if (loading) {
    return <PageLoading message="Loading billing information..." />;
  }

  if (error || !data) {
    return (
      <div className="page-container" data-testid="billing-error">
        <header className="page-header">
          <h1>Billing & Usage</h1>
          <p className="subtitle">{currentTeam?.name}</p>
        </header>
        <NoBillingData />
      </div>
    );
  }

  const billing = data.billing || {};
  const usage = data.usage || {};
  const usageData = usage.usage || {};
  const usageLimits = usage.limits || billing.limits || {};
  const stripeConfigured = billing.stripe_configured;
  const executionPercent = Math.min(usage.percentages?.executions || 0, 100);

  return (
    <div className="page-container hic-billing" data-testid="billing-page">
      <header className="page-header billing-header">
        <div>
          <div className="billing-eyebrow">HOSTED HIC SUBSCRIPTIONS</div>
          <h1>Billing & Usage</h1>
          <p className="subtitle">{currentTeam?.name}</p>
        </div>
        <div className="no-lockin-badge">
          <span className="status-dot" /> Monthly · Cancel anytime · No lock-in
        </div>
      </header>

      <div className="billing-truth-banner">
        <strong>Your workspace is month-to-month.</strong>
        <span>Cancel before the next renewal and your paid access remains active through the current billing period. HIC licensing, managed partnerships, and SLA113 factory deployments are separate products.</span>
      </div>

      {!stripeConfigured && (
        <div className="mock-mode-banner" data-testid="mock-mode-banner">
          <span className="banner-icon">ℹ️</span>
          <span className="banner-text">
            <strong>Billing setup pending:</strong> Plan details are live, but checkout stays disabled until Stripe price IDs are configured.
          </span>
        </div>
      )}

      <div className="billing-overview-grid">
        <section className="billing-card current-plan-card" data-testid="current-plan">
          <div className="card-kicker">CURRENT PLAN</div>
          <div className="current-plan-row">
            <div>
              <div className="plan-name">{billing.plan_name || 'Free'}</div>
              <div className="plan-price">{billing.price_display || '$0/month'}</div>
            </div>
            <span className={`status-badge ${billing.status === 'active' ? 'badge-success' : ''}`}>
              {billing.cancel_at_period_end ? 'Cancels at period end' : (billing.status || 'Active')}
            </span>
          </div>
          <p className="plan-term">Month-to-month. Cancel anytime from the billing portal.</p>
          {billing.current_period_end && (
            <p className="period-note">Current period ends {new Date(billing.current_period_end).toLocaleDateString()}</p>
          )}
          <AdminOnly>
            {stripeConfigured && billing.plan !== 'free' && (
              <button className="btn-secondary manage-btn" onClick={handleManageBilling}>
                Manage or cancel subscription
              </button>
            )}
          </AdminOnly>
        </section>

        <section className="billing-card usage-card" data-testid="usage-card">
          <div className="card-kicker">CURRENT MONTH</div>
          <div className="usage-number">
            {formatLimit(usageData.executions_count)}
            <span> / {formatLimit(usageLimits.executions_per_month)} executions</span>
          </div>
          <div className="meter-bar">
            <div className="meter-fill" style={{ width: `${executionPercent}%` }} />
          </div>
          <div className="usage-meta">
            <span>{formatLimit(usageData.tokens_used)} tokens tracked</span>
            <span>{formatLimit(usageData.api_calls_count)} API calls</span>
          </div>
          {(usage.percentages?.executions || 0) > 80 && (
            <p className="usage-warning">Approaching the included monthly execution allowance.</p>
          )}
          <p className="overage-note">{billing.overage_note}</p>
        </section>
      </div>

      <AdminOnly>
        <section className="plans-section" data-testid="plans-section">
          <div className="plans-heading">
            <div>
              <div className="billing-eyebrow">CHOOSE YOUR HIC WORKSPACE</div>
              <h2>Simple monthly plans.</h2>
            </div>
            <p>No annual contract is required. Upgrade, downgrade, or cancel as your workload changes.</p>
          </div>

          <div className="plans-grid">
            {plans.map((plan) => {
              const isCurrent = billing.plan === plan.key;
              const isPro = plan.key === 'pro';
              const contactEmail = plan.contact_email || FOUNDER_EMAIL;

              return (
                <article key={plan.key} className={`plan-card ${isPro ? 'featured' : ''}`} data-testid={`plan-${plan.key}`}>
                  {isPro && <div className="featured-label">FOUNDING PRICE</div>}
                  <div className="plan-card-top">
                    <div className="plan-card-name">{plan.name}</div>
                    <div className="plan-card-price">{plan.price_display}</div>
                    <div className="plan-card-term">Monthly · Cancel anytime</div>
                  </div>

                  <p className="plan-description">{plan.description}</p>

                  <div className="plan-limits">
                    <div><strong>{formatLimit(plan.limits?.executions_per_month)}</strong><span>executions / month</span></div>
                    <div><strong>{formatLimit(plan.limits?.team_members)}</strong><span>team members</span></div>
                    <div><strong>{formatLimit(plan.limits?.api_keys)}</strong><span>API keys</span></div>
                    <div><strong>{formatLimit(plan.limits?.pipelines)}</strong><span>pipelines</span></div>
                  </div>

                  <ul className="plan-features">
                    {(plan.features || []).map((feature) => <li key={feature}>— {feature}</li>)}
                  </ul>

                  <p className="plan-overage">{plan.overage_note}</p>

                  <div className="plan-action">
                    {isCurrent ? (
                      <span className="current-plan-badge">Current plan</span>
                    ) : plan.requires_sales ? (
                      <a className="btn-primary plan-button" href={`mailto:${contactEmail}?subject=HIC%20Enterprise%20App`}>
                        Contact the founder
                      </a>
                    ) : plan.purchasable && stripeConfigured ? (
                      <button
                        className="btn-primary plan-button"
                        onClick={() => handleUpgrade(plan.key)}
                        disabled={Boolean(upgradingPlan)}
                      >
                        {upgradingPlan === plan.key ? 'Opening checkout...' : plan.cta}
                      </button>
                    ) : plan.key === 'free' ? (
                      <span className="plan-muted-action">Included automatically</span>
                    ) : (
                      <button className="btn-secondary plan-button" disabled>
                        Checkout setup pending
                      </button>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      </AdminOnly>

      <section className="commercial-paths">
        <div className="commercial-copy">
          <div className="billing-eyebrow">NEED MORE THAN THE HOSTED APP?</div>
          <h2>Subscriptions are not licenses.</h2>
          <p>Use HIC inside this hosted workspace, license the white-label intelligence layer inside your own product, partner with Empire-1 for managed operation, or license the full SLA113 factory.</p>
        </div>
        <a className="btn-secondary" href="/licensing">Compare commercial paths →</a>
      </section>

      <style>{`
        .hic-billing{max-width:1180px}.billing-header{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}.billing-eyebrow{font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}.no-lockin-badge{display:inline-flex;align-items:center;gap:9px;padding:10px 13px;border:1px solid rgba(0,212,170,.25);background:rgba(0,212,170,.06);border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--accent-green)}.status-dot{width:7px;height:7px;border-radius:50%;background:var(--accent-green);box-shadow:0 0 10px rgba(0,212,170,.8)}.billing-truth-banner{display:grid;grid-template-columns:220px 1fr;gap:24px;padding:18px 20px;border-left:2px solid var(--gold);background:rgba(232,185,35,.045);margin-bottom:20px}.billing-truth-banner strong{font-size:14px}.billing-truth-banner span{font-size:13px;color:var(--ink-3);line-height:1.6}.mock-mode-banner{display:flex;align-items:center;gap:.75rem;padding:.85rem 1rem;margin-bottom:1.25rem;background:rgba(77,159,255,.1);border:1px solid rgba(77,159,255,.3);border-radius:8px}.banner-text{font-size:.85rem;color:var(--accent-blue)}.billing-overview-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:42px}.billing-card{border:1px solid var(--border-color);background:var(--panel-bg,rgba(255,255,255,.02));padding:24px}.card-kicker{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.12em;color:var(--ink-4);margin-bottom:18px}.current-plan-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.plan-name{font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:700;text-transform:uppercase}.plan-price{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--gold);margin-top:4px}.plan-term,.period-note,.overage-note{font-size:12.5px;color:var(--ink-4);line-height:1.6}.manage-btn{margin-top:14px}.usage-number{font-family:'Barlow Condensed',sans-serif;font-size:34px;font-weight:700}.usage-number span{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ink-4);font-weight:400}.meter-bar{height:7px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden;margin:16px 0}.meter-fill{height:100%;background:linear-gradient(90deg,var(--gold),var(--accent-green));border-radius:inherit}.usage-meta{display:flex;justify-content:space-between;gap:16px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--ink-4)}.usage-warning{font-size:.8rem;color:var(--accent-orange);margin-top:.75rem}.plans-section{margin-top:26px}.plans-heading{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:24px}.plans-heading h2,.commercial-copy h2{font-family:'Barlow Condensed',sans-serif;font-size:34px;text-transform:uppercase;margin:0}.plans-heading p{max-width:460px;color:var(--ink-3);font-size:13.5px;line-height:1.6}.plans-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.plan-card{position:relative;border:1px solid var(--border-color);padding:24px;background:rgba(255,255,255,.018);display:flex;flex-direction:column}.plan-card.featured{border-color:rgba(232,185,35,.55);background:linear-gradient(180deg,rgba(232,185,35,.055),rgba(255,255,255,.015))}.featured-label{position:absolute;top:0;right:0;background:var(--gold);color:#050505;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;letter-spacing:.1em;padding:7px 9px}.plan-card-name{font-family:'Barlow Condensed',sans-serif;font-size:25px;font-weight:700;text-transform:uppercase}.plan-card-price{font-family:'Barlow Condensed',sans-serif;font-size:31px;font-weight:700;margin-top:10px}.plan-card-term{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--accent-green);margin-top:4px}.plan-description{font-size:13px;color:var(--ink-3);line-height:1.6;min-height:62px}.plan-limits{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border-color);border:1px solid var(--border-color);margin:8px 0 18px}.plan-limits div{background:var(--surface,#0d0d12);padding:12px}.plan-limits strong{display:block;font-family:'Barlow Condensed',sans-serif;font-size:21px}.plan-limits span{display:block;font-family:'JetBrains Mono',monospace;font-size:8.5px;color:var(--ink-4);text-transform:uppercase;margin-top:3px}.plan-features{list-style:none;padding:0;margin:0 0 18px;font-size:12.5px;color:var(--ink-3);line-height:1.7}.plan-overage{font-size:11px;color:var(--ink-4);line-height:1.55;margin-top:auto}.plan-action{margin-top:18px}.plan-button{display:flex;width:100%;justify-content:center;text-decoration:none}.current-plan-badge,.plan-muted-action{display:flex;justify-content:center;padding:11px;border:1px solid rgba(0,212,170,.25);color:var(--accent-green);font-family:'JetBrains Mono',monospace;font-size:10px;text-transform:uppercase}.commercial-paths{display:flex;align-items:center;justify-content:space-between;gap:24px;border-top:1px solid var(--border-color);margin-top:48px;padding:34px 0}.commercial-copy p{max-width:700px;color:var(--ink-3);line-height:1.65;font-size:13.5px}@media(max-width:900px){.plans-grid{grid-template-columns:1fr}.billing-overview-grid{grid-template-columns:1fr}.billing-header,.plans-heading,.commercial-paths{flex-direction:column;align-items:flex-start}.billing-truth-banner{grid-template-columns:1fr}.plan-description{min-height:auto}}@media(max-width:520px){.usage-meta{flex-direction:column}.current-plan-row{flex-direction:column}.no-lockin-badge{border-radius:8px}.plan-limits{grid-template-columns:1fr}}
      `}</style>
    </div>
  );
};

export default BillingPage;

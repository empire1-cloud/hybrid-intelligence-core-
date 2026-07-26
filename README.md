# Hybrid Intelligence Core

Empire-1 HIC is a hosted multi-model intelligence application with 19 specialized engines, Pipeline Composer, execution history, analytics, team workspaces, API keys, usage metering, and Stripe subscription billing.

## Product model

### Use HIC — hosted app subscription

- **Free:** $0/month — 100 executions, 3 team members, 2 API keys, 5 pipelines
- **HIC Pro:** $299/month — 5,000 executions, 10 team members, 10 API keys, 50 pipelines
- **HIC Enterprise App:** starting at $1,500/month — larger negotiated capacity and support

All hosted-app plans are month-to-month. Customers can cancel anytime and retain paid access through the current billing period. Additional usage is agreed before billing; there are no automatic surprise overages.

### Separate commercial paths

- **Revenue Sprint:** $999 one-time
- **Empire Partnership:** starting at $5,000/month
- **HIC white-label license:** starting at $2,500/month, plus deployment-scoped implementation
- **SLA113 factory license:** starting at $7,500/month, plus implementation

A hosted HIC subscription is not a white-label license. Licensing places Empire-1 infrastructure underneath another company’s product. SLA113 licensing provides the full factory and operator platform.

## Model policy

HIC is independent of Google/Gemini APIs. The active execution boundary permits only approved OpenAI and Anthropic model identifiers and fails closed on Gemini, Google, Vertex, or unknown model overrides.

Current approved logical model identifiers:

- `gpt-5.2`
- `gpt-4o`
- `gpt-4o-mini`
- `claude-sonnet-4.5`
- `claude-3-5-sonnet`

## Core features

- 19 specialized AI engines
- Multi-model routing under one policy-controlled voice
- Canon enforcement and format normalization
- Drift monitoring
- Pipeline Composer
- Execution history and analytics
- JWT workspaces and `hic_...` API keys
- Monthly team usage limits
- Stripe checkout, billing portal, and subscription webhooks

## Quick start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

## Required billing configuration

```bash
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
STRIPE_PRO_PRICE_ID=...
# Optional sales-assisted Enterprise price:
STRIPE_ENTERPRISE_PRICE_ID=...
```

Without Stripe configuration, the application displays the plan catalog honestly but disables self-service checkout.

## Deployment requirements

The analytics dashboard uses `psutil` for real system metrics:

```bash
pip install psutil
```

If `psutil` is unavailable, the dashboard displays mock data with a warning indicator.

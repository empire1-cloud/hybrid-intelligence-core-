"""
Billing Service
Handles Stripe integration for month-to-month HIC subscription billing.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List
from bson import ObjectId

logger = logging.getLogger(__name__)

STRIPE_AVAILABLE = False
stripe = None

try:
    import stripe as stripe_module
    stripe = stripe_module
    STRIPE_API_KEY = os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_API_KEY")
    if STRIPE_API_KEY:
        stripe.api_key = STRIPE_API_KEY
        STRIPE_AVAILABLE = True
        logger.info("Stripe billing service initialized")
    else:
        logger.warning("STRIPE_SECRET_KEY not set - billing service disabled")
except ImportError:
    logger.warning("stripe package not installed - billing service disabled")


from database import teams_collection, get_database
from services.audit_service import create_audit_log
from services.email_service import APP_URL


FOUNDER_EMAIL = os.environ.get("FOUNDER_EMAIL", "founder@empire1.cloud")


class BillingError(Exception):
    """Custom exception for billing errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Hosted HIC application subscriptions.
# Licensing, managed partnerships, and SLA113 factory deployments are separate
# commercial paths and are not represented as self-service app plans here.
PLANS = {
    "free": {
        "name": "Free",
        "description": "Explore the HIC workspace with a small monthly execution allowance.",
        "price_id": None,
        "price_display": "$0/month",
        "monthly_price_cents": 0,
        "billing_interval": "month",
        "contract_term": "month_to_month",
        "cancel_anytime": True,
        "requires_sales": False,
        "limits": {
            "executions_per_month": 100,
            "team_members": 3,
            "api_keys": 2,
            "pipelines": 5,
        },
        "features": [
            "Basic HIC engines",
            "Execution history",
            "Community support",
        ],
        "overage_note": "Upgrade when the included monthly allowance is reached.",
        "cta": "Current free plan",
    },
    "pro": {
        "name": "HIC Pro",
        "description": "The complete hosted HIC application for builders and operating teams.",
        "price_id": os.environ.get("STRIPE_PRO_PRICE_ID"),
        "price_display": "$299/month",
        "monthly_price_cents": 29900,
        "billing_interval": "month",
        "contract_term": "month_to_month",
        "cancel_anytime": True,
        "requires_sales": False,
        "limits": {
            "executions_per_month": 5000,
            "team_members": 10,
            "api_keys": 10,
            "pipelines": 50,
        },
        "features": [
            "All approved HIC engines",
            "Pipeline Composer",
            "Advanced analytics and execution history",
            "Team workspace and API keys",
            "Priority support",
        ],
        "overage_note": "Additional usage can be added separately; no automatic surprise overages.",
        "cta": "Start HIC Pro",
    },
    "enterprise": {
        "name": "HIC Enterprise App",
        "description": "A larger hosted HIC workspace with negotiated capacity, governance, and support.",
        "price_id": os.environ.get("STRIPE_ENTERPRISE_PRICE_ID"),
        "price_display": "Starting at $1,500/month",
        "monthly_price_cents": 150000,
        "billing_interval": "month",
        "contract_term": "month_to_month",
        "cancel_anytime": True,
        "requires_sales": True,
        "limits": {
            "executions_per_month": 50000,
            "team_members": 50,
            "api_keys": 50,
            "pipelines": 250,
        },
        "features": [
            "Larger included execution allowance",
            "Advanced governance and analytics",
            "Priority capacity and dedicated support",
            "Custom integrations",
            "Deployment-specific service terms",
        ],
        "overage_note": "Capacity and additional usage are agreed before activation.",
        "cta": "Contact the founder",
    },
}


PUBLIC_PLAN_FIELDS = (
    "name",
    "description",
    "price_display",
    "monthly_price_cents",
    "billing_interval",
    "contract_term",
    "cancel_anytime",
    "requires_sales",
    "limits",
    "features",
    "overage_note",
    "cta",
)


def billing_events_collection():
    """Get billing events collection for webhook history."""
    return get_database().billing_events


def _public_plan(key: str, config: Dict) -> Dict:
    data = {field: config.get(field) for field in PUBLIC_PLAN_FIELDS}
    data.update({
        "key": key,
        "has_price": bool(config.get("price_id")),
        "purchasable": bool(config.get("price_id")) and not config.get("requires_sales", False),
        "contact_email": FOUNDER_EMAIL if config.get("requires_sales") else None,
    })
    return data


async def get_or_create_stripe_customer(team_id: str, owner_email: str, team_name: str) -> str:
    """Get or create a Stripe customer for a team."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if not team:
        raise BillingError("Team not found", 404)

    stripe_customer_id = team.get("billing", {}).get("stripe_customer_id")
    if stripe_customer_id:
        return stripe_customer_id

    customer = stripe.Customer.create(
        email=owner_email,
        name=team_name,
        metadata={
            "team_id": team_id,
            "team_name": team_name,
            "product": "hic_app",
        },
    )

    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {"$set": {
            "billing.stripe_customer_id": customer.id,
            "billing.updated_at": datetime.now(timezone.utc),
        }}
    )

    return customer.id


async def create_checkout_session(
    team_id: str,
    plan: str,
    owner_email: str,
    team_name: str,
    user_id: str,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> Dict:
    """Create a Stripe checkout session for a monthly hosted-app subscription."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    plan_config = PLANS.get(plan)
    if not plan_config:
        raise BillingError(f"Unknown plan: {plan}", 400)

    if plan_config.get("requires_sales"):
        raise BillingError(
            f"{plan_config['name']} is activated with the founder. Contact {FOUNDER_EMAIL}.",
            409,
        )

    price_id = plan_config.get("price_id")
    if not price_id:
        raise BillingError(f"Plan {plan} is not available for purchase", 400)

    customer_id = await get_or_create_stripe_customer(team_id, owner_email, team_name)

    success_url = success_url or f"{APP_URL}/billing?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = cancel_url or f"{APP_URL}/billing?canceled=true"

    metadata = {
        "team_id": team_id,
        "plan": plan,
        "product": "hic_app",
        "contract_term": "month_to_month",
    }

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
        subscription_data={"metadata": metadata},
    )

    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="billing.checkout_created",
        details={
            "plan": plan,
            "session_id": session.id,
            "contract_term": "month_to_month",
        },
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "plan": _public_plan(plan, plan_config),
    }


async def create_portal_session(
    team_id: str,
    owner_email: str,
    team_name: str,
    user_id: str,
    return_url: Optional[str] = None,
) -> Dict:
    """Create a Stripe portal session for plan changes or cancellation."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    customer_id = await get_or_create_stripe_customer(team_id, owner_email, team_name)
    return_url = return_url or f"{APP_URL}/billing"

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )

    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="billing.portal_opened",
        details={"cancel_anytime": True},
    )

    return {
        "portal_url": session.url,
        "cancel_anytime": True,
    }


async def handle_webhook_event(payload: bytes, sig_header: str) -> Dict:
    """Handle Stripe webhook events."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            import json
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        raise BillingError(f"Invalid payload: {str(e)}", 400)
    except stripe.error.SignatureVerificationError as e:
        raise BillingError(f"Invalid signature: {str(e)}", 400)

    event_type = event["type"]
    data = event["data"]["object"]

    await billing_events_collection().insert_one({
        "event_id": event["id"],
        "event_type": event_type,
        "data": dict(data),
        "processed_at": datetime.now(timezone.utc),
    })

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data)
    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data)
    elif event_type == "invoice.paid":
        await handle_invoice_paid(data)
    elif event_type == "invoice.payment_failed":
        await handle_invoice_payment_failed(data)

    return {"received": True, "event_type": event_type}


async def handle_checkout_completed(session: Dict):
    """Handle successful checkout."""
    team_id = session.get("metadata", {}).get("team_id")
    plan = session.get("metadata", {}).get("plan", "pro")
    subscription_id = session.get("subscription")

    if not team_id:
        logger.warning("Checkout completed without team_id in metadata")
        return

    now = datetime.now(timezone.utc)

    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {"$set": {
            "billing.plan": plan,
            "billing.status": "active",
            "billing.subscription_id": subscription_id,
            "billing.contract_term": "month_to_month",
            "billing.cancel_anytime": True,
            "billing.updated_at": now,
        }}
    )

    logger.info(f"Team {team_id} upgraded to {plan}")


async def handle_subscription_created(subscription: Dict):
    """Handle new subscription."""
    customer_id = subscription.get("customer")

    team = await teams_collection().find_one({
        "billing.stripe_customer_id": customer_id
    })

    if not team:
        logger.warning(f"No team found for customer {customer_id}")
        return

    now = datetime.now(timezone.utc)
    period_end = datetime.fromtimestamp(
        subscription.get("current_period_end", 0),
        tz=timezone.utc
    )

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {"$set": {
            "billing.status": subscription.get("status"),
            "billing.subscription_id": subscription.get("id"),
            "billing.current_period_end": period_end,
            "billing.contract_term": "month_to_month",
            "billing.cancel_anytime": True,
            "billing.updated_at": now,
        }}
    )


async def handle_subscription_updated(subscription: Dict):
    """Handle subscription update."""
    customer_id = subscription.get("customer")

    team = await teams_collection().find_one({
        "billing.stripe_customer_id": customer_id
    })

    if not team:
        return

    now = datetime.now(timezone.utc)
    period_end = datetime.fromtimestamp(
        subscription.get("current_period_end", 0),
        tz=timezone.utc
    )

    items = subscription.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id") if items else None

    plan = "free"
    for plan_key, plan_config in PLANS.items():
        if plan_config.get("price_id") == price_id:
            plan = plan_key
            break

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {"$set": {
            "billing.plan": plan,
            "billing.status": subscription.get("status"),
            "billing.current_period_end": period_end,
            "billing.cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "billing.contract_term": "month_to_month",
            "billing.cancel_anytime": True,
            "billing.updated_at": now,
        }}
    )


async def handle_subscription_deleted(subscription: Dict):
    """Handle subscription cancellation and downgrade to Free."""
    customer_id = subscription.get("customer")

    team = await teams_collection().find_one({
        "billing.stripe_customer_id": customer_id
    })

    if not team:
        return

    now = datetime.now(timezone.utc)

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {"$set": {
            "billing.plan": "free",
            "billing.status": "canceled",
            "billing.subscription_id": None,
            "billing.current_period_end": None,
            "billing.cancel_at_period_end": False,
            "billing.updated_at": now,
        }}
    )

    logger.info(f"Team {team['_id']} subscription canceled")


async def handle_invoice_paid(invoice: Dict):
    """Handle successful invoice payment."""
    customer_id = invoice.get("customer")

    team = await teams_collection().find_one({
        "billing.stripe_customer_id": customer_id
    })

    if not team:
        return

    if team.get("billing", {}).get("status") == "past_due":
        await teams_collection().update_one(
            {"_id": team["_id"]},
            {"$set": {
                "billing.status": "active",
                "billing.updated_at": datetime.now(timezone.utc),
            }}
        )


async def handle_invoice_payment_failed(invoice: Dict):
    """Handle failed invoice payment."""
    customer_id = invoice.get("customer")

    team = await teams_collection().find_one({
        "billing.stripe_customer_id": customer_id
    })

    if not team:
        return

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {"$set": {
            "billing.status": "past_due",
            "billing.updated_at": datetime.now(timezone.utc),
        }}
    )

    logger.warning(f"Team {team['_id']} invoice payment failed")


async def get_team_billing(team_id: str) -> Dict:
    """Get billing information for a team."""
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})

    if not team:
        raise BillingError("Team not found", 404)

    billing = team.get("billing", {})
    plan_key = billing.get("plan", "free")
    plan_config = PLANS.get(plan_key, PLANS["free"])

    return {
        "plan": plan_key,
        "plan_name": plan_config["name"],
        "status": billing.get("status", "active"),
        "current_period_end": billing.get("current_period_end"),
        "cancel_at_period_end": billing.get("cancel_at_period_end", False),
        "limits": plan_config["limits"],
        "features": plan_config["features"],
        "price_display": plan_config["price_display"],
        "contract_term": plan_config["contract_term"],
        "cancel_anytime": plan_config["cancel_anytime"],
        "overage_note": plan_config["overage_note"],
        "stripe_configured": STRIPE_AVAILABLE,
    }


def get_plan_limits(plan: str) -> Dict:
    """Get limits for a specific plan."""
    plan_config = PLANS.get(plan, PLANS["free"])
    return plan_config["limits"]


def get_available_plans() -> List[Dict]:
    """Get the public hosted-app subscription catalog."""
    return [_public_plan(key, config) for key, config in PLANS.items()]

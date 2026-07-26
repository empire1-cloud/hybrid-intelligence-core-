"""
Billing Service
Handles Stripe integration for monthly, cancel-anytime subscription billing.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

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


from database import get_database, teams_collection
from services.audit_service import create_audit_log
from services.email_service import APP_URL


class BillingError(Exception):
    """Custom exception for billing errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


PLANS = {
    "free": {
        "name": "Free",
        "display_price": "$0",
        "price_cents": 0,
        "billing_interval": "month",
        "cancel_anytime": True,
        "price_id": None,
        "self_service": True,
        "description": "Explore the HIC app with a real workspace and monthly usage allowance.",
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
    },
    "pro": {
        "name": "HIC Pro",
        "display_price": "$299",
        "price_cents": 29900,
        "billing_interval": "month",
        "cancel_anytime": True,
        "price_id": os.environ.get("STRIPE_PRO_PRICE_ID"),
        "self_service": True,
        "description": "The full hosted HIC app for founders and operating teams.",
        "limits": {
            "executions_per_month": 5000,
            "team_members": 10,
            "api_keys": 10,
            "pipelines": 50,
        },
        "features": [
            "All HIC engines",
            "Pipeline Composer",
            "Advanced analytics",
            "Execution history",
            "Priority support",
        ],
    },
    "enterprise": {
        "name": "HIC Enterprise",
        "display_price": "From $1,500",
        "price_cents": 150000,
        "billing_interval": "month",
        "cancel_anytime": True,
        "price_id": os.environ.get("STRIPE_ENTERPRISE_PRICE_ID"),
        "self_service": False,
        "description": "Hosted HIC for higher-volume teams that need expanded capacity and support.",
        "limits": {
            "executions_per_month": 50000,
            "team_members": 50,
            "api_keys": 50,
            "pipelines": 250,
        },
        "features": [
            "Everything in HIC Pro",
            "Expanded monthly capacity",
            "Priority support",
            "Advanced governance",
            "Deployment-specific integrations",
        ],
    },
}


def billing_events_collection():
    """Get billing events collection for webhook history."""
    return get_database().billing_events


def _timestamp_or_none(timestamp: Optional[int]) -> Optional[datetime]:
    if not timestamp:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def _get_subscription_id(team: Dict) -> str:
    subscription_id = team.get("billing", {}).get("subscription_id")
    if not subscription_id:
        raise BillingError("No active paid subscription found", 400)
    return subscription_id


def _verify_monthly_price(price_id: str) -> None:
    """Fail closed if a configured Stripe price is not monthly recurring."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    price = stripe.Price.retrieve(price_id)
    recurring = getattr(price, "recurring", None)
    interval = recurring.get("interval") if recurring else None
    if interval != "month":
        raise BillingError(
            "Configured Stripe price must be recurring monthly. Annual lock-ins are not supported.",
            500,
        )


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
        },
    )

    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {
            "$set": {
                "billing.stripe_customer_id": customer.id,
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
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
    """Create a monthly Stripe checkout session for a hosted HIC subscription."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    plan_config = PLANS.get(plan)
    if not plan_config:
        raise BillingError(f"Unknown plan: {plan}", 400)
    if plan == "free":
        raise BillingError("The Free plan does not require checkout", 400)
    if not plan_config.get("self_service"):
        raise BillingError(
            f"{plan_config['name']} requires a deployment-scope conversation before activation",
            400,
        )

    price_id = plan_config.get("price_id")
    if not price_id:
        raise BillingError(f"Plan {plan} is not available for purchase", 400)

    _verify_monthly_price(price_id)
    customer_id = await get_or_create_stripe_customer(team_id, owner_email, team_name)

    success_url = success_url or f"{APP_URL}/billing?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = cancel_url or f"{APP_URL}/billing?canceled=true"

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        subscription_data={
            "metadata": {
                "team_id": team_id,
                "plan": plan,
                "billing_policy": "monthly_cancel_anytime",
            }
        },
        metadata={
            "team_id": team_id,
            "plan": plan,
            "billing_policy": "monthly_cancel_anytime",
        },
    )

    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="billing.checkout_created",
        details={
            "plan": plan,
            "session_id": session.id,
            "billing_interval": "month",
            "cancel_anytime": True,
        },
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "billing_interval": "month",
        "cancel_anytime": True,
    }


async def create_portal_session(
    team_id: str,
    owner_email: str,
    team_name: str,
    user_id: str,
    return_url: Optional[str] = None,
) -> Dict:
    """Create a Stripe customer portal session."""
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
    )

    return {"portal_url": session.url}


async def cancel_subscription_at_period_end(team_id: str, user_id: str) -> Dict:
    """Schedule cancellation while preserving access through the paid period."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if not team:
        raise BillingError("Team not found", 404)

    subscription_id = _get_subscription_id(team)
    subscription = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True,
    )
    period_end = _timestamp_or_none(subscription.get("current_period_end"))

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.cancel_at_period_end": True,
                "billing.current_period_end": period_end,
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )

    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="billing.cancellation_scheduled",
        details={
            "subscription_id": subscription_id,
            "current_period_end": period_end.isoformat() if period_end else None,
        },
    )

    return {
        "cancel_at_period_end": True,
        "current_period_end": period_end,
        "message": "Cancellation scheduled. Access remains active through the paid billing period.",
    }


async def resume_subscription(team_id: str, user_id: str) -> Dict:
    """Remove a scheduled cancellation before the current paid period ends."""
    if not STRIPE_AVAILABLE:
        raise BillingError("Billing is not configured", 500)

    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if not team:
        raise BillingError("Team not found", 404)

    subscription_id = _get_subscription_id(team)
    subscription = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=False,
    )
    period_end = _timestamp_or_none(subscription.get("current_period_end"))

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.cancel_at_period_end": False,
                "billing.current_period_end": period_end,
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )

    await create_audit_log(
        user_id=user_id,
        team_id=team_id,
        action="billing.cancellation_reversed",
        details={"subscription_id": subscription_id},
    )

    return {
        "cancel_at_period_end": False,
        "current_period_end": period_end,
        "message": "Subscription will continue month to month.",
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
    except ValueError as exc:
        raise BillingError(f"Invalid payload: {str(exc)}", 400)
    except stripe.error.SignatureVerificationError as exc:
        raise BillingError(f"Invalid signature: {str(exc)}", 400)

    event_type = event["type"]
    data = event["data"]["object"]

    await billing_events_collection().insert_one(
        {
            "event_id": event["id"],
            "event_type": event_type,
            "data": dict(data),
            "processed_at": datetime.now(timezone.utc),
        }
    )

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

    await teams_collection().update_one(
        {"_id": ObjectId(team_id)},
        {
            "$set": {
                "billing.plan": plan,
                "billing.status": "active",
                "billing.subscription_id": subscription_id,
                "billing.cancel_at_period_end": False,
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )

    logger.info("Team %s upgraded to %s", team_id, plan)


async def handle_subscription_created(subscription: Dict):
    """Handle a newly created subscription."""
    customer_id = subscription.get("customer")
    team = await teams_collection().find_one(
        {"billing.stripe_customer_id": customer_id}
    )

    if not team:
        logger.warning("No team found for customer %s", customer_id)
        return

    period_end = _timestamp_or_none(subscription.get("current_period_end"))

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.status": subscription.get("status"),
                "billing.subscription_id": subscription.get("id"),
                "billing.current_period_end": period_end,
                "billing.cancel_at_period_end": bool(subscription.get("cancel_at_period_end")),
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )


async def handle_subscription_updated(subscription: Dict):
    """Handle plan, status, renewal, or cancellation-schedule changes."""
    customer_id = subscription.get("customer")
    team = await teams_collection().find_one(
        {"billing.stripe_customer_id": customer_id}
    )

    if not team:
        return

    period_end = _timestamp_or_none(subscription.get("current_period_end"))
    items = subscription.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id") if items else None

    plan = team.get("billing", {}).get("plan", "free")
    for plan_key, plan_config in PLANS.items():
        if plan_config.get("price_id") == price_id:
            plan = plan_key
            break

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.plan": plan,
                "billing.status": subscription.get("status"),
                "billing.current_period_end": period_end,
                "billing.cancel_at_period_end": bool(subscription.get("cancel_at_period_end")),
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )


async def handle_subscription_deleted(subscription: Dict):
    """Downgrade a team only after the paid subscription has ended."""
    customer_id = subscription.get("customer")
    team = await teams_collection().find_one(
        {"billing.stripe_customer_id": customer_id}
    )

    if not team:
        return

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.plan": "free",
                "billing.status": "canceled",
                "billing.subscription_id": None,
                "billing.current_period_end": None,
                "billing.cancel_at_period_end": False,
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )

    logger.info("Team %s subscription canceled", team["_id"])


async def handle_invoice_paid(invoice: Dict):
    """Handle successful invoice payment."""
    customer_id = invoice.get("customer")
    team = await teams_collection().find_one(
        {"billing.stripe_customer_id": customer_id}
    )

    if not team:
        return

    if team.get("billing", {}).get("status") == "past_due":
        await teams_collection().update_one(
            {"_id": team["_id"]},
            {
                "$set": {
                    "billing.status": "active",
                    "billing.updated_at": datetime.now(timezone.utc),
                }
            },
        )


async def handle_invoice_payment_failed(invoice: Dict):
    """Handle failed invoice payment."""
    customer_id = invoice.get("customer")
    team = await teams_collection().find_one(
        {"billing.stripe_customer_id": customer_id}
    )

    if not team:
        return

    await teams_collection().update_one(
        {"_id": team["_id"]},
        {
            "$set": {
                "billing.status": "past_due",
                "billing.updated_at": datetime.now(timezone.utc),
            }
        },
    )

    logger.warning("Team %s invoice payment failed", team["_id"])


async def get_team_billing(team_id: str) -> Dict:
    """Get billing information and public plan metadata for a team."""
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
        "display_price": plan_config["display_price"],
        "billing_interval": plan_config["billing_interval"],
        "cancel_anytime": plan_config["cancel_anytime"],
        "stripe_configured": STRIPE_AVAILABLE,
    }


def get_plan_limits(plan: str) -> Dict:
    """Get limits for a specific plan."""
    plan_config = PLANS.get(plan, PLANS["free"])
    return plan_config["limits"]


def get_available_plans() -> List[Dict]:
    """Get the hosted HIC subscription catalog."""
    return [
        {
            "key": key,
            "name": config["name"],
            "description": config["description"],
            "display_price": config["display_price"],
            "price_cents": config["price_cents"],
            "billing_interval": config["billing_interval"],
            "cancel_anytime": config["cancel_anytime"],
            "self_service": config["self_service"],
            "limits": config["limits"],
            "features": config["features"],
            "has_price": bool(config.get("price_id")),
        }
        for key, config in PLANS.items()
    ]

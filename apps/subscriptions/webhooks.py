from django.utils import timezone
from subscriptions.services import (
    get_subscription_from_event,
    upgrade_subscription_state
)

EVENT_HANDLERS = {
    "subscription.activated": "ACTIVATE",
    "subscription.charged": "RENEW",
    "subscription.cancelled": "CANCEL",
    "payment.failed": "FAIL",
}

def handle_razorpay_event(event):
    action = EVENT_HANDLERS.get(event.get("event"))

    if not action:
        return
    
    subscription = get_subscription_from_event(event)
    if not subscription:
        return
    
    entity = event["payload"]["subscription"]["entity"]
    period_end = timezone.datetime.fromtimestamp(
        entity.get("current_end"),
        tz=timezone.UTC
    ) if entity.get("current_end") else None

    if action == "RENEW" and subscription.change_type == "DOWNGRADE":
        subscription.plan = subscription.pending_plan
        subscription.pending_plan = None
        subscription.change_type = None
        subscription.save()

    if action in ("ACTIVATE", "RENEW"):
        upgrade_subscription_state(
            subscription,
            status="ACTIVE",
            period_end=period_end,
        )

    elif action == "CANCEL":
        upgrade_subscription_state(
            subscription,
            status="CANCELLED",
        )

    elif action == "FAIL":
        upgrade_subscription_state(
            subscription,
            status="EXPIRED",
        )
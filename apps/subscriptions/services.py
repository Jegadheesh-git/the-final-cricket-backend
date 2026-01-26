from django.utils import timezone
from .razorpay_client import client
from .models import Subscription
from accounts.models import User
from .capabilities import PLAN_CAPABILITIES

def create_razorpay_subscription(*, plan, owner_type, owner_id):
    """
    Create Razorpay subscription and stores DB record (PENDING)
    """

    response = client.subscription.create({
        "plan_id": plan.razorpay_plan_id,
        "total_count": 1 if plan.billing_cycle == "YEARLY" else 12,
        "quantity": 1,
        "customer_notify": 1
    })

    subscription = Subscription.objects.create(
        owner_type = owner_type,
        owner_id = owner_id,
        plan = plan,
        razorpay_subscription_id = response["id"],
        status = "ACTIVE", # TODO -> will be finished via webhook
        current_period_start = timezone.now(),
        current_period_end = None,
    )

    return response, subscription

def has_available_seats(scope):
    """
    Returns True if organization has available user seats
    """

    subscription = scope.subscription
    if not subscription:
        return False
    
    plan_code = subscription.plan.code
    capabilities = PLAN_CAPABILITIES.get(plan_code, {})
    user_limit = capabilities.get("limits",{}).get("users")

    # unlimited seats
    if user_limit is None:
        return True
    
    current_users = User.objects.filter(organization_id = scope.owner_id).count()

    return current_users < user_limit

def get_subscription_from_event(event):
    """
    Extracts razorpay_subscription_id safely and returns subscription
    """

    try:
        razorpay_sub_id = (
            event["payload"]["subscription"]["entity"]["id"]
        )
    except KeyError:
        return None
    
    try:
        return Subscription.objects.get(
            razorpay_subscription_id = razorpay_sub_id
        )
    except Subscription.DoesNotExist:
        return None
    
def upgrade_subscription_state(subscription, *, status, period_end=None):
    """
    Applies subscription state changes safely
    """

    subscription.status = status

    if period_end:
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = period_end

    subscription.save()


def upgrade_subscription(subscription, new_plan):
    """
    Immediate plan change with proration
    """

    client.subscription.update(
        subscription.razorpay_subscription_id,
        {
            "plan_id": new_plan.razorpay_plan_id,
            "schedule_change_at": "now",
        }
    )

    subscription.plan = new_plan
    subscription.change_type ="UPGRADE"
    subscription.pending_plan = None
    subscription.save()

def schedule_downgrade(subscription, new_plan):
    """
    Downgrade at period end
    """

    client.subscription.update(
        subscription.razorpay_subscription_id,
        {
            "plan_id": new_plan.razorpay_plan_id,
            "schedule_change_at": "cycle_end",
        },
    )

    subscription.change_type = "DOWNGRADE"
    subscription.pending_plan = new_plan
    subscription.save()
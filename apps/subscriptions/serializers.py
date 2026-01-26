from rest_framework.serializers import ModelSerializer
from .models import Plan, Subscription

class PlanSerializer(ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            'id',
            'code',
            'name',
            'owner_type',
            'billing_cycle',
            'toolUrl'
        )

class SubscriptionSerializer(ModelSerializer):
    plan = PlanSerializer(read_only=True)
    pending_plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id',
            'plan',
            'status',
            'current_period_start',
            'current_period_end',
            'change_type',
            'pending_plan',
        )
from .models import Plan, Subscription
from .serializers import PlanSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.conf import settings
from django.utils import timezone

#subscription helper services
from .services import create_razorpay_subscription, upgrade_subscription, schedule_downgrade
from subscriptions.webhooks import handle_razorpay_event
import hmac
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class PlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.scope
        plans = Plan.objects.filter(owner_type = scope.owner_type, is_active=True)

        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)

class PlanSelectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        scope = request.scope
        plan_code = request.data.get('plan_code')

        if not plan_code:
            raise ValidationError("Plan code is required")
        
        try:
            plan = Plan.objects.get(code=plan_code, is_active=True)
        except Plan.DoesNotExist:
            raise ValidationError("Plan is either invalid or inactive")
        
        #Owner type validation

        if plan.owner_type != scope.owner_type:
            raise PermissionDenied("Selected plan is invalid for current user")
        
        #Org level permission

        if scope.owner_type == "ORG" and scope.role != "OWNER":
            raise PermissionDenied("Current user cannot select plan for the organisation")
        
        return Response({
            "message": "Plan selection is valid",
            "plan": {
                "code": plan.code,
                "name": plan.name,
                "billing_cycle": plan.billing_cycle,
            }
        })
    
class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        scope = request.scope
        plan_code = request.data.get('plan_code')

        if not plan_code:
            raise ValidationError("Plan code is required")
        
        try:
            plan = Plan.objects.get(code= plan_code, is_active = True)
        except Plan.DoesNotExist:
            raise ValidationError("Plan is either invalid or Inactive")
        
        #validate owner
        if plan.owner_type != scope.owner_type:
            raise ValidationError("Selected plan doesnoot belongs to user owner type")
        
        #validate org owner
        if plan.owner_type == "ORG" and scope.role != "OWNER":
             raise PermissionDenied("You dont have the access. Only owner can create the subscription")

        #Cancel existing subscriptions (Upgrade/downgrade)
        Subscription.objects.filter(
            owner_type = scope.owner_type,
            owner_id = scope.owner_id,
            status = "ACTIVE"
        ).update(status="CANCELLED")

        response, subscription = create_razorpay_subscription(
            plan = plan,
            owner_type = scope.owner_type,
            owner_id = scope.owner_id
        )

        return Response({
            "razorpay_subscription_id": response["id"],
            "razorpay_plan_id": plan.razorpay_plan_id,
            "status": "CREATED"
        })

@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        signature = request.headers.get("X-Razorpay-Signature")

        if not self.verify_signature(payload, signature):
            return Response({"error":"Invalid signature"}, status=400)
        
        event = json.loads(payload)
        handle_razorpay_event(event)

        return Response({"status":"ok"})
    
    def verify_signature(self, payload, signature):
        secret = settings.RAZORPAY_WEBHOOK_SECRET.encode()
        expected_signature = hmac.new(
            secret,
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)
    
    
class ChangePlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        scope = request.scope
        plan_code = request.data.get("plan_code")

        if not plan_code:
            raise ValidationError("plan_code is required")

        subscription = scope.subscription
        if not subscription:
            raise ValidationError("No active subscription")
        
        try:
            new_plan  = Plan.objects.get(code=plan_code, is_active=True)
        except Plan.DoesNotExist:
            raise ValidationError("Invalid plan")
        
        #owner validation
        if new_plan.owner_type != scope.owner_type:
            raise ValidationError("Plan not allowed")
        
        #org permissions
        if scope.owner_type == "ORG" and scope.role != "OWNER":
            raise PermissionDenied("Only owner can change plan")
        
        current_plan = subscription.plan

        if current_plan.billing_cycle != new_plan.billing_cycle:
            raise ValidationError("Billing cycle change not allowed directly")
        
        if new_plan.id == current_plan.id:
            raise ValidationError("Already on the same plan")
        
        if new_plan.billing_cycle == "MONTHLY":
            upgrade_subscription(subscription, new_plan)
            return Response({"status":"UPGRADED"})
        
        schedule_downgrade(subscription, new_plan)
        return Response({"status":"DOWNGRADE_SCHEDULED"})

class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.scope
        subscription = scope.subscription
        
        if not subscription:
            return Response(None)
        
        # We need to manually serialize because scope.subscription might be a cached object or raw model
        from .serializers import SubscriptionSerializer
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
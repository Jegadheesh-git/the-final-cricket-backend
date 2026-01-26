#drf view
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
#permission
from rest_framework.permissions import IsAuthenticated
#exception
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from .models import Organization, OrganizationInvite
from .serializers import OrganizationSerializer, InviteUserSerializer

from subscriptions.services import has_available_seats
from subscriptions.capabilities import PLAN_CAPABILITIES
from accounts.models import User
from backend.core.scope import Scope
from subscriptions.models import Subscription

class OrganizationViewSet(ModelViewSet):

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("Request Scope: ", self.request.scope.owner_type)
        if user.organization:
            return Organization.objects.filter(id=user.organization_id)
        return Organization.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user

        if user.organization:
            raise ValidationError("User already belongs to an organization")
        
        org = serializer.save(created_by=user)
        user.organization = org
        user.role = "OWNER"
        user.save()

class InviteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        #Must belongs to an organisation
        if not user.organization:
            raise PermissionDenied("User does not belongs to any organisation")
        
        #RBAC
        if user.role not in ["OWNER", "ADMIN"]:
            raise PermissionDenied("User not allowed to invite users")
        
        #Check seats
        if not has_available_seats(request.scope):
            raise ValidationError("User seat limit reached for current plan")
        
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite = serializer.save(organization=user.organization)

        # Temp: return token
        # Todo: write send email functionalities

        return Response({
            "message": "Invite created",
            "invite_token": invite.token
        })
    
class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        try:
            invite = OrganizationInvite.objects.get(
                token = token,
                is_used = False
            )
        except OrganizationInvite.DoesNotExist:
            raise ValidationError("Invalid or expired invite")
        
        user = request.user

        # Prevent joining multiple orgs
        if user.organization:
            raise ValidationError("User already belongs to an organization")
        
        # Email must match
        if user.email.lower() != invite.email.lower():
            raise ValidationError("Invite email does not match user")
        
        # Check seats
        # Check seats
        sub = Subscription.objects.filter(
            owner_type="ORG", owner_id=invite.organization.id, status="ACTIVE"
        ).first()
        
        # Temp scope for validation
        org_scope = Scope(
            owner_type="ORG", 
            owner_id=invite.organization.id, 
            role="MEMBER", 
            subscription=sub,
            allow_system_data=True
        )

        if not has_available_seats(org_scope):
            raise ValidationError("No available seats in organization")
        
        # Attach user to org
        user.organization = invite.organization
        user.role = invite.role
        user.save()

        invite.is_used = True
        invite.save()

        return Response({"message":"Joined organization successfully"})
    

class SeatUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.scope

        if scope.owner_type != "ORG":
            return Response({"details":"Not an organization"})
        
        subscription = scope.subscription
        if not subscription:
            return Response({"seats": None})
        
        plan_code = subscription.plan.code
        limits = PLAN_CAPABILITIES.get(plan_code,{}).get("limits", {})
        max_users = limits.get("users")

        used = User.objects.filter(
            organization_id = scope.owner_id
        ).count()

        return Response({
            "used": used,
            "max": max_users,
        })       

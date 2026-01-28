#drf view
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
#permission
from rest_framework.permissions import IsAuthenticated
#exception
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from .models import Organization, OrganizationInvite
from .serializers import OrganizationSerializer, InviteUserSerializer, OrganizationInviteSerializer, OrganizationUserSerializer, AcceptInviteSerializer

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

        # Must belong to organization
        if not user.organization:
            raise PermissionDenied("User does not belong to any organization")

        # RBAC
        if user.role not in ["OWNER", "ADMIN"]:
            raise PermissionDenied("User not allowed to invite users")

        # Seat check
        if not has_available_seats(request.scope):
            raise ValidationError("User seat limit reached for current plan")

        serializer = InviteUserSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        invite = serializer.save()

        return Response(
            {
                "message": "Invite created successfully",
                "invite": {
                    "id": invite.id,
                    "email": invite.email,
                    "role": invite.role,
                    "token": invite.token,
                    "is_used": invite.is_used,
                    "created_at": invite.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    
class AcceptInviteView(APIView):
    authentication_classes = []   # no auth
    permission_classes = []

    def post(self, request):
        serializer = AcceptInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            invite = OrganizationInvite.objects.get(
                token=token,
                is_used=False
            )
        except OrganizationInvite.DoesNotExist:
            raise ValidationError("Invalid or expired invite")

        email = invite.email.lower()

        # User must be new
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists")

        # Seat check
        sub = Subscription.objects.filter(
            owner_type="ORG",
            owner_id=invite.organization.id,
            status="ACTIVE"
        ).first()

        org_scope = Scope(
            owner_type="ORG",
            owner_id=invite.organization.id,
            role=invite.role,
            subscription=sub,
            allow_system_data=True
        )

        if not has_available_seats(org_scope):
            raise ValidationError("No available seats in organization")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            password=serializer.validated_data["password"],
        )

        user.organization = invite.organization
        user.role = invite.role
        user.save()

        invite.is_used = True
        invite.save()

        return Response(
            {
                "message": f"Welcome to {invite.organization.name}, {user.first_name}!"
            },
            status=status.HTTP_201_CREATED,
        )


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


class MyOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. No organization
        if not user.organization:
            return Response(
                {"message": "no organisation found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Permission check
        if user.role == "MEMBER":
            return Response(
                {"message": "you dont have permission to view"},
                status=status.HTTP_403_FORBIDDEN,
            )

        organization = user.organization

        # 3. Users in organization
        users = User.objects.filter(organization=organization)

        # 4. Invites
        invites = organization.invites.all()

        data = {
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "created_at": organization.created_at,
            },
            "stats": {
                "total_users": users.count(),
            },
            "users": OrganizationUserSerializer(users, many=True).data,
            "invites": OrganizationInviteSerializer(invites, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)
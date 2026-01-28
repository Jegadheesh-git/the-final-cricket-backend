from rest_framework import serializers
from .models import Organization, OrganizationInvite
from accounts.models import User

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")

class InviteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvite
        fields = ("email", "role")

    def validate_email(self, value):
        value = value.lower()
        request = self.context["request"]
        organization = request.user.organization

        # User already exists in org
        if User.objects.filter(
            email=value,
            organization=organization
        ).exists():
            raise serializers.ValidationError(
                "User already exists in this organization"
            )

        # Invite already sent & not used
        if OrganizationInvite.objects.filter(
            organization=organization,
            email=value,
            is_used=False
        ).exists():
            raise serializers.ValidationError(
                "Invite already sent to this email"
            )

        return value

    def validate_role(self, value):
        if value not in ["ADMIN", "MEMBER"]:
            raise serializers.ValidationError("Invalid role")
        return value

    def create(self, validated_data):
        request = self.context["request"]

        return OrganizationInvite.objects.create(
            organization=request.user.organization,
            **validated_data
        )

class OrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
        )

class OrganizationInviteSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    accepted_user = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationInvite
        fields = (
            "id",
            "email",
            "role",
            "created_at",
            "status",
            "accepted_user",
        )

    def get_status(self, obj):
        return "ACCEPTED" if obj.is_used else "PENDING"

    def get_accepted_user(self, obj):
        if not obj.is_used:
            return None

        # If invite is accepted, user must exist
        try:
            user = User.objects.get(email=obj.email, organization=obj.organization)
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
            }
        except User.DoesNotExist:
            return None

class AcceptInviteSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data

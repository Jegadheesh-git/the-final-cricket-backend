from rest_framework.serializers import ModelSerializer
from .models import Organization, OrganizationInvite

class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")

class InviteUserSerializer(ModelSerializer):
    class Meta:
        model = OrganizationInvite
        fields = ("email","role")
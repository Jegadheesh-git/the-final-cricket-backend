from rest_framework.viewsets import ModelViewSet
from backend.core.permissions import ScopeRBACPermission, SubscriptionPermission

class BaseScopedModelViewSet(ModelViewSet):
    """
    Base ViewSet for all scoped SAAS models
    """
    permission_classes = [ScopeRBACPermission, SubscriptionPermission]

from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from backend.core.viewsets import BaseScopedModelViewSet

class OwnedModelViewSet(BaseScopedModelViewSet):
    """
    Full CRUD for USER / ORG owned data.
    SYSTEM data is global and read-only.
    """

    def get_queryset(self):
        scope = self.request.scope

        tenant_q = Q(
            owner_type=scope.owner_type,
            owner_id=scope.owner_id
        )

        if scope.allow_system_data:
            system_q = Q(owner_type="SYSTEM")
            return self.queryset.filter(tenant_q | system_q)

        return self.queryset.filter(tenant_q)

    def perform_create(self, serializer):
        scope = self.request.scope
        serializer.save(
            owner_type=scope.owner_type,
            owner_id=scope.owner_id,
            is_locked=False
        )

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.owner_type == "SYSTEM" or obj.is_locked:
            raise PermissionDenied("System data cannot be modified")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner_type == "SYSTEM" or instance.is_locked:
            raise PermissionDenied("System data cannot be deleted")
        instance.delete()

from django.db.models import Q
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from backend.core.permissions import ScopeRBACPermission, SubscriptionPermission

class OwnedModelListView(ListModelMixin, GenericViewSet):
    """
    LIST-only view for USER / ORG + SYSTEM data
    """
    permission_classes = [ScopeRBACPermission, SubscriptionPermission]
    pagination_class = None

    def get_queryset(self):
        scope = self.request.scope

        tenant_q = Q(
            owner_type=scope.owner_type,
            owner_id=scope.owner_id
        )

        if scope.allow_system_data:
            system_q = Q(owner_type="SYSTEM")
            return self.queryset.filter(tenant_q | system_q)

        return self.queryset.filter(tenant_q)

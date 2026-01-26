from rest_framework.viewsets import ModelViewSet
from backend.core.querysets import ScopeQuerySetMixin
from backend.core.permissions import ScopeRBACPermission, SubscriptionPermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

class BaseScopedModelViewSet(ScopeQuerySetMixin, ModelViewSet):
    """
    Base ViewSet for all scoped SAAS models
    """

    permission_classes = [ScopeRBACPermission, SubscriptionPermission]

    def perform_create(self, serializer):
        scope = self.request.scope

        serializer.save(
            owner_type = scope.owner_type,
            owner_id = scope.owner_id,
            created_by = self.request.user
        )

class OwnedModelViewSet(BaseScopedModelViewSet):

    """
    ViewSet for all scoped SAAS models that are owned by the user
    """

    def get_queryset(self):
        scope = self.request.scope

        if scope.allow_system_data:
            return self.queryset.filter(owner_type__in=["SYSTEM", scope.owner_type])
        
        return self.queryset.filter(owner_type=scope.owner_type, owner_id=scope.owner_id)
    
    def perform_create(self, serializer):
        scope = self.request.scope
        serializer.save(owner_type=scope.owner_type, owner_id=scope.owner_id, is_locked=False)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.is_locked:
            raise PermissionDenied("System data cannot be modified")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.is_locked:
            raise PermissionDenied("System data cannot be deleted")
        instance.delete()

class OwnedScopeQuerysetMixin:
    def get_queryset(self):
        scope = self.request.scope

        if scope.allow_system_data:
            return self.queryset.filter(
                owner_type__in=["SYSTEM", scope.owner_type]
            )

        return self.queryset.filter(
            owner_type=scope.owner_type,
            owner_id=scope.owner_id
        )

class OwnedModelListView(
    OwnedScopeQuerysetMixin,
    ScopeQuerySetMixin,
    ListModelMixin,
    GenericViewSet
):
    """
    Scoped LIST-only ViewSet
    """

    permission_classes = [ScopeRBACPermission, SubscriptionPermission]
    pagination_class = None
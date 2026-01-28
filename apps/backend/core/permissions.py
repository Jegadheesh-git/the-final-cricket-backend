from rest_framework.permissions import BasePermission, SAFE_METHODS
from subscriptions.capabilities import PLAN_CAPABILITIES


class ScopeRBACPermission(BasePermission):
    """
    Enforce Role based permissions within a scope
    """

    def has_permission(self, request, view):
        scope = getattr(request, "scope", None)

        if scope is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if scope.owner_type == "USER":
            return True

        return scope.role in ["OWNER", "ADMIN"]

    def has_object_permission(self, request, view, obj):
        scope = request.scope

        # SYSTEM data → read-only for everyone
        if obj.owner_type == "SYSTEM":
            return request.method in SAFE_METHODS

        # ORG / USER → must match scope exactly
        return (
            obj.owner_type == scope.owner_type
            and obj.owner_id == scope.owner_id
        )


class SubscriptionPermission(BasePermission):

    def has_permission(self, request, view):
        scope = request.scope

        # No subscription → allow reads only
        if not scope.subscription:
            return request.method in SAFE_METHODS

        if not scope.subscription.is_active():
            return False

        plan_code = scope.subscription.plan.code
        capabilities = PLAN_CAPABILITIES.get(plan_code, {})

        # Stadium creation limit
        if request.method == "POST" and view.basename == "stadium":
            limit = capabilities.get("limits", {}).get("stadiums")

            if limit is None:
                return True
            """
            count = Stadium.objects.filter(
                owner_type=scope.owner_type,
                owner_id=scope.owner_id
            ).count()

            return count < limit
            """

        return True

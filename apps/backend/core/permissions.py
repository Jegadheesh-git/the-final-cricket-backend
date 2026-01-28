from rest_framework.permissions import BasePermission, SAFE_METHODS
from subscriptions.capabilities import PLAN_CAPABILITIES
from stadium.models import Stadium

class ScopeRBACPermission(BasePermission):
    """
    Enforce Role based permissions within a scope
    """

    def has_permission(self, request, view):
        # ✅ Allow preflight
        if request.method == "OPTIONS":
            return True
        
        scope = getattr(request, "scope", None)

        if scope is None:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        if scope.owner_type == "USER":
            return True
        
        return scope.role in ["OWNER", "ADMIN"]
    

class SubscriptionPermission(BasePermission):
    def has_permission(self, request, view):

        if request.method == "OPTIONS":
            return True
        
        scope = request.scope

        # No subscription -> block writes
        if not scope.subscription:
            return request.method in ('GET',)

        if not scope.subscription.is_active():
            return False

        plan_code = scope.subscription.plan.code
        capabilities = PLAN_CAPABILITIES.get(plan_code, {}) 

        #stadium creation limit
        if request.method == "POST" and view.basename == "stadium":
            limit = capabilities.get("limits",{}).get("stadiums")

            if limit is None:
                return True
            
            count = Stadium.objects.filter(
                owner_type = scope.owner_type,
                owner_id = scope.owner_id
            ).count()

            return count < limit
        
        return True
from .scope import Scope
from subscriptions.models import Subscription

class ScopeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        
        request.scope = None

        if user.is_authenticated:
            if user.organization_id:

                subscription = Subscription.objects.filter(
                    owner_type = "ORG",
                    owner_id = user.organization.id,
                    status = "ACTIVE"
                ).first()

                request.scope = Scope(
                    owner_type = "ORG",
                    owner_id=user.organization_id,
                    role = user.role,
                    subscription = subscription,
                    allow_system_data=user.organization.allow_system_data,
                )

            else:
                subscription = Subscription.objects.filter(
                    owner_type = "USER",
                    owner_id = user.id,
                    status = "ACTIVE"
                ).first()

                request.scope = Scope(
                    owner_type="USER",
                    owner_id=user.id,
                    role = "OWNER",
                    subscription = subscription,
                    allow_system_data=user.allow_system_data,
                )

        return self.get_response(request)
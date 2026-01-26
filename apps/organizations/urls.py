from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, InviteUserView, AcceptInviteView
from django.urls import path

urlpatterns = [
    path("organizations/invite/", InviteUserView.as_view()),
    path("organizations/invite/accept/", AcceptInviteView.as_view()),
]

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")

urlpatterns += router.urls


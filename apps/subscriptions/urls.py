from django.urls import path
from .views import PlanListView, PlanSelectView, CreateSubscriptionView, RazorpayWebhookView, MySubscriptionView

urlpatterns = [
    path("plans/", PlanListView.as_view()),
    path("plans/select/", PlanSelectView.as_view()),
    path("plans/me/", MySubscriptionView.as_view()),
    path("create/", CreateSubscriptionView.as_view()),
    path("razorpay/webhook/", RazorpayWebhookView.as_view()),
]
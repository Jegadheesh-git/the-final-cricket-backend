from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from subscriptions.models import Plan
from accounts.models import User

class SubscriptionViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")
        self.client.force_login(self.user)
        self.plan = Plan.objects.create(name="Pro", code="PRO", owner_type="USER", billing_cycle="MONTHLY", razorpay_plan_id="p_1")

    def test_list_plans(self):
        res = self.client.get("/api/subscriptions/plans/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch("subscriptions.services.client.subscription.create")
    def test_create_subscription(self, mock_create):
        # View calls create_razorpay_subscription -> client.subscription.create
        mock_create.return_value = {"id": "sub_123"}
        
        data = {"plan_code": "PRO"}
        res = self.client.post("/api/subscriptions/create/", data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["razorpay_subscription_id"], "sub_123")

    @patch("subscriptions.views.RazorpayWebhookView.verify_signature")
    @patch("subscriptions.views.handle_razorpay_event")
    def test_webhook(self, mock_handle, mock_verify):
        mock_verify.return_value = True
        
        data = {"payload": "dummy"}
        res = self.client.post("/api/subscriptions/razorpay/webhook/", data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_handle.assert_called() 

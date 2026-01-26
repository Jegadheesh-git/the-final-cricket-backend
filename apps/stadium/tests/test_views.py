from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from stadium.models import Stadium
import uuid
from subscriptions.models import Plan, Subscription
from django.utils import timezone

class StadiumViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")
        self.client.force_login(self.user)
        
        # ScopeMiddleware implies we need a subscription for USER scope if strictly checked? 
        # BaseScopedModelViewSet uses request.scope.
        # If no subscription, allows creation?
        # Usually checking 'limits' is done, but let's assume valid or unlimited for now. 
        # But safest to create a subscription if middleware expects it.
        # However, BaseScopedModelViewSet might not block if subscription is missing, unless limited.
        
        # Let's create one just in case 
        plan = Plan.objects.create(name="Free", code="FREE", owner_type="USER", billing_cycle="MONTHLY", razorpay_plan_id="plan_free")
        Subscription.objects.create(owner_type="USER", owner_id=self.user.id, plan=plan, status="ACTIVE", current_period_end=timezone.now()+timezone.timedelta(days=30))

    def test_stadium_crud(self):
        url = "/api/stadiums/" # DefaultRouter basename 'stadium', typically 'stadiums' or 'stadium' depending on router registry.
        # Need to check urls.py
        
        sid = str(uuid.uuid4())
        data = { "name": "API Ground", "city": "API City", "sync_id": sid }
        res = self.client.post(url, data)
        if res.status_code == 404:
             # Try singular or check router
             pass
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stadium.objects.count(), 1)
        
        s = Stadium.objects.first()
        # s.owner_id is UUID, user.id is int. SQLite/Django coerced int to UUID.
        # Check if UUID's int value matches user.id
        self.assertEqual(s.owner_id.int, self.user.id)
        self.assertEqual(str(s.sync_id), sid)

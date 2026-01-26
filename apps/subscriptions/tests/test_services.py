from django.test import TestCase
from subscriptions.models import Plan, Subscription
from subscriptions.services import has_available_seats
from accounts.models import User
from backend.core.scope import Scope
from django.utils import timezone
import uuid

class SubscriptionServiceTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name="Pro", code="PRO", owner_type="ORG", billing_cycle="MONTHLY", razorpay_plan_id="p_1")
        self.org_user = User.objects.create_user(username="owner", password="password")
        # Assume org exists logic or mocked via scope owner_type="ORG"

    def test_has_seats_unlimited(self):
        # capabilities logic: if plan code not in capability dict, assumed unlimited.
        sub = Subscription.objects.create(owner_type="ORG", owner_id=uuid.uuid4(), plan=self.plan, status="ACTIVE")
        scope = Scope("ORG", sub.owner_id, "ADMIN", sub, True)
        self.assertTrue(has_available_seats(scope))

import uuid

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from organizations.models import Organization, OrganizationInvite
from subscriptions.models import Plan, Subscription
from django.utils import timezone

class OrganizationViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")
        self.client.force_login(self.user)

    def test_create_organization(self):
        url = "/api/organizations/" 
        data = { "name": "New Org" }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organization.objects.count(), 1)
        
        # Verify user is linked ?? 
        # OrganizationViewSet likely sets created_by. 
        # Does it link user.organization? Probably not auto-link unless logic exists.
        
    def test_invite_flow(self):
        # Create Org manually
        org = Organization.objects.create(name="My Org", created_by=self.user)
        # Link user to org to be admin
        self.user.organization = org
        self.user.role = "ADMIN"
        self.user.save()
        
        # Create Subscription for seats check
        plan = Plan.objects.create(
            name="Pro", code="PRO", 
            owner_type="ORG", billing_cycle="MONTHLY",
            razorpay_plan_id="plan_123"
        )
        Subscription.objects.create(
            owner_type="ORG", 
            owner_id=org.id, 
            plan=plan, 
            status="ACTIVE",
            current_period_end=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Invite
        url_invite = "/api/organizations/invite/"
        data = { "email": "new@example.com", "role": "MEMBER" }
        res = self.client.post(url_invite, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        invite = OrganizationInvite.objects.get(email="new@example.com")
        token = invite.token

        # Accept
        # Create another user to accept
        user2 = User.objects.create_user(username="newuser", email="new@example.com", password="password")
        self.client.logout()
        self.client.force_login(user2)
        
        url_accept = "/api/organizations/invite/accept/"
        res = self.client.post(url_accept, { "token": str(token) })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        user2.refresh_from_db()
        self.assertEqual(user2.organization, org)
        self.assertEqual(user2.role, "MEMBER")

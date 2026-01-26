from django.test import TestCase
from organizations.models import Organization, OrganizationInvite
from accounts.models import User
import uuid

class OrganizationModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")

    def test_create_organization(self):
        org = Organization.objects.create(name="My Org", created_by=self.user)
        self.assertEqual(org.name, "My Org")
        self.assertEqual(org.created_by, self.user)

    def test_create_invite(self):
        org = Organization.objects.create(name="My Org", created_by=self.user)
        invite = OrganizationInvite.objects.create(
            organization=org, email="test@example.com", role="MEMBER"
        )
        self.assertIsNotNone(invite.token)
        self.assertFalse(invite.is_used)

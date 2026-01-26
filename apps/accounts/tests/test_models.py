from django.test import TestCase
from accounts.models import User, Device
from organizations.models import Organization
from coredata.models import Nationality

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="password123")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.role, "OWNER") # Default
        self.assertTrue(user.allow_system_data) # Default

    def test_user_organization_link(self):
        # Organization needs created_by
        creator = User.objects.create_user(username="creator", password="pwd")
        org = Organization.objects.create(name="Test Org", created_by=creator)
        
        user = User.objects.create_user(username="orguser", password="pwd", organization=org)
        
        self.assertEqual(user.organization, org)

class DeviceModelTest(TestCase):
    def test_device_creation(self):
        device_id = "550e8400-e29b-41d4-a716-446655440000"
        device = Device.objects.create(
            id=device_id,
            owner_type="USER",
            owner_id=device_id, # arbitrary uuid for owner
            device_name="Test PC",
            device_type="DESKTOP"
        )
        self.assertTrue(device.is_active)
        self.assertEqual(device.device_type, "DESKTOP")

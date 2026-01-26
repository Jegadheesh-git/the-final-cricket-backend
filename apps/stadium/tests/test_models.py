from django.test import TestCase
from stadium.models import Stadium
from accounts.models import User
import uuid

class StadiumModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="password")

    def test_create_stadium(self):
        sid = uuid.uuid4()
        s = Stadium.objects.create(
            name="Ground 1", city="City", 
            owner_type="USER", owner_id=self.user.id,
            sync_id=sid
        )
        self.assertEqual(s.name, "Ground 1")
        self.assertEqual(s.sync_id, sid)

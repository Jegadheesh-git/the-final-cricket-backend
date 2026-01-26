from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from coredata.models import Nationality, Team
from accounts.models import User
from subscriptions.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta

class CoreDataViewsTest(APITestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Free Plan", 
            code="FREE",
            owner_type="USER",
            billing_cycle="MONTHLY",
            razorpay_plan_id="plan_12345"
        )
        self.user = User.objects.create_user(username="testadmin", password="password")
        self.sub = Subscription.objects.create(
            owner_type="USER",
            owner_id=self.user.id,
            plan=self.plan,
            status="ACTIVE",
            current_period_end=timezone.now() + timedelta(days=30)
        )
        self.client.force_login(self.user)
        self.nat = Nationality.objects.create(name="TestLand", code="TL")
        
    def test_list_nationalities(self):
        url = reverse('nationality') # name="nationality" in urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'TL')

    def test_create_team(self):
        url = reverse('team-list') # Standard router name
        data = {
            "name": "Test Team",
            "short_name": "TT",
            "team_type": "DOMESTIC",
            "nationality": self.nat.id
        }
        response = self.client.post(url, data)
        if response.status_code != 201:
            print(response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.get().name, "Test Team")

    def test_get_team_detail(self):
        team = Team.objects.create(name="Existing Team", short_name="ET", team_type="LEAGUE")
        url = reverse('team-detail', args=[team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Existing Team")

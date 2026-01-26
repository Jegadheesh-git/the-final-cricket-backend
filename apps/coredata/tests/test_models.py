from django.test import TestCase
from coredata.models import Nationality, Player, Team, Stadium
from datetime import date

class CoreDataModelsTest(TestCase):
    def setUp(self):
        self.nat = Nationality.objects.create(name="CricketLand", code="CKL")

    def test_nationality_str(self):
        self.assertEqual(str(self.nat), "CricketLand - CKL")

    def test_player_creation(self):
        player = Player.objects.create(
            first_name="John",
            last_name="Doe",
            nationality=self.nat,
            gender="MALE",
            batting_hand="RIGHT",
            bowling_hand="RIGHT",
            role="ALL_ROUNDER",
            date_of_birth=date(1990, 1, 1)
        )
        self.assertEqual(str(player), "Doe, John - CricketLand - CKL")
        self.assertTrue(player.is_locked) # Default for OwnedModel

    def test_team_creation(self):
        team = Team.objects.create(
            name="Super Kings",
            short_name="SK",
            team_type="LEAGUE",
            nationality=self.nat
        )
        self.assertEqual(str(team), "Super Kings")

    def test_stadium_creation(self):
        stadium = Stadium.objects.create(
            name="Grand Arena",
            city="Metropolis",
            nationality=self.nat
        )
        self.assertEqual(str(stadium), "Grand Arena, Metropolis - CricketLand - CKL")

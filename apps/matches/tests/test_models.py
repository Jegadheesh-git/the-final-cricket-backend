from django.test import TestCase
from django.core.exceptions import ValidationError
from matches.models import Match, MatchType, PlayingXI
from coredata.models import Nationality, Team, Player
from competitions.models import Series

class MatchModelTest(TestCase):
    def setUp(self):
        self.nat = Nationality.objects.create(name="MatchLand", code="ML")
        self.team1 = Team.objects.create(name="Team A", team_type="DOMESTIC", nationality=self.nat)
        self.team2 = Team.objects.create(name="Team B", team_type="DOMESTIC", nationality=self.nat)
        self.mtype = MatchType.objects.create(name="T20", code="T20", max_overs=20)
        self.series = Series.objects.create(
            name="Test Series", 
            owner_type="SYSTEM",
            series_type="BILATERAL"
        )

    def test_match_validation_teams(self):
        match = Match(
            series=self.series,
            match_type=self.mtype,
            team1=self.team1,
            team2=self.team1 # Same team
        )
        with self.assertRaises(ValidationError):
            match.full_clean()

    def test_match_creation_success(self):
        match = Match.objects.create(
            series=self.series,
            match_type=self.mtype,
            team1=self.team1,
            team2=self.team2
        )
        self.assertEqual(match.state, "DRAFT")

class MatchTypeTest(TestCase):
    def test_properties(self):
        mt = MatchType(code="TEST", name="Test Match")
        self.assertTrue(mt.is_test)
        self.assertTrue(mt.follow_on_allowed)

        mt2 = MatchType(code="T20", name="T20")
        self.assertFalse(mt2.is_test)
        self.assertFalse(mt2.follow_on_allowed)

from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from accounts.models import User
from coredata.models import Nationality, Team, Player
from competitions.models import Tournament, Competition, Series, CompetitionTeam, CompetitionSquad, SeriesTeam, SeriesSquad
import datetime

class CompetitionModelsTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testowner", password="password")
        self.nat = Nationality.objects.create(name="TestLand", code="TL")
        self.team1 = Team.objects.create(name="Team A", team_type="DOMESTIC", nationality=self.nat)
        self.player1 = Player.objects.create(
            first_name="John", last_name="Doe", nationality=self.nat, 
            gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER"
        )

    def test_tournament_creation(self):
        """Test valid tournament creation"""
        tourney = Tournament.objects.create(
            name="Test Tourney", 
            tournament_type="LEAGUE", 
            nationality=self.nat,
            owner_type="USER",
            owner_id=self.user.id
        )
        self.assertEqual(tourney.name, "Test Tourney")
        self.assertTrue(tourney.is_active)

    def test_competition_creation(self):
        """Test competition linking to tournament"""
        tourney = Tournament.objects.create(
            name="T1", tournament_type="LEAGUE", owner_type="USER", owner_id=self.user.id
        )
        comp = Competition.objects.create(
            name="C1", tournament=tourney, 
            start_date=datetime.date.today(),
            owner_type="USER", owner_id=self.user.id
        )
        self.assertEqual(comp.tournament, tourney)
        self.assertFalse(comp.is_locked)

    def test_series_creation(self):
        """Test series creation independent of tournament"""
        series = Series.objects.create(
            name="Bilateral Series",
            series_type="BILATERAL",
            owner_type="USER",
            owner_id=self.user.id
        )
        self.assertEqual(series.series_type, "BILATERAL")
        self.assertEqual(series.owner_id, self.user.id)

    def test_competition_squad_constraints(self):
        """Test linking teams and players to competition"""
        tourney = Tournament.objects.create(name="T2", tournament_type="LEAGUE", owner_type="USER", owner_id=self.user.id)
        comp = Competition.objects.create(name="C2", tournament=tourney, owner_type="USER", owner_id=self.user.id)
        
        # Add Team
        ct = CompetitionTeam.objects.create(competition=comp, team=self.team1)
        self.assertEqual(ct.team, self.team1)
        
        # Duplicate Team should fail
        with self.assertRaises(IntegrityError):
             CompetitionTeam.objects.create(competition=comp, team=self.team1)
            
        # Add Player to Squad
        cs = CompetitionSquad.objects.create(competition_team=ct, player=self.player1)
        self.assertEqual(cs.player, self.player1)
        
        # Duplicate Player in Squad should fail
        with self.assertRaises(IntegrityError):
             CompetitionSquad.objects.create(competition_team=ct, player=self.player1)

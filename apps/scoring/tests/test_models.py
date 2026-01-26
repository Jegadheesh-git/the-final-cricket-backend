from django.test import TestCase
from competitions.models import Tournament, Competition
from matches.models import Match, Innings, Toss, MatchType
from scoring.models import Ball, InningsAggregate, BatterStats, BowlerStats
from coredata.models import Nationality, Team, Player
from accounts.models import User
from django.utils import timezone

class ScoringModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="scorer", password="password")
        self.nat = Nationality.objects.create(name="ScoringLand", code="SL")
        self.team1 = Team.objects.create(name="S Team 1", team_type="LEAGUE", nationality=self.nat)
        self.team2 = Team.objects.create(name="S Team 2", team_type="LEAGUE", nationality=self.nat)
        
        self.tourney = Tournament.objects.create(name="S T", tournament_type="LEAGUE", owner_type="USER", owner_id=self.user.id)
        self.comp = Competition.objects.create(name="S C", tournament=self.tourney, owner_type="USER", owner_id=self.user.id)
        self.mtype = MatchType.objects.create(name="T20", code="T20", max_overs=20)
        
        self.match = Match.objects.create(
            competition=self.comp, match_type=self.mtype,
            team1=self.team1, team2=self.team2, 
            state="IN_PROGRESS", match_mode="ONLINE"
        )
        self.toss = Toss.objects.create(match=self.match, won_by_id=self.team1.id, decision="BAT")
        self.innings = Innings.objects.create(
            match=self.match, batting_team_id=self.team1.id, bowling_team_id=self.team2.id, innings_number=1
        )
        
        self.batter = Player.objects.create(first_name="B1", last_name="Bat", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER")
        self.bowler = Player.objects.create(first_name="B2", last_name="Bowl", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BOWLER")

    def test_ball_creation(self):
        # Create non-striker for validity
        non_striker = Player.objects.create(first_name="NS", last_name="NS", nationality=self.nat)
        ball = Ball.objects.create(
            user=self.user,
            match=self.match,
            innings=self.innings,
            over_number=0,
            ball_number=1,
            ball_in_over=1,
            striker=self.batter,
            non_striker=non_striker,
            bowler=self.bowler,
            batting_team=self.team1,
            bowling_team=self.team2,
            runs_off_bat=4
        )
        self.assertEqual(ball.runs_off_bat, 4)
        self.assertEqual(ball.over_number, 0)

    def test_stats_creation(self):
        b_stats = BatterStats.objects.create(
            innings=self.innings, player=self.batter, runs=10, balls=5
        )
        sr = (b_stats.runs / b_stats.balls) * 100
        self.assertEqual(sr, 200.0)

        bw_stats = BowlerStats.objects.create(
            innings=self.innings, player=self.bowler, runs_conceded=12, balls=6, wickets=1
        )
        eco = (bw_stats.runs_conceded / bw_stats.balls) * 6
        self.assertEqual(eco, 12.0)

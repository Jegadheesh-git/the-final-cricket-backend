from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from matches.models import Match, Innings, Toss, PlayingXI, MatchType
from competitions.models import Tournament, Competition
from coredata.models import Nationality, Team, Player
from subscriptions.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta

class ScoringViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="scorer_v", password="password")
        self.plan = Plan.objects.create(name="Pro", code="PRO", owner_type="USER", billing_cycle="MONTHLY")
        Subscription.objects.create(
            owner_type="USER", owner_id=self.user.id, plan=self.plan, status="ACTIVE",
            current_period_end=timezone.now() + timedelta(days=30)
        )
        self.client.force_login(self.user)
        
        self.nat = Nationality.objects.create(name="Land", code="LD")
        self.team1 = Team.objects.create(name="T1", team_type="LEAGUE", nationality=self.nat)
        self.team2 = Team.objects.create(name="T2", team_type="LEAGUE", nationality=self.nat)

        self.tourney = Tournament.objects.create(name="S T", tournament_type="LEAGUE", owner_type="USER", owner_id=self.user.id)
        self.comp = Competition.objects.create(name="S C", tournament=self.tourney, owner_type="USER", owner_id=self.user.id)
        self.mtype = MatchType.objects.create(name="T20", code="T20", max_overs=20)
        
        self.match = Match.objects.create(
            competition=self.comp, match_type=self.mtype,
            team1=self.team1, team2=self.team2, 
            state="READY",
            match_mode="ONLINE"
        )
        self.toss = Toss.objects.create(match=self.match, won_by_id=self.team1.id, decision="BAT")
        
        # Players
        self.p1 = Player.objects.create(first_name="Str", last_name="Ker", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER")
        self.p2 = Player.objects.create(first_name="Non", last_name="Str", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER")
        self.b1 = Player.objects.create(first_name="Bwl", last_name="Er", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BOWLER")

        # Playing XI
        PlayingXI.objects.create(match=self.match, team_id=self.team1.id, player=self.p1, batting_position=1)
        PlayingXI.objects.create(match=self.match, team_id=self.team1.id, player=self.p2, batting_position=2)
        PlayingXI.objects.create(match=self.match, team_id=self.team2.id, player=self.b1, batting_position=1)

    def test_start_session_and_scoring(self):
        # 1. Start Innings
        url = f"/api/matches/matches/{self.match.id}/innings/"
        data = { "batting_team": self.team1.id }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        innings_number = res.data['innings_number']
        
        # Refresh match state
        self.match.refresh_from_db()
        self.assertEqual(self.match.state, "IN_PROGRESS")
        
        # 2. Setup Innings (Session Init)
        url_setup = reverse('setup_innings', args=[innings_number])  # Assuming logic uses ID not number, checking URLs
        # Actually URLs use `innings_id`. args should use ID.
        innings_obj = Innings.objects.get(match=self.match, innings_number=innings_number)
        url_setup = reverse('setup_innings', args=[innings_obj.id])
        
        data_setup = {
            "striker": self.p1.id,
            "non_striker": self.p2.id,
            "bowler": self.b1.id
        }
        res = self.client.post(url_setup, data_setup)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        # 3. Submit Ball
        url_ball = reverse('submit_ball')
        ball_data = {
            "innings": innings_obj.id,
            "over_number": 1,
            "ball_number": 1,
            "ball_in_over": 1,
            "bowler": self.b1.id,
            "striker": self.p1.id,
            "non_striker": self.p2.id,
            "runs": {
                "runs_off_bat": 4,
                "extras": 0
            }
        }
        res = self.client.post(url_ball, ball_data, format='json')
        if res.status_code != 201:
            print("Ball Submit Failed:", res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
    def test_end_innings(self):
        # Create completed innings context
        innings = Innings.objects.create(
            match=self.match, batting_team_id=self.team1.id, bowling_team_id=self.team2.id, innings_number=1,
            state="ACTIVE"
        )
        url = reverse('end_innings', args=[innings.id])
        res = self.client.post(url, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        innings.refresh_from_db()
        self.assertEqual(innings.state, "COMPLETED")

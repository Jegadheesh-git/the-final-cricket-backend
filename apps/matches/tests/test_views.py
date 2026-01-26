from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from matches.models import Match, MatchType, PlayingXI
from coredata.models import Nationality, Team, Player
from competitions.models import Tournament, Competition
from accounts.models import User
from subscriptions.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta

class MatchViewsTest(APITestCase):
    def setUp(self):
        # Auth & Sub
        self.user = User.objects.create_user(username="testadmin", password="password")
        self.plan = Plan.objects.create(name="Free Plan", code="FREE", owner_type="USER", billing_cycle="MONTHLY", razorpay_plan_id="plan_123")
        self.sub = Subscription.objects.create(
            owner_type="USER", owner_id=self.user.id, plan=self.plan, status="ACTIVE",
            current_period_end=timezone.now() + timedelta(days=30)
        )
        self.client.force_login(self.user)

        # Base Data
        self.nat = Nationality.objects.create(name="MatchLand", code="ML")
        self.team1 = Team.objects.create(name="Team A", team_type="DOMESTIC", nationality=self.nat)
        self.team2 = Team.objects.create(name="Team B", team_type="DOMESTIC", nationality=self.nat)
        self.p1 = Player.objects.create(first_name="P1", last_name="L1", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER")
        self.p2 = Player.objects.create(first_name="P2", last_name="L2", nationality=self.nat, gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER")
        self.mtype = MatchType.objects.create(name="T20", code="T20", max_overs=20)

        # Context
        self.tournament = Tournament.objects.create(name="Tourney 1", tournament_type="LEAGUE", owner_type="USER", owner_id=self.user.id)
        self.competition = Competition.objects.create(name="Comp 1", tournament=self.tournament, owner_type="USER", owner_id=self.user.id)

    def test_create_match(self):
        url = reverse('match-create') # Updated name
        data = {
            "competition": self.competition.id,
            "match_type": self.mtype.id,
            "team1": self.team1.id,
            "team2": self.team2.id,
            "match_mode": "ONLINE"
        }
        response = self.client.post(url, data)
        if response.status_code != 201:
            print("Match Create Failed:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 1)
        self.assertEqual(Match.objects.get().state, "DRAFT")

    def test_set_playing_xi(self):
        # Create match manually
        match = Match.objects.create(
            competition=self.competition, match_type=self.mtype, team1=self.team1, team2=self.team2, match_mode="ONLINE", state="READY"
        )
        url = reverse('playing-xi', args=[match.id])
        
        from competitions.models import CompetitionTeam, CompetitionSquad
        ct = CompetitionTeam.objects.create(competition=self.competition, team=self.team1)
        
        # Create 11 Players
        players_data = []
        for i in range(1, 12):
            p = Player.objects.create(
                first_name=f"P{i}", last_name=f"L{i}", nationality=self.nat, 
                gender="MALE", batting_hand="RIGHT", bowling_hand="RIGHT", role="BATTER"
            )
            # Add to Squad
            CompetitionSquad.objects.create(competition_team=ct, player=p)
            
            players_data.append({
                "player_id": str(p.id),
                "batting_position": i,
                "is_captain": (i == 1), # First player is captain
                "is_wicket_keeper": (i == 2)
            })

        data = {
            "team_id": self.team1.id,
            "players": players_data
        }
        response = self.client.put(url, data, format='json')
        if response.status_code != 200:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check first player
        self.assertTrue(PlayingXI.objects.filter(match=match, batting_position=1).exists())

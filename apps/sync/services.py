# from stadium.models import Stadium
from .models import SyncOperation

def apply_operation(*, scope, device_id, op):
    sync_id = op["sync_id"]

    #Idempotency check
    if SyncOperation.objects.filter(
        device_id = device_id,
        sync_id = sync_id,\
        operation = op["operation"]
    ).exists():
        return {"sync_id":sync_id, "status":"SKIPPED"}
    
    """
    
    if op["entity"] == "stadium":
        if op["operation"] == "CREATE":
            Stadium.objects.create(
                sync_id = sync_id,
                owner_type = scope.owner_type,
                owner_id = scope.owner_id,
                **op["payload"]
            )

        elif op["operation"] == "UPDATE":
            Stadium.objects.filter(
                sync_id = sync_id,
                owner_type = scope.owner_type,
                owner_id = scope.owner_id
            ).update(**op["payload"])

        elif op["operation"] == "DELETE":
            Stadium.objects.filter(
                sync_id = sync_id,
                owner_type = scope.owner_type,
                owner_id = scope.owner_id
            ).delete()

    SyncOperation.objects.create(
        owner_type = scope.owner_type,
        owner_id = scope.owner_id,
        device_id = device_id,
        entity = op["entity"],
        operation = op["operation"],
        sync_id=sync_id,
        payload=op["payload"]
    )

    return {"sync_id":sync_id, "status":"APPLIED"}

    """

from django.db import transaction
from django.shortcuts import get_object_or_404
from matches.models import Match, PlayingXI
from competitions.models import CompetitionSquad, SeriesSquad
from scoring.services.ball_service import submit_ball
# from scoring.services.session_service import start_scoring_session # Reuse logic?

def get_player_squad(context_obj, team):
    """
    Helper to fetch squad players based on context (Competition/Series).
    """
    players = []
    
    if hasattr(context_obj, 'competition_teams'):
        # It is a Competition
        comp_team = context_obj.competition_teams.filter(team=team).first()
        if comp_team:
            squad_entries = CompetitionSquad.objects.filter(competition_team=comp_team).select_related('player')
            players = [entry.player for entry in squad_entries]
            
    elif hasattr(context_obj, 'teams'):
        # It is a Series
        series_team = context_obj.teams.filter(team=team).first()
        if series_team:
            squad_entries = SeriesSquad.objects.filter(series_team=series_team).select_related('player')
            players = [entry.player for entry in squad_entries]
            
    return players

def get_offline_match_context(match_id):
    match = get_object_or_404(Match, id=match_id)
    
    # 1. Determine Context
    context_obj = match.competition if match.competition else match.series
    # If neither (shouldn't happen per constraints), no squad?
    
    # 2. Fetch Squads
    t1_squad = get_player_squad(context_obj, match.team1)
    t2_squad = get_player_squad(context_obj, match.team2)
    
    # 3. Serialize output
    def serialize_player(p):
        return {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "role": p.role,
            "batting_hand": p.batting_hand,
            "bowling_hand": p.bowling_hand,
            "full_name": f"{p.first_name} {p.last_name}"
        }
        
    return {
        "match_id": match.id,
        "match_type": {
            "balls_per_over": match.match_type.balls_per_over,
            "max_overs": match.match_type.max_overs,
            "name": match.match_type.name,
            # Add other rules
        },
        "teams": {
            "team1": {
                "id": match.team1.id,
                "name": match.team1.name,
                "short_name": match.team1.short_name,
                "squad": [serialize_player(p) for p in t1_squad]
            },
            "team2": {
                "id": match.team2.id,
                "name": match.team2.name,
                "short_name": match.team2.short_name,
                "squad": [serialize_player(p) for p in t2_squad]
            }
        },
        "state": match.state
    }

@transaction.atomic
def process_bulk_sync(data, user):
    """
    Process offline actions: Events (Toss, XI) -> Balls.
    """
    match_id = data['match_id']
    match = get_object_or_404(Match, id=match_id)
    
    # 1. Process Pre-Scoring Events (Toss, Playing XI)
    events = data.get('events', [])
    for event in events:
        if event['type'] == 'TOSS_DECISION':
            handle_toss_sync(match, event['payload'])
        elif event['type'] == 'PLAYING_XI':
            handle_playing_xi_sync(match, event['payload'])
            
    # 2. Process Balls
    balls = data.get('balls', [])
    results = []
    for ball_payload in balls:
        # ball_payload should match arguments for submit_ball
        # Ideally, offline app sends exactly what submit_ball expects
        # We might need to inject 'innings' ID if offline app works with local IDs?
        # Assuming offline app knows the server Innings ID or we resolve it.
        # For a new match, 'Innings' might need to be created via an Event first!
        
        # If offline app created innings locally, it needs to sync that 'INNINGS_START' event first.
        # Let's assume ball_payload has valid server IDs for now, or we handle ID mapping.
        
        try:
             # Check if ball already exists?
             ball_id = submit_ball(ball_payload, user)
             results.append({"status": "SUCCESS", "ball_id": ball_id})
        except Exception as e:
             results.append({"status": "ERROR", "error": str(e)}) # Stop or Continue?
             # For rigorous sync, likely stop and report error?
             raise e 
             
    return {"status": "SYNC_COMPLETED", "processed_balls": len(results)}

from matches.models import Toss
from matches.models import Team, Player

def handle_toss_sync(match, payload):
    won_by_id = payload.get('won_by')
    decision = payload.get('decision')
    
    if hasattr(match, 'toss'):
        # Idempotent: if already exists, assume it matches or update?
        # For safety in offline sync, we might update if data differs, or just skip.
        return

    won_by_team = get_object_or_404(Team, id=won_by_id)
    
    Toss.objects.create(
        match=match,
        won_by=won_by_team,
        decision=decision
    )

def handle_playing_xi_sync(match, payload):
    # payload: list of dicts { "team_id": ..., "player_id": ..., "batting_position": ..., "is_captain": ..., "is_wicket_keeper": ... }
    # Or maybe grouped by team? The serializer said "payload" is generic dict.
    # Let's assume payload is a LIST of player entries.
    
    players_data = payload.get('players', [])
    
    # Ideally, wipe existing XI and recreate? Or standard bulk create?
    # Offline sync might be partial? No, usually "bulk sync" implies full state push from offline session.
    # To be safe, we can check existence.
    
    existing_xi = set(
        PlayingXI.objects.filter(match=match).values_list('team_id', 'player_id')
    )
    
    new_entries = []
    for p_data in players_data:
        team_id = p_data['team_id']
        player_id = p_data['player_id']
        
        if (team_id, player_id) in existing_xi:
            continue
            
        new_entries.append(PlayingXI(
             match=match,
             team_id=team_id,
             player_id=player_id,
             batting_position=p_data['batting_position'],
             is_captain=p_data.get('is_captain', False),
             is_wicket_keeper=p_data.get('is_wicket_keeper', False)
        ))
        
    if new_entries:
        PlayingXI.objects.bulk_create(new_entries)
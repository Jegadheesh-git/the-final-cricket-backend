from uuid import UUID
from django.shortcuts import get_object_or_404
from django.db import transaction

from matches.models import Innings, PlayingXI
from scoring.models.aggregates import InningsAggregate

@transaction.atomic
def setup_innings(
    innings_id: UUID,
    striker_id: UUID,
    non_striker_id: UUID,
    bowler_id: UUID
) -> None:
    """
    Phase 2 — Lock initial innings setup.
    """

    innings = get_object_or_404(Innings, id=innings_id)

    if innings.state != "OPEN":
        raise ValueError("Innings is not open for setup")

    if striker_id == non_striker_id:
        raise ValueError("Striker and non-striker cannot be the same")

    match = innings.match

    # Playing XIs
    batting_xi = set(PlayingXI.objects.filter(
        match=match,
        team=innings.batting_team
    ).values_list("player_id", flat=True))

    bowling_xi = set(PlayingXI.objects.filter(
        match=match,
        team=innings.bowling_team
    ).values_list("player_id", flat=True))

    # Validate batters
    if striker_id not in batting_xi or non_striker_id not in batting_xi:
        raise ValueError("Selected batters are not in batting Playing XI")

    # Validate bowler
    if bowler_id not in bowling_xi:
        raise ValueError("Selected bowler is not in bowling Playing XI")

    # Get or create aggregate
    aggregate, _ = InningsAggregate.objects.get_or_create(
        innings=innings
    )

    aggregate.current_striker_id = striker_id
    aggregate.current_non_striker_id = non_striker_id
    aggregate.current_bowler_id = bowler_id
    
    # Calculate Target
    target = calculate_target_runs(innings)
    if target:
        aggregate.target_runs = target
        
    aggregate.save()

    innings.state = "ACTIVE"
    innings.save()

def calculate_target_runs(current_innings: Innings) -> int | None:
    match = current_innings.match
    if match.match_type.is_test:
        return calculate_test_target(current_innings)
    else:
        return calculate_limited_overs_target(current_innings)

def calculate_limited_overs_target(innings: Innings) -> int | None:
    # If Super Over
    if innings.is_super_over:
        # If accessing super over, find the PREVIOUS super over for this match (same index?)
        # Actually super over chasing means Innings 2 of the super over pair.
        # Assuming pair is handled by sequence or batting team? 
        # Typically SO is 1 over per team.
        # If this is the 2nd innings of the Super Over.
        # How to know? batting_team was bowling_team in previous SO innings with same index?
        # Let's simplify: Check if there is a COMPLETED super over with the SAME index.
        prev_so = Innings.objects.filter(
            match=innings.match, 
            is_super_over=True, 
            super_over_index=innings.super_over_index,
            state="COMPLETED"
        ).order_by('-innings_number').first()
        
        if prev_so:
             agg = InningsAggregate.objects.filter(innings=prev_so).first()
             return (agg.runs + 1) if agg else None
        return None

    # Standard Limited Overs
    if innings.innings_number == 2:
        i1 = Innings.objects.filter(match=innings.match, innings_number=1).first()
        if i1 and i1.state == "COMPLETED":
             agg = InningsAggregate.objects.filter(innings=i1).first()
             return (agg.runs + 1) if agg else None
    return None

def calculate_test_target(innings: Innings) -> int | None:
    # Only Innings 4 has a target to win
    if innings.innings_number != 4:
        return None
        
    # Get all previous innings
    i1 = Innings.objects.filter(match=innings.match, innings_number=1).first()
    i2 = Innings.objects.filter(match=innings.match, innings_number=2).first()
    i3 = Innings.objects.filter(match=innings.match, innings_number=3).first()
    
    if not (i1 and i2 and i3):
        return None
        
    def get_runs(i):
        agg = InningsAggregate.objects.filter(innings=i).first()
        return agg.runs if agg else 0
        
    r1 = get_runs(i1)
    r2 = get_runs(i2)
    r3 = get_runs(i3)
    
    # Check sequences
    # Standard: T1(r1), T2(r2), T1(r3) -> Target for T2(I4) = (r1 + r3) - r2 + 1
    # Follow-on: T1(r1), T2(r2), T2(r3) -> Target for T1(I4) = (r2 + r3) - r1 + 1
    
    # We can just sum runs by team
    batting_team_id = innings.batting_team_id
    
    # If standard: I4 batting team is T2.
    # T2 runs so far = r2. T1 runs = r1 + r3.
    # Target = (All runs of Opponent) - (All runs of Self) + 1
    
    runs_self = 0
    runs_opp = 0
    
    for i, r in [(i1, r1), (i2, r2), (i3, r3)]:
        if i.batting_team_id == batting_team_id:
            runs_self += r
        else:
            runs_opp += r
            
    target = runs_opp - runs_self + 1
    
    # If target is <= 0, it means they already won?? No, usually Innings 4 starts only if there IS a target.
    # If Innings 3 finished with Opponent leading by X, then target is X+1.
    # If Innings 3 finished and Opponent still trails (Innings Defeat), Innings 4 wouldn't normally start.
    # But if it does, target logic stands.
    
    return target if target > 0 else 0

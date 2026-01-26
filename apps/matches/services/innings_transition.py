from uuid import UUID
from django.shortcuts import get_object_or_404
from django.db import transaction

from matches.models import Match, Innings

@transaction.atomic
def end_innings(innings_id: UUID) -> None:
    innings = get_object_or_404(Innings, id=innings_id)

    if innings.state != "ACTIVE":
        raise ValueError("Only ACTIVE innings can be ended")

    innings.state = "COMPLETED"
    innings.save()

@transaction.atomic
def prepare_next_innings(
    match_id: UUID, 
    is_super_over: bool = False, 
    enforce_follow_on: bool = False
) -> Innings:
    match = get_object_or_404(Match, id=match_id)
    match_type = match.match_type

    last = Innings.objects.filter(match=match).order_by("-innings_number").first()
    if not last:
        raise ValueError("Cannot prepare next innings without a previous one")

    # 1. Super Over Logic
    if is_super_over:
        if not match_type.super_over_allowed:
            raise ValueError("Super Over not allowed for this match type")
            
        # Determine SO number (1, 2, ...)
        last_so_index = Innings.objects.filter(
            match=match, is_super_over=True
        ).count()
        
        new_innings_number = last.innings_number + 1
        
        # Super over typically starts with Team 2 batting first (chasing team from regular match)
        # But rules vary. Let's assume standard: Team 2 bats first in SO 1.
        # IF multiple super overs?
        # Standard: Team that batted SECOND in previous SO bats FIRST in new SO.
        
        if last_so_index == 0:
            # First SO: Team 2 bats first
            batting_team = match.team2
            bowling_team = match.team1
        else:
            # Subsequent SO: Swap from last innings
            batting_team = last.bowling_team
            bowling_team = last.batting_team

        return Innings.objects.create(
            match=match,
            innings_number=new_innings_number,
            batting_team=batting_team,
            bowling_team=bowling_team,
            state="OPEN",
            is_super_over=True,
            super_over_index=last_so_index + 1
        )

    # 2. Standard Logic (with Follow-On check)
    completed_count = Innings.objects.filter(
        match=match, state="COMPLETED", is_super_over=False
    ).count()

    # match_type.max_innings is the Total innings (e.g. 2 for T20, 4 for Test)
    max_allowed = match_type.max_innings

    if completed_count >= max_allowed:
        raise ValueError("No more standard innings allowed")

    new_number = completed_count + 1
    
    # Follow-On Logic
    if enforce_follow_on:
        if not match_type.follow_on_allowed:
             raise ValueError("Follow-on not allowed for this match type")
        
        # Follow-on means SAME team bats again.
        # Usually happens after Innings 2. So Innings 3 has SAME batting team as Innings 2.
        batting_team = last.batting_team
        bowling_team = last.bowling_team
    else:
        # Standard Swap
        batting_team = last.bowling_team
        bowling_team = last.batting_team

    return Innings.objects.create(
        match=match,
        innings_number=new_number,
        batting_team=batting_team,
        bowling_team=bowling_team,
        state="OPEN",
    )

def end_match(match_id: UUID) -> None:
    match = get_object_or_404(Match, id=match_id)

    if match.state != "COMPLETED":
        match.state = "COMPLETED"
        match.save()

"""
SERVICE: Start or Resume Innings Session

RESPONSIBILITY:
- Create first innings if none exists
- Resume active innings if already created
- Set match state to IN_PROGRESS

MUST NEVER DO:
- Save balls
- Decide targets or results
"""

from django.db import transaction
from django.utils import timezone
from matches.models import Innings


@transaction.atomic
def start_or_resume_innings_session(*, match):
    active = match.innings.filter(state=Innings.State.ACTIVE).first()
    if active:
        return active

    innings = match.innings.order_by("innings_number").first()
    if innings:
        innings.state = Innings.State.ACTIVE
        innings.start_time = innings.start_time or timezone.now()
        innings.save()
    else:
        innings = Innings.objects.create(
            match=match,
            innings_number=1,
            batting_team=match.team1,
            bowling_team=match.team2,
            state=Innings.State.ACTIVE,
            start_time=timezone.now(),
        )

    match.state = "IN_PROGRESS"
    match.save(update_fields=["state"])
    return innings

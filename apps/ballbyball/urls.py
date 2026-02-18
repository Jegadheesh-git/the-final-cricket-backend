from django.urls import path
from .api.verify_match_is_ready_for_ball_by_ball_scoring import (
    VerifyMatchReadyForBallByBallScoringView,
)
from ballbyball.api.initialise_ball_by_ball_session import (
    InitialiseBallByBallSessionView,
)
from ballbyball.api.record_single_ball_delivery import (RecordSingleBallDeliveryView)
from ballbyball.api.undo_most_recent_ball_delivery import (
    UndoMostRecentBallDeliveryView,
)
from ballbyball.api.end_active_innings import EndActiveInningsView
from ballbyball.api.start_next_innings import StartNextInningsView
from ballbyball.api.end_match import EndMatchView
from ballbyball.api.apply_dls import ApplyDLSView
from ballbyball.api.apply_penalty import ApplyPenaltyView
from ballbyball.api.declare_innings import DeclareInningsView

urlpatterns = [
    path(
        "verify-match-is-ready-for-ball-by-ball-scoring/",
        VerifyMatchReadyForBallByBallScoringView.as_view(),
        name="verify-match-ready-for-scoring",
    ),
    path(
        "initialise-ball-by-ball-session/",
        InitialiseBallByBallSessionView.as_view(),
        name="initialise-ball-by-ball-session",
    ),
    path(
        "record-single-ball-delivery/",
        RecordSingleBallDeliveryView.as_view(),
        name="record-single-ball-delivery",
    ),
    path(
        "undo-most-recent-ball-delivery/",
        UndoMostRecentBallDeliveryView.as_view(),
        name="undo-most-recent-ball-delivery",
    ),
    path(
        "end-active-innings/",
        EndActiveInningsView.as_view(),
        name="end-active-innings",
    ),
    path(
        "start-next-innings/",
        StartNextInningsView.as_view(),
        name="start-next-innings",
    ),
    path(
        "end-match/",
        EndMatchView.as_view(),
        name="end-match",
    ),
    path(
        "apply-dls/",
        ApplyDLSView.as_view(),
        name="apply-dls",
    ),
    path(
        "apply-penalty/",
        ApplyPenaltyView.as_view(),
        name="apply-penalty",
    ),
    path(
        "declare-innings/",
        DeclareInningsView.as_view(),
        name="declare-innings",
    ),
]

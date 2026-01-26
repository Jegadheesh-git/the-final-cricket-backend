from django.urls import path
from .views import (
    MatchViewSet,
    MatchDetailView,
    MatchStateUpdateView,
    PrepareOfflineMatchView,
    ConfirmOnlineMatchView,
    StartMatchView,
    CompleteMatchView,
    OfflineSyncView,
    PlayingXIView,
    TossView,
    InningsView,

    EndInningsAPIView,
    PrepareNextInningsAPIView,
    EndMatchAPIView,
)

from rest_framework.routers import SimpleRouter
router = SimpleRouter()
router.register(r'matches', MatchViewSet)

urlpatterns = router.urls

urlpatterns += [
    path("matches/<uuid:match_id>/prepare-offline/", PrepareOfflineMatchView.as_view(), name="prepare-offline"),
    path("matches/<uuid:match_id>/confirm-online/", ConfirmOnlineMatchView.as_view(), name="confirm-online"),
    path("matches/<uuid:match_id>/start/", StartMatchView.as_view(), name="start-match"),
    path("matches/<uuid:match_id>/complete/", CompleteMatchView.as_view(), name="complete-match"),
    path("matches/<uuid:match_id>/sync-offline/", OfflineSyncView.as_view(), name="sync-offline"),
    path("matches/<uuid:match_id>/playing-xi/", PlayingXIView.as_view(), name="playing-xi"),
    path("matches/<uuid:match_id>/toss/", TossView.as_view(), name="toss"),
    path("matches/<uuid:match_id>/innings/", InningsView.as_view(), name="innings"),
    path("matches/<uuid:match_id>/innings/<int:innings_number>/complete/", InningsView.as_view(), name="complete-innings"),
    path("matches/<uuid:match_id>/detail/", MatchDetailView.as_view(), name="match-detail"),
    path(
        "matches/<uuid:match_id>/state/",
        MatchStateUpdateView.as_view(),
        name="match-state-update"
    ),
]

urlpatterns += [
    path("innings/<uuid:innings_id>/end/", EndInningsAPIView.as_view()),
    path("matches/<uuid:match_id>/innings/prepare-next/", PrepareNextInningsAPIView.as_view()),
    path("matches/<uuid:match_id>/end/", EndMatchAPIView.as_view()),
]







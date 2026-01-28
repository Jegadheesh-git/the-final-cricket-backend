from django.urls import path
from .views import (
    TournamentViewSet, TournamentListView,
    CompetitionViewSet, CompetitionListView,
    CompetitionTeamsView, CompetitionSquadView,
    SeriesTeamsView, SeriesSquadView
)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'tournaments', TournamentViewSet)
router.register(r'competitions', CompetitionViewSet)

router.register(
    r"my-tournaments",
    TournamentListView,
    basename="my-tournaments"
)


urlpatterns = router.urls

urlpatterns += [
    path('competitions/<uuid:competition_id>/teams/', CompetitionTeamsView.as_view(), name='competition-teams'),
    path('competition/<uuid:competition_id>/team/<uuid:team_id>/squad/', CompetitionSquadView.as_view(), name='competition-squad')
]

urlpatterns += [
    path(
        "series/<uuid:series_id>/teams/",
        SeriesTeamsView.as_view(),
        name="series-teams"
    ),
    path(
        "series-teams/<int:series_team_id>/squad/",
        SeriesSquadView.as_view(),
        name="series-squad"
    ),
]

urlpatterns += [
    
    
    path(
        "my-competitions/",
        CompetitionListView.as_view({"get": "list"}),
        name="tournament-list",
    ),
    
]

"""
    path(
        "my-tournaments/",
        TournamentListView.as_view({"get": "list"}),
        name="tournament-list",
    ),
    """
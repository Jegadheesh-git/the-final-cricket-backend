from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (
    NationalityListView,
    StadiumViewSet, StadiumListView,
    UmpireViewSet,
    PlayerViewSet,
    PlayerListView,
    TeamViewSet,
    TeamListView
)
# APIView URLs
urlpatterns = [
    path("nationalities/", NationalityListView.as_view(), name="nationality"),
]
# ViewSet URLs (Router)
router = SimpleRouter()
router.register(r"stadiums", StadiumViewSet, basename="stadium")
router.register(r"umpires", UmpireViewSet, basename="umpire")
router.register(r"players", PlayerViewSet, basename="player")
router.register(r"teams", TeamViewSet, basename="team")
# Combine both
urlpatterns += router.urls

urlpatterns += [
    path(
        "my-teams/",
        TeamListView.as_view({"get": "list"}),
        name="team-list",
    ),
    path(
        "my-players/",
        PlayerListView.as_view({"get": "list"}),
        name="player-list",
    ),
    path(
        "my-stadiums/",
        StadiumListView.as_view({"get": "list"}),
        name="stadium-list",
    ),
    path(
        "my-umpires/",
        UmpireViewSet.as_view({"get": "list"}),
        name="umpire-list",
    ),
]
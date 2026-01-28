from .models import Nationality, Stadium, Umpire, Player, Team
from .serializers import NationalitySerializer, StadiumSerializer, UmpireSerializer, PlayerSerializer, TeamSerializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from backend.core.viewsets import OwnedModelViewSet, OwnedModelListView

class NationalityListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NationalitySerializer
    pagination_class = None
    queryset = Nationality.objects.filter(is_active=True)

class StadiumViewSet(OwnedModelViewSet):
    serializer_class = StadiumSerializer
    queryset = Stadium.objects.all()

class StadiumListView(OwnedModelListView):
    serializer_class = StadiumSerializer
    queryset = Stadium.objects.all()

class UmpireViewSet(OwnedModelViewSet):
    serializer_class = UmpireSerializer
    queryset = Umpire.objects.all()

class UmpireListView(OwnedModelListView):
    serializer_class = UmpireSerializer
    queryset = Stadium.objects.all()

class PlayerViewSet(OwnedModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()

class PlayerListView(OwnedModelListView):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()

class TeamViewSet(OwnedModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()

class TeamListView(OwnedModelListView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
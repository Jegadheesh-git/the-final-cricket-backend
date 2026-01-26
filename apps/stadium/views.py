from backend.core.viewsets import BaseScopedModelViewSet
from .models import Stadium
from .serializers import StadiumSerializer

class StadiumViewSet(BaseScopedModelViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer

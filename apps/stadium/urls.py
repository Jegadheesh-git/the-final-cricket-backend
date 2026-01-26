from rest_framework.routers import SimpleRouter
from .views import StadiumViewSet

router = SimpleRouter()
router.register("stadiums", StadiumViewSet, basename="stadium")

urlpatterns = router.urls
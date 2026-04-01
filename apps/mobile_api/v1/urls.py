from apps.mobile_api.v1.views import ConsultaViewSet
from apps.utils.api import get_api_router

app_name = "v1"

router = get_api_router()
router.register("consultas", ConsultaViewSet, basename="consultas")

urlpatterns = router.urls

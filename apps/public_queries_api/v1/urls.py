from apps.public_queries_api.v1.views import PublicQueryAuth, PublicQueryMapResult
from apps.utils.api import get_api_router

app_name = "v1"

router = get_api_router()
router.register("query-result", PublicQueryMapResult, basename="query-map-result")
router.register("auth", PublicQueryAuth, basename="auth")


urlpatterns = router.urls

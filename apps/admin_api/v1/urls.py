from apps.admin_api.v1.views import PublicQueryAPI, PublicQueryManager
from apps.utils.api import get_api_router

app_name = "v1"

router = get_api_router()
router.register("public-query", PublicQueryManager, basename="public-query")
router.register("public-query-api", PublicQueryAPI, basename="public-query-api")


urlpatterns = router.urls

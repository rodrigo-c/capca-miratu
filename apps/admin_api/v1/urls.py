from apps.admin_api.v1.views import PublicQueryManager
from apps.utils.api import get_api_router

app_name = "v1"

router = get_api_router()
router.register("public-query", PublicQueryManager, basename="public-query")


urlpatterns = router.urls

from django.apps import AppConfig

from apps.public_queries.lib.constants import AppConstants


class PublicQueriesConfig(AppConfig):
    name = "apps.public_queries"
    verbose_name = AppConstants.VERBOSE_NAME

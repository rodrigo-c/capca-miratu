from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PublicQueriesConfig(AppConfig):
    name = "apps.public_queries"
    verbose_name = gettext_lazy("Public Queries")

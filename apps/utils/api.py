from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter


def get_api_router():
    return DefaultRouter() if settings.DEBUG else SimpleRouter()

from django.contrib import admin

from apps.admin.registrations import register_models


class AdminSite(admin.AdminSite):
    pass


admin_site = AdminSite(name="django_admin")
register_models(site=admin_site)

from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "apps.admin.site.AdminSite"

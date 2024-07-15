from django.contrib.admin import AdminSite

from apps.admin.registrations.users import users_tuple_models

TUPLE_MODEL_ARRAY = [
    *users_tuple_models,
]


def register_models(site: AdminSite) -> None:
    for tuple_model in TUPLE_MODEL_ARRAY:
        site.register(*tuple_model)

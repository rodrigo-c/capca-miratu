from django.contrib.auth import views as auth_views

from apps.public_queries.lib.constants import ContextConstants


class UserLoginView(auth_views.LoginView):
    template_name = "admin/login.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["app_context"] = ContextConstants
        context["form"] = self._set_auth_form(form=context["form"])
        return context

    def _set_auth_form(self, form):
        form.fields["username"].widget.attrs["autocomplete"] = "email"
        form.fields["username"].widget.attrs["type"] = "email"
        form.fields["username"].widget.attrs["placeholder"] = "Correo electrónico"
        form.fields["password"].widget.attrs["placeholder"] = "Contraseña"
        return form

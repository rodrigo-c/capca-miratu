from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from apps.public_queries.lib.constants import ContextConstants


class UserLoginView(auth_views.LoginView):
    template_name = "admin/login.html"
    next_page = "admin:entry-point"
    redirect_authenticated_user = True

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

    def get_success_url(self):
        return self.get_default_redirect_url()


class UserLogoutView(auth_views.LogoutView):
    next_page = "admin:login"

    def get_success_url(self):
        return self.get_default_redirect_url()


class AdminEntryPoint(LoginRequiredMixin, TemplateView):
    template_name = "admin/entry-point.html"
    login_url = "/admin/login/"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["user"] = {
            "email": self.request.user.email,
            "is_superuser": self.request.user.is_superuser,
        }
        context["url_base"] = reverse("admin_api:v1:public-query-list")
        context["cursor"] = {
            "focus": self.request.GET.get("f"),
            "key": self.request.GET.get("k"),
        }
        return context

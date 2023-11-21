from django.http import Http404
from django.views.generic import TemplateView

from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.services import get_active_public_query_by_uuid


class PublicQuerySubmit(TemplateView):
    template_name = "public_queries/submit.html"

    def get(self, request, uuid):
        try:
            public_query = get_active_public_query_by_uuid(uuid=uuid)
        except PublicQueryDoesNotExist:
            raise Http404
        context = self.get_context_data(public_query=public_query)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["navigation_title"] = "Consulta Pública"
        return context

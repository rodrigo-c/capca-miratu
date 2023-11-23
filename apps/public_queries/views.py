from django.http import Http404
from django.views.generic import TemplateView

from apps.public_queries.forms import AnswerFormSet, ResponseForm
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.services import get_active_public_query_by_uuid


class PublicQuerySubmit(TemplateView):
    template_name = "public_queries/submit.html"

    def get(self, request, uuid):
        try:
            public_query = get_active_public_query_by_uuid(uuid=uuid)
        except PublicQueryDoesNotExist:
            raise Http404
        self.public_query = public_query
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self):
        context = super().get_context_data(public_query=self.public_query)
        context["navigation_title"] = "Consulta Pública"
        context["response_form"] = ResponseForm(
            initial={"query": self.public_query.uuid}
        )
        if self.public_query.questions:
            initial = [
                {"question-data": question, "question": question.uuid}
                for question in self.public_query.questions
            ]
            context["answer_formset"] = AnswerFormSet(initial=initial)
        return context

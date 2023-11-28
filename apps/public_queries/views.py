from uuid import UUID

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.public_queries.forms import AnswerFormSet, ResponseForm
from apps.public_queries.lib.exceptions import ObjectDoesNotExist
from apps.public_queries.services import (
    get_active_public_query_by_url_code,
    get_active_public_query_by_uuid,
    get_response_by_uuid,
    submit_response,
)


class PublicQuerySubmit(TemplateView):
    template_name = "public_queries/submit.html"

    def dispatch(self, request, uuid, *args, **kwargs) -> HttpResponse:
        try:
            if len(str(uuid)) <= getattr(settings, "MAXIMUM_URL_CHARS", 5):
                public_query = get_active_public_query_by_url_code(url_code=uuid)
            else:
                uuid = UUID(uuid)
                public_query = get_active_public_query_by_uuid(uuid=uuid)
        except (ValueError, ObjectDoesNotExist):
            raise Http404
        self.public_query = public_query
        return super().dispatch(request, uuid, *args, **kwargs)

    def get(self, request, uuid) -> HttpResponse:
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, uuid) -> HttpResponseRedirect | HttpResponse:
        response_form = ResponseForm(
            data=request.POST,
            initial={"query": self.public_query.uuid},
        )
        answer_formset = self.get_answer_formset(data=request.POST, files=request.FILES)

        if not (response_form.is_valid() & answer_formset.is_valid()):
            if not response_form.is_valid():
                focus = "response"
            else:
                focus = next(
                    index
                    for index, form in enumerate(answer_formset)
                    if not form.is_valid()
                )
            context = self.get_context_data(
                response_form=response_form, answer_formset=answer_formset, focus=focus
            )
            return self.render_to_response(context)

        submitted_response_data = submit_response(
            response=response_form.get_validated_dataclass(
                query_uuid=self.public_query.uuid,
                answers=answer_formset.get_validated_dataclasses(),
            ),
            public_query=self.public_query,
        )
        return HttpResponseRedirect(
            redirect_to=self.get_success_url(response_uuid=submitted_response_data.uuid)
        )

    def get_context_data(
        self,
        response_form: ResponseForm | None = None,
        answer_formset: AnswerFormSet | None = None,
        focus: str | None = None,
    ) -> dict:
        context = super().get_context_data(public_query=self.public_query)
        context["focus"] = focus if focus is not None else "detail"
        context["navigation_title"] = "Consulta Pública"
        context["response_form"] = response_form or self.get_response_form()
        if self.public_query.questions:
            context["answer_formset"] = answer_formset or self.get_answer_formset()
        return context

    def get_response_form(self, **kwargs) -> ResponseForm:
        return ResponseForm(initial={"query": self.public_query.uuid}, **kwargs)

    def get_answer_formset(self, **kwargs) -> AnswerFormSet:
        initial = [
            {"question-data": question} for question in self.public_query.questions
        ]
        return AnswerFormSet(**kwargs, initial=initial)

    def get_success_url(self, response_uuid: UUID) -> str:
        return reverse("public_queries:submit-success", kwargs={"uuid": response_uuid})


class SuccessSubmit(TemplateView):
    template_name = "public_queries/success.html"

    def dispatch(self, request, uuid, *args, **kwargs) -> HttpResponse:
        try:
            uuid = UUID(uuid)
            response_data = get_response_by_uuid(uuid=uuid)
        except (ValueError, ObjectDoesNotExist):
            raise Http404
        self.response_data = response_data
        return super().dispatch(request, uuid, *args, **kwargs)

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["response_data"] = self.response_data
        context["navigation_title"] = "Consulta Pública"
        context["success_message"] = "El formulario fue enviado con éxito."
        context[
            "sucess_gratitude_message"
        ] = "¡Gracias por aportar con tu visión ciudadana!"
        return context

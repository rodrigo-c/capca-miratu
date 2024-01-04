from uuid import UUID

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.public_queries.forms import AnswerFormSet, ResponseForm
from apps.public_queries.lib.constants import (
    ContextConstants,
    PublicQueryResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.exceptions import ObjectDoesNotExist
from apps.public_queries.services import (
    get_answer_result,
    get_public_query,
    get_public_query_response_result,
    get_public_query_result,
    get_response_by_uuid,
    submit_response,
)


class UUIDObjectURL:
    url_active_status = None
    url_service = None
    url_service_field = "identifier"
    url_service_extra_kwargs = None

    def dispatch(self, request, uuid, *args, **kwargs) -> HttpResponse:
        extra_kwargs = self.get_url_service_extra_kwargs()
        try:
            object_data = self.__class__.url_service(
                **{self.url_service_field: uuid, **extra_kwargs}
            )
        except ObjectDoesNotExist:
            raise Http404
        self.object = object_data
        return super().dispatch(request, uuid, *args, **kwargs)

    def get_url_service_extra_kwargs(self):
        return self.url_service_extra_kwargs or {}

    def _get_page_num(self) -> int:
        if "page_num" in self.request.GET and self.request.GET["page_num"].isdecimal():
            return int(self.request.GET["page_num"])
        return 1


class PublicQuerySubmit(UUIDObjectURL, TemplateView):
    template_name = "public_queries/submit.html"
    url_service = get_public_query
    url_service_extra_kwargs = {"active": True}

    def get(self, request, uuid) -> HttpResponse:
        self.public_query = self.object
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, uuid) -> HttpResponseRedirect | HttpResponse:
        self.public_query = self.object
        response_form = self.get_response_form(
            data=request.POST,
        )
        answer_formset = self.get_answer_formset(data=request.POST, files=request.FILES)
        if not (response_form.is_valid() & answer_formset.is_valid()):
            return self._return_invalid_forms(
                response_form=response_form, answer_formset=answer_formset
            )

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

    def _return_invalid_forms(
        self, response_form: ResponseForm, answer_formset: AnswerFormSet
    ) -> HttpResponse:
        if not response_form.is_valid():
            focus = "identifier"
        else:
            focus = next(
                index
                for index, form in enumerate(answer_formset)
                if (
                    not form.is_valid()
                    or form.question_data.kind == QuestionConstants.KIND_IMAGE
                )
            )
        context = self.get_context_data(
            response_form=response_form, answer_formset=answer_formset, focus=focus
        )
        return self.render_to_response(context)

    def get_context_data(
        self,
        response_form: ResponseForm | None = None,
        answer_formset: AnswerFormSet | None = None,
        focus: str | None = None,
    ) -> dict:
        context = super().get_context_data(public_query=self.public_query)
        context["focus"] = focus if focus is not None else "entry"
        context["auth_url"] = self.get_auth_url()
        context["app_context"] = ContextConstants
        context["response_form"] = response_form or self.get_response_form()
        if self.public_query.questions:
            context["answer_formset"] = answer_formset or self.get_answer_formset()
        return context

    def get_auth_url(self) -> str:
        return reverse(
            "public_queries_api:v1:auth-can-submit",
            kwargs={"pk": self.public_query.url_code},
        )

    def get_response_form(self, **kwargs) -> ResponseForm:
        return ResponseForm(
            initial={"query": self.public_query.uuid, "query-data": self.public_query},
            **kwargs
        )

    def get_answer_formset(self, **kwargs) -> AnswerFormSet:
        initial = [
            {"question-data": question} for question in self.public_query.questions
        ]
        return AnswerFormSet(**kwargs, initial=initial)

    def get_success_url(self, response_uuid: UUID) -> str:
        return reverse("public_queries:submit-success", kwargs={"uuid": response_uuid})


class SuccessSubmit(UUIDObjectURL, TemplateView):
    template_name = "public_queries/success.html"
    url_service = get_response_by_uuid
    url_service_field = "uuid"

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["response_data"] = self.object
        context["success_message"] = ContextConstants.SUCCESS_MESSAGE
        context["sucess_gratitude_message"] = ContextConstants.SUCCESS_GRATITUDE
        return context


class PublicQueryResult(UUIDObjectURL, TemplateView):
    template_name = "public_queries/query-result.html"
    url_service = get_public_query

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["result"] = get_public_query_result(public_query=self.object)
        context["navigation_title"] = "Resultado de Consulta Pública"
        return context


class AnswerQuestionResult(UUIDObjectURL, TemplateView):
    template_name = "public_queries/answer-result.html"
    url_service = get_answer_result
    url_service_field = "question_uuid"

    def get_url_service_extra_kwargs(self):
        return {
            "page_num": self._get_page_num(),
            "page_size": PublicQueryResultConstants.DEFAULT_PAGE_SIZE,
        }

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["answer_result"] = self.object
        context["navigation_title"] = "Resultado de Consulta Pública"
        return context


class PublicQueryResponseResult(UUIDObjectURL, TemplateView):
    template_name = "public_queries/response-result.html"
    url_service = get_public_query

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        page_num = self._get_page_num()
        response_result = get_public_query_response_result(
            public_query=self.object,
            page_num=page_num,
            page_size=PublicQueryResultConstants.DEFAULT_PAGE_SIZE,
        )
        context["response_result"] = response_result
        context["navigation_title"] = "Resultado de Consulta Pública"
        return context


class PublicQueryMapResult(UUIDObjectURL, TemplateView):
    template_name = "public_queries/map-result.html"
    url_service = get_public_query

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["public_query"] = self.object
        return context

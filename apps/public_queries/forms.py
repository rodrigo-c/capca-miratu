from uuid import UUID

from django import forms
from django.forms import formset_factory

from apps.public_queries.lib.dataclasses import AnswerData, ResponseData


class ResponseForm(forms.Form):
    query = forms.UUIDField(widget=forms.HiddenInput(), required=True)
    email = forms.EmailField(required=False)
    rut = forms.CharField(max_length=10, required=False)

    def get_validated_dataclass(
        self, query_uuid: UUID, answers: list[AnswerData]
    ) -> ResponseData:
        return ResponseData(
            query_uuid=query_uuid,
            answers=answers,
            email=self.cleaned_data.get("email") or None,
            rut=self.cleaned_data.get("rut") or None,
        )


class AnswerForm(forms.Form):
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Agregar comentarios"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get("initial", {})
        self.question_data = initial.get("question-data")
        if self.question_data:
            self.fields["text"].required = self.question_data.required

    def get_validated_dataclass(self) -> AnswerData:
        return AnswerData(
            question_uuid=self.question_data.uuid,
            text=self.cleaned_data.get("text") or None,
        )


def get_validated_dataclasses(formset) -> list[AnswerData]:
    return [form.get_validated_dataclass() for form in formset.forms]


AnswerFormSet = formset_factory(AnswerForm, extra=0)
AnswerFormSet.get_validated_dataclasses = get_validated_dataclasses

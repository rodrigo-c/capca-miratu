from uuid import UUID

from django.contrib.gis import forms
from django.core.validators import MaxLengthValidator
from django.forms import formset_factory

from multiupload.fields import MultiImageField, MultiUploadMetaInput

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import AnswerData, ResponseData


class ResponseForm(forms.Form):
    query = forms.UUIDField(widget=forms.HiddenInput(), required=True)
    location = forms.PointField(widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(required=False)
    rut = forms.CharField(max_length=10, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "tu@correo.cl (Opcional)"
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["rut"].widget.attrs["placeholder"] = "1000000-1 (Opcional)"
        self.fields["rut"].widget.attrs["autocomplete"] = "rut"

    def get_validated_dataclass(
        self, query_uuid: UUID, answers: list[AnswerData]
    ) -> ResponseData:
        return ResponseData(
            query_uuid=query_uuid,
            answers=answers,
            email=self.cleaned_data.get("email") or None,
            rut=self.cleaned_data.get("rut") or None,
            location=self.cleaned_data.get("location"),
        )


class MultipleImageInput(MultiUploadMetaInput):
    template_name = "public_queries/components/image-field.html"
    allow_multiple_selected = True


class MultiImageField(MultiImageField):
    def to_python(self, data):
        return super().to_python(data=data or [])

    def run_validators(self, value):
        value = value or []
        for image in value:
            super().run_validators(value=image)


class AnswerForm(forms.Form):
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Agregar comentarios"}),
    )
    images = MultiImageField(required=False, widget=MultipleImageInput())
    options = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "options-field"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get("initial", {})
        self.question_data = initial.get("question-data")
        if self.question_data:
            self._set_fields_by_kind(kind=self.question_data.kind)

    def _set_fields_by_kind(self, kind: str) -> None:
        if kind == QuestionConstants.KIND_TEXT:
            self._set_text_answer()

        elif kind == QuestionConstants.KIND_IMAGE:
            self._set_image_answer()

        elif kind == QuestionConstants.KIND_SELECT:
            self._set_select_answer()

    def _set_text_answer(self):
        field = self.fields["text"]
        field.required = self.question_data.required
        max_length = int(self.question_data.text_max_length or 255)
        field.maxlength = max_length
        field.validators.append(MaxLengthValidator(max_length))
        field.widget.attrs["maxlength"] = max_length
        field.widget.attrs["required"] = self.question_data.required
        field.widget.attrs["minlength"] = 1 if field.required else None
        self._hide_field("images")
        self._hide_field("options")

    def _set_image_answer(self):
        field = self.fields["images"]
        field.required = self.question_data.required
        field.min_num = 1 if self.question_data.required else 0
        field.max_num = self.question_data.max_answers
        field.maxlength = field.max_num
        field.widget.attrs["maxlength"] = field.max_num
        field.widget.attrs["minlength"] = 1 if field.required else None
        field.widget.attrs["required"] = self.question_data.required
        self._hide_field("text")
        self._hide_field("options")

    def _set_select_answer(self):
        field = self.fields["options"]
        field.required = self.question_data.required
        field.choices = [
            (option_data.uuid, option_data.name)
            for option_data in self.question_data.options
        ]
        max_length = int(self.question_data.max_answers or 1)
        field.maxlength = max_length
        message = (
            f"Sólo puede seleccionar máximo {max_length} "
            f"opci{'ones' if max_length > 1 else 'ón'}"
        )
        field.validators.append(
            MaxLengthValidator(limit_value=max_length, message=message)
        )
        self._hide_field("text")
        self._hide_field("images")

    def _hide_field(self, field: str) -> None:
        self.fields[field].disabled = True
        self.fields[field].widget.attrs.update({"class": "hidden"})

    def get_validated_dataclasses(self) -> list[AnswerData]:
        if self.question_data.kind == QuestionConstants.KIND_TEXT:
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                text=self.cleaned_data.get("text") or None,
            )
            return [answer_data]
        elif self.question_data.kind == QuestionConstants.KIND_IMAGE:
            image_files = self.cleaned_data.get("images", []) or []
            return [
                AnswerData(
                    question_uuid=self.question_data.uuid,
                    image=image_file,
                )
                for image_file in image_files
            ]
        elif self.question_data.kind == QuestionConstants.KIND_SELECT:
            options = self.cleaned_data.get("options")
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                options=[UUID(option_uuid) for option_uuid in options],
            )
            return [answer_data]


def get_validated_dataclasses(formset) -> list[AnswerData]:
    validated_data_list = []
    for form in formset.forms:
        validated_data_list.extend(form.get_validated_dataclasses())
    return validated_data_list


AnswerFormSet = formset_factory(AnswerForm, extra=0)
AnswerFormSet.get_validated_dataclasses = get_validated_dataclasses

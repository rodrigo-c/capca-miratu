from uuid import UUID

from django.contrib.gis import forms
from django.core.validators import MaxLengthValidator
from django.forms import formset_factory

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.lib.dataclasses import AnswerData, ResponseData


class ResponseForm(forms.Form):
    query = forms.UUIDField(widget=forms.HiddenInput(), required=True)
    location = forms.PointField(widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(required=False)
    rut = forms.CharField(max_length=10, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get("initial", {})
        public_query = initial.get("query-data")
        if public_query:
            self.set_auth(public_query=public_query)
        self.fields["email"].widget.attrs["placeholder"] = "Correo electrónico"
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["rut"].widget.attrs["placeholder"] = "Rut"
        self.fields["rut"].widget.attrs["autocomplete"] = "rut"

    def set_auth(self, public_query) -> None:
        if public_query.auth_email == PublicQueryConstants.AUTH_DISABLE:
            self.fields["email"].disabled = True
        elif public_query.auth_email == PublicQueryConstants.AUTH_REQUIRED:
            self.fields["email"].widget.attrs["required"] = True
            self.fields["email"].required = True
        if public_query.auth_rut == PublicQueryConstants.AUTH_DISABLE:
            self.fields["rut"].disabled = True
        elif public_query.auth_rut == PublicQueryConstants.AUTH_REQUIRED:
            self.fields["rut"].widget.attrs["required"] = True
            self.fields["rut"].required = True

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


class OSMWidget(forms.OSMWidget):
    template_name = "public_queries/components/point-field.html"


class PreviewImageInput(forms.ClearableFileInput):
    template_name = "public_queries/components/image-field.html"


class OptionFieldInput(forms.CheckboxSelectMultiple):
    template_name = "public_queries/components/options-field.html"
    option_template_name = "public_queries/components/options-field-input.html"


class AnswerForm(forms.Form):
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "Agregar comentarios", "rows": "5"}
        ),
    )
    image = forms.ImageField(
        required=False,
        widget=PreviewImageInput(),
    )
    options = forms.MultipleChoiceField(
        required=False,
        widget=OptionFieldInput(),
    )
    point = forms.PointField(required=False, widget=OSMWidget())

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

        elif kind == QuestionConstants.KIND_POINT:
            self._set_point_answer()

    def _hide_fields(self, exclude: list[str] | None = None) -> None:
        for field_name in self.fields.keys():
            if field_name not in exclude:
                self.fields[field_name].disabled = True
                self.fields[field_name].widget.attrs.update({"class": "hidden"})

    def _set_text_answer(self):
        field = self.fields["text"]
        field.required = self.question_data.required
        max_length = int(self.question_data.text_max_length or 255)
        field.maxlength = max_length
        field.validators.append(MaxLengthValidator(max_length))
        field.widget.attrs["maxlength"] = max_length
        field.widget.attrs["required"] = self.question_data.required
        field.widget.attrs["minlength"] = 1 if field.required else None
        self._hide_fields(exclude=["text"])

    def _set_image_answer(self):
        field = self.fields["image"]
        field.required = self.question_data.required
        field.min_num = 1 if self.question_data.required else 0
        field.max_num = self.question_data.max_answers
        field.maxlength = field.max_num
        field.widget.attrs["maxlength"] = field.max_num
        field.widget.attrs["minlength"] = 1 if field.required else None
        field.widget.attrs["required"] = self.question_data.required
        self._hide_fields(exclude=["image"])

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
        self._hide_fields(exclude=["options"])

    def _set_point_answer(self):
        field = self.fields["point"]
        field.required = self.question_data.required
        default_lon = (
            self.question_data.default_point[0]
            if self.question_data.default_point
            else -70.668423
        )
        default_lat = (
            self.question_data.default_point[1]
            if self.question_data.default_point
            else -33.447869
        )
        field.widget.attrs["default_lat"] = default_lat
        field.widget.attrs["default_lon"] = default_lon
        field.widget.attrs["default_zoom"] = self.question_data.default_zoom or 9
        self._hide_fields(exclude=["point"])

    def get_validated_dataclass(self) -> AnswerData:
        if self.question_data.kind == QuestionConstants.KIND_IMAGE:
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                image=self.cleaned_data.get("image") or None,
            )
        elif self.question_data.kind == QuestionConstants.KIND_TEXT:
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                text=self.cleaned_data.get("text") or None,
            )
        elif self.question_data.kind in [
            QuestionConstants.KIND_SELECT,
            QuestionConstants.KIND_SELECT_IMAGE,
        ]:
            options = self.cleaned_data.get("options", [])
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                options=[UUID(option_uuid) for option_uuid in options],
            )
        elif self.question_data.kind == QuestionConstants.KIND_POINT:
            answer_data = AnswerData(
                question_uuid=self.question_data.uuid,
                point=self.cleaned_data.get("point") or None,
            )
        return answer_data


def get_validated_dataclasses(formset) -> list[AnswerData]:
    validated_data_list = []
    for form in formset.forms:
        validated_data_list.append(form.get_validated_dataclass())
    return validated_data_list


AnswerFormSet = formset_factory(AnswerForm, extra=0)
AnswerFormSet.get_validated_dataclasses = get_validated_dataclasses

from django import forms
from django.forms import formset_factory


class ResponseForm(forms.Form):
    query = forms.UUIDField(widget=forms.HiddenInput(), required=True)
    email = forms.EmailField(required=False)
    rut = forms.CharField(max_length=10, required=False)


class AnswerForm(forms.Form):
    question = forms.UUIDField(widget=forms.HiddenInput(), required=True)
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


AnswerFormSet = formset_factory(AnswerForm, extra=0)

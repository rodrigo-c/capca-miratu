from unittest import mock

from apps.public_queries.forms import AnswerForm


class TestAnswerForm:
    def test_init(self):
        fake_question_data = mock.Mock()
        fake_question_data.required = True
        form = AnswerForm(initial={"question-data": fake_question_data})
        assert form.fields["text"].required == fake_question_data.required
        assert form.question_data == fake_question_data

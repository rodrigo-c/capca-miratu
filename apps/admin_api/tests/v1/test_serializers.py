import pytest

from apps.admin_api.lib.constants import PublicQueryErrorConstants
from apps.admin_api.v1.serializers.edit import CreateQuestionSerializer
from apps.public_queries.lib.constants import QuestionConstants


@pytest.mark.django_db
class TestCreateQuestionSerializer:
    def get_base_data(self) -> dict:
        return {
            "kind": QuestionConstants.KIND_SELECT,
            "name": "Question X",
            "required": False,
        }

    def test_success(self):
        data = self.get_base_data()
        data["options"] = [{"name": "1"}, {"name": "2"}]
        serializer = CreateQuestionSerializer(data=data)
        assert serializer.is_valid()

    def test_option_equals(self):
        data = self.get_base_data()
        option_label = "Option"
        data["options"] = [
            {"name": option_label},
            {"name": option_label},
        ]
        serializer = CreateQuestionSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            str(serializer.errors["options"][0])
            == PublicQueryErrorConstants.OPTIONS_EQUALS
        )

    def test_option_list_empty(self):
        data = self.get_base_data()
        serializer = CreateQuestionSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            str(serializer.errors["options"][0])
            == PublicQueryErrorConstants.OPTIONS_EMPTY
        )

    def test_option_list_with_one(self):
        data = self.get_base_data()
        data["options"] = [{"name": "1"}]
        serializer = CreateQuestionSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            str(serializer.errors["options"][0])
            == PublicQueryErrorConstants.OPTIONS_EMPTY
        )

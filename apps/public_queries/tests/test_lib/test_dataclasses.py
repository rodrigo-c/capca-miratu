import json
from datetime import datetime

from django.contrib.gis.geos import Point

from apps.public_queries.lib.dataclasses import AnswerData, AnswerResultData


class TestAnswerResultData:
    def test_partial_list_json(self):
        partial_list = [
            AnswerData(
                question_uuid=None, point=Point(index, index), send_at=datetime.now()
            )
            for index in range(5)
        ]
        answer_result_data = AnswerResultData(
            question=None, total=5, partial_list=partial_list
        )
        partial_list_json = answer_result_data.partial_list_json
        assert isinstance(partial_list_json, str)
        loaded_partial_list = json.loads(partial_list_json)
        assert loaded_partial_list[0]["question_uuid"] is None
        assert isinstance(loaded_partial_list[0]["send_at"], str)

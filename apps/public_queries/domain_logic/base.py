from apps.public_queries.lib.dataclasses import AnswerData
from apps.public_queries.models import Answer
from apps.utils.dataclasses import build_dataclass_from_model_instance


class ServiceBase:
    def _build_answer_data_list(
        self, instances: list[Answer], with_response: bool = False
    ) -> list[AnswerData]:
        answers = [
            build_dataclass_from_model_instance(
                klass=AnswerData,
                instance=instance,
                uuid=instance.id,
                response_uuid=instance.response_id,
                question_uuid=instance.question_id,
                image=instance.image.url if instance.image else None,
                options=getattr(instance, "_cached_options", None),
                send_at=(instance.response.send_at if with_response else None),
            )
            for instance in instances
        ]
        return answers

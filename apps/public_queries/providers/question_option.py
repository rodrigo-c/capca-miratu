from apps.public_queries.models import QuestionOption


def bulk_create_question_options(data_list: list[dict]) -> list[QuestionOption]:
    fields = ["name", "order"]
    instances = []
    for data in data_list:
        instance_kwargs = {field: data[field] for field in fields if field in data}
        instance_kwargs["question_id"] = data["question_uuid"]
        instance = QuestionOption(**instance_kwargs)
        instances.append(instance)
    return QuestionOption.objects.bulk_create(objs=instances)

from apps.public_queries.models import Answer


def bulk_create_answers(answers: list[dict]) -> list[Answer]:
    instances = [Answer(**answer) for answer in answers]
    return Answer.objects.bulk_create(objs=instances)

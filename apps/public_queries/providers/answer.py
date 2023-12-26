from uuid import UUID

from apps.public_queries.models import Answer


def bulk_create_answers(answers: list[dict]) -> list[Answer]:
    instances = [Answer(**answer) for answer in answers]
    return Answer.objects.bulk_create(objs=instances)


def get_total_answers_by_question_uuid(question_uuid: UUID) -> int:
    return Answer.objects.filter(question_id=question_uuid).count()


def get_answers_by_question_uuid(question_uuid: UUID) -> list[Answer]:
    return Answer.objects.filter(question_id=question_uuid)


def get_answers_by_query_uuid(query_uuid: UUID) -> list[Answer]:
    return Answer.objects.filter(question__query_id=query_uuid)


def get_total_answers_by_option_uuid(option_uuid: UUID) -> int:
    return Answer.objects.filter(options=option_uuid).count()

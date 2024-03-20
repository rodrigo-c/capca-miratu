from apps.public_queries.models import PublicQuery


def query_can_edit_questions(public_query: PublicQuery) -> bool:
    can_edit = True
    max_question = 10
    for index, _ in enumerate(public_query.responses.all()):
        if index == max_question:
            can_edit = False
            break
    return can_edit

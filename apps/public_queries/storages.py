def get_public_query_image_path(instance, filename) -> str:
    return f"public_queries/{instance.url_code}/images/{filename}"


def get_public_query_answer_image_path(instance, filename) -> str:
    url_code = instance.response.query.url_code
    return f"public_queries/{url_code}/answers/{instance.response_id}/{filename}"


def get_public_query_answer_image_path_thumb(instance, filename) -> str:
    url_code = instance.response.query.url_code
    return f"public_queries/{url_code}/answers/{instance.id}-thumb.png"


def get_public_query_answer_image_path_thumb_medium(instance, filename) -> str:
    url_code = instance.response.query.url_code
    return (
        f"public_queries/{url_code}/answers/"
        f"{str(instance.response.send_at)[:19]}-{instance.id}.png"
    )


def get_public_query_question_image_path(instance, filename) -> str:
    url_code = instance.query.url_code
    return f"public_queries/{url_code}/questions/{instance.id}/{filename}"


def get_public_query_question_option_image_path(instance, filename) -> str:
    url_code = instance.question.query.url_code
    return f"public_queries/{url_code}/questions-options/{instance.id}/{filename}"

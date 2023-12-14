class AppConstants:
    VERBOSE_NAME = "App Consulta Pública"


class PublicQueryConstants:
    KIND_OPEN = "OPEN"
    KIND_CHOICES = [
        (KIND_OPEN, "Open"),
    ]
    VERBOSE_NAME = "Consulta"
    VERBOSE_NAME_PLURAL = "Consultas"


class QuestionConstants:
    KIND_TEXT = "TEXT"
    KIND_IMAGE = "IMAGE"
    KIND_SELECT = "SELECT"
    KIND_POINT = "POINT"
    KIND_CHOICES = [
        (KIND_TEXT, "Text"),
        (KIND_IMAGE, "Image"),
        (KIND_SELECT, "Select"),
        (KIND_POINT, "Geo Point"),
    ]
    RESULT_AVAILABLE_KINDS = [
        KIND_TEXT,
        KIND_IMAGE,
        KIND_POINT,
    ]
    VERBOSE_NAME = "Pregunta"
    VERBOSE_NAME_PLURAL = "Preguntas"


class PublicQueryResultConstants:
    LENGTH_PARTIAL_LIST = 5
    QUESTION_KIND_WITH_LIST = [
        QuestionConstants.KIND_TEXT,
        QuestionConstants.KIND_IMAGE,
    ]
    DEFAULT_PAGE_SIZE = 50


class QuestionOptionConstants:
    VERBOSE_NAME = "Opción"
    VERBOSE_NAME_PLURAL = "Opciones"


class ResponseConstants:
    VERBOSE_NAME = "Respuesta"
    VERBOSE_NAME_PLURAL = "Respuestas"


class AnswerConstants:
    VERBOSE_NAME = "Respuesta a pregunta"
    VERBOSE_NAME_PLURAL = "Respuestas a preguntas"

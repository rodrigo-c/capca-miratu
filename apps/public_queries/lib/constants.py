class AppConstants:
    VERBOSE_NAME = "App Consulta Pública"


class ContextConstants:
    HEAD_TITLE = "Bienvenido a"
    MAIN_TITLE = "Visión <b>ciudadana</b>"
    QUERY_RESPONSE = "Responder consulta"
    IDENTIFIER_LABEL = "Identificación"
    DETAIL_LABEL = "En qué consiste"
    QUESTION_LABEL = "Pregunta"
    NEXT_LABEL = "Siguiente"
    BACK_LABEL = "Volver"
    SUCCESS_MESSAGE = "Tu respuesta fue enviada con éxito"
    SUCCESS_GRATITUDE = "¡Muchas gracias por tu respuesta!"
    QUERY_SUCCES = "¡Muchas gracias por tu respuesta!"


class PublicQueryConstants:
    KIND_OPEN = "OPEN"
    KIND_CLOSED = "CLOSED"
    KIND_CHOICES = [
        (KIND_OPEN, "Abierta"),
        (KIND_CLOSED, "Cerrada"),
    ]
    AUTH_REQUIRED = "REQUIRED"
    AUTH_OPTIONAL = "OPTIONAL"
    AUTH_DISABLE = "DISABLE"
    AUTH_CHOICES = [
        (AUTH_REQUIRED, "Requerido"),
        (AUTH_OPTIONAL, "Opcional"),
        (AUTH_DISABLE, "Deshabilitado"),
    ]
    VERBOSE_NAME = "Consulta"
    VERBOSE_NAME_PLURAL = "Consultas"
    NOT_MAX_RESPONSES = 0

    STATUS_VERBOSE_DRAFT = "draft"
    STATUS_VERBOSE_ACTIVE = "active"
    STATUS_VERBOSE_FINISHED = "finished"
    STATUS_VERBOSE_EARRING = "earring"
    STATUS_VERBOSE_LABELS = {
        STATUS_VERBOSE_DRAFT: "Borrador",
        STATUS_VERBOSE_ACTIVE: "Activa",
        STATUS_VERBOSE_FINISHED: "Finalizada",
        STATUS_VERBOSE_EARRING: "Pendiente",
    }


class AuthConstants:
    RUT_REQUIRED = "El RUT es requerido"
    EMAIL_REQUIRED = "El correo es requerido"
    RUT_INVALID = "El RUT es inválido"
    EMAIL_INVALID = "El correo es inválido"
    RUT_MAX_RESPONSES = "El RUT ya emitió el máximo de respuestas"
    EMAIL_MAX_RESPONSES = "El correo ya emitió el máximo de respuestas"
    EMAIL_NOT_ALLOWED = "El correo no está habilitado"
    FORBIDDEN = "No está autorizado"


class QuestionConstants:
    KIND_TEXT = "TEXT"
    KIND_IMAGE = "IMAGE"
    KIND_SELECT = "SELECT"
    KIND_SELECT_IMAGE = "SELECT_IMAGE"
    KIND_POINT = "POINT"
    KIND_CHOICES = [
        (KIND_TEXT, "Text"),
        (KIND_IMAGE, "Image"),
        (KIND_SELECT, "Select"),
        (KIND_SELECT_IMAGE, "Select images"),
        (KIND_POINT, "Geo Point"),
    ]
    RESULT_AVAILABLE_KINDS = [
        KIND_TEXT,
        KIND_IMAGE,
        KIND_POINT,
    ]
    VERBOSE_NAME = "Pregunta"
    VERBOSE_NAME_PLURAL = "Preguntas"
    KIND_TO_FIELD_LABEL = {
        KIND_TEXT: "text",
        KIND_IMAGE: "image",
        KIND_SELECT: "options",
        KIND_SELECT_IMAGE: "options",
        KIND_POINT: "point",
    }


class ResponderConstants:
    VERBOSE_NAME = "Consultado"
    VERBOSE_NAME_PLURAL = "Consultados"


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


class QueryMapResultConstants:
    LOCATION = "Ubicación del usuario"


class CreatePublicQueryConstants:
    INVALID_START_END_AT = "La fecha de inicio debe ser menor que la de término"

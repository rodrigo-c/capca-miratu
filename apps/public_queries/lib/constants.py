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
    SUCCESS_GRATITUDE = "¡Muchas gracias por aportar con tu visión ciudadana!"


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
    KIND_TO_FIELD_LABEL = {
        KIND_TEXT: "text",
        KIND_IMAGE: "image",
        KIND_SELECT: "options",
        KIND_POINT: "point",
    }


class ResponderConstants:
    VERBOSE_NAME = "Respondedor"
    VERBOSE_NAME_PLURAL = "Respondedores"


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

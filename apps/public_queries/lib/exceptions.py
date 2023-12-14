class ObjectDoesNotExist(Exception):
    pass


class PublicQueryDoesNotExist(ObjectDoesNotExist):
    pass


class ResponseDoesNotExist(ObjectDoesNotExist):
    pass


class QuestionDoesNotExist(ObjectDoesNotExist):
    pass

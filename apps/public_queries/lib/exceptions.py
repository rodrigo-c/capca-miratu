class ObjectDoesNotExist(Exception):
    pass


class PublicQueryDoesNotExist(ObjectDoesNotExist):
    pass


class ResponseDoesNotExist(ObjectDoesNotExist):
    pass


class QuestionDoesNotExist(ObjectDoesNotExist):
    pass


class CantSubmitPublicQueryError(Exception):
    def __init__(self, data, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)

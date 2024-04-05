class ObjectDoesNotExist(Exception):
    pass


class PublicQueryDoesNotExist(ObjectDoesNotExist):
    pass


class PublicQueryEarring(Exception):
    def __init__(self, public_query, *args, **kwargs):
        self.public_query = public_query
        super().__init__(*args, **kwargs)


class ResponseDoesNotExist(ObjectDoesNotExist):
    pass


class QuestionDoesNotExist(ObjectDoesNotExist):
    pass


class CantSubmitPublicQueryError(Exception):
    def __init__(self, data, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)


class PublicQueryCreateError(Exception):
    pass


class PublicQueryUpdateError(Exception):
    pass

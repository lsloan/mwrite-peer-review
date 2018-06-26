class ReviewsInProgressException(Exception):
    pass


class APIException(Exception):
    def __init__(self, **kwargs):
        self.status_code = kwargs['status_code']
        self.data = kwargs['data']

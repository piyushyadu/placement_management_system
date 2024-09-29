
class DatabaseAddException(Exception):
    def __init__(self, message='unable to add data in database'):
        super().__init__(message)


class DatabaseFetchException(Exception):
    def __init__(self, message='unable to fetch data from database'):
        super().__init__(message)

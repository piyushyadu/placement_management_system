
class DatabaseException(Exception):
    """Base class for all database related exception"""
    pass


class DatabaseAddException(DatabaseException):
    def __init__(self, message='unable to add data in database'):
        super().__init__(message)


class DatabaseFetchException(DatabaseException):
    def __init__(self, message='unable to fetch data from database'):
        super().__init__(message)


class NotFoundException(Exception):
    """Base class for resource not found related exception"""
    pass


class JobNotFoundException(NotFoundException):
    def __init__(self, job_id):
        super().__init__(f"Job with job id '{job_id}' not found")


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id):
        super().__init__(f"User with id '{user_id}' not found")

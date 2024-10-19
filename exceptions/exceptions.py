
class DatabaseException(Exception):
    """Base class for all database related exception"""
    pass


class DatabaseAddException(DatabaseException):
    def __init__(self, message='unable to add data in database'):
        super().__init__(message)


class DatabaseFetchException(DatabaseException):
    def __init__(self, message='unable to fetch data from database'):
        super().__init__(message)


class DatabaseDeleteException(DatabaseException):
    def __init__(self, message='unable to delete data from database'):
        super().__init__(message)


class NotFoundException(Exception):
    """Base class for resource not found related exception"""
    def __init__(self, message):
        super().__init__(message)
    pass


class JobNotFoundException(NotFoundException):
    def __init__(self, job_id):
        super().__init__(message=f"Job(job_id={job_id}) not found")


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id):
        super().__init__(f"User(user_id={user_id}) not found")


class QuestionNotFoundException(NotFoundException):
    def __init__(self, user_id):
        super().__init__(f"Question(question_id={user_id}) not found")

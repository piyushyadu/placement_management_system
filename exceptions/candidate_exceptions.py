
class CandidateException(Exception):
    """Base class for all candidate related exception"""
    pass


class UsedUsernameException(CandidateException):
    def __init__(self, message='username already exist'):
        super().__init__(message)


class UsedEmailException(CandidateException):
    def __init__(self, message='email already exist'):
        super().__init__(message)

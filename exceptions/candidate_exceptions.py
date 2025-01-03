
class AccountCreateException(Exception):
    """Base class for all candidate related exception"""
    pass


class CandidateException(Exception):
    """Base class for all candidate related exception"""
    pass


class UsedUsernameException(AccountCreateException):
    def __init__(self, message='username already exist'):
        super().__init__(message)


class UsedEmailException(AccountCreateException):
    def __init__(self, message='email already exist'):
        super().__init__(message)


class ClosedJobException(CandidateException):
    def __init__(self, job_id):
        super().__init__(f'job(id={job_id}) is now closed')


class NotApplicableJobException(CandidateException):
    def __init__(self, user_id, job_id):
        super().__init__(f'user(id={user_id}) is not applicable of job({job_id})')


class AlreadyAppliedJobException(CandidateException):
    def __init__(self, user_id, job_id):
        super().__init__(f'user(id={user_id}) has already applied for job({job_id})')

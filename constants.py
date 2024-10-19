from fastapi import HTTPException, status


class Patterns:
    USERNAME = r'^[a-zA-Z][a-zA-Z0-9_.]{5,29}$'
    EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    NAME = r"^[a-zA-Z\s]{1,50}$"


class ResourceName:
    HEALTH = '/health'
    LOGIN = '/login'
    CREATE_ACCOUNT = '/signup'


class EndpointName:
    CANDIDATE = '/candidate'

    VIEW_ACCOUNTS = '/accounts'
    DECIDE_APPROVAL_STATUS = 'account/{account_id}/status'

    ASK_QUESTION = '/question'
    VIEW_ASKED_QUESTIONS = '/questions'
    ANSWER_QUESTION = 'question/{question_id}/answer'

    JOB = '/job'
    JOBS = '/jobs'
    APPLY_JOB = 'job/{job_id}/apply'
    JOB_APPLICANTS = 'job/{job_id}/applicants'
    MOVE_JOB = 'job/{job_id}/nextRound'

    GET_MESSAGES = '/messages'


class RoleName:
    ADMIN = 'admin'
    CANDIDATE = 'candidate'
    PLACEMENT_OFFICER = 'placement_officer'


class HttpErrorException:
    STATUS_500 = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                               detail='Internal server error.')
    STATUS_501 = HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                               detail='Feature not implemented')
    STATUS_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                               detail="User is not authorized to access this resource")

















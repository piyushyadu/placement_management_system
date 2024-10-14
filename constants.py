
class Patterns:
    USERNAME = r'^[a-zA-Z][a-zA-Z0-9_.]{5,29}$'
    EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    NAME = r"^[a-zA-Z\s]{1,50}$"


class ResourceName:
    APPROVAL = '/approval'
    CREATE_ACCOUNT = '/createAccount'
    HEALTH = '/health'
    LOGIN = '/login'
    Question = '/question'


class EndpointName:
    PENDING_ACCOUNTS = '/pendingAccounts'
    DECIDE_APPROVAL_STATUS = '/decideApprovalStatus'
    CANDIDATE = '/candidate'
    ASK_QUESTION = '/ask'
    VIEW_ASKED_QUESTIONS = '/view'
    ANSWER_QUESTION = '/answer'


class RoleName:
    ADMIN = 'admin'
    CANDIDATE = 'candidate'
    PLACEMENT_OFFICER = 'placement_officer'



class HttpErrorMessage:
    pass
















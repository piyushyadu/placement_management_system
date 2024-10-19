from pydantic import BaseModel, Field, field_validator, constr, conint
from typing import Literal, Optional, List
import datetime
from constants import Patterns


class UserData(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime
    first_name: str
    last_name: str
    approval_status: str
    role: str


class DecideApprovalStatusRequest(BaseModel):
    id: int = Field(gt=0, lt=10**8)
    approval_status: Literal['refused', 'approved']


class DecideApprovalStatusResponse(BaseModel):
    id: int
    username: str
    approval_status: str


class QuestionAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10**4)


class QuestionAskResponse(BaseModel):
    id: int
    questioner_id: int
    question: str
    asked_at: datetime.datetime


class QuestionDataResponse(BaseModel):
    id: int
    questioner_id: int
    asked_at: datetime.datetime
    question: str
    response_status: str
    answerer_id: Optional[int]
    answered_at: Optional[datetime.datetime]
    answer: Optional[str]


class QuestionAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10**4)


class CreateJobRequest(BaseModel):
    company_name: str = Field(pattern=Patterns.NAME, min_length=1, max_length=100)
    job_description: str = Field(min_length=1, max_length=10**4)
    ctc: float = Field(ge=0)
    applicable_degree: str = Field(min_length=1, max_length=100)
    applicable_branches: List[constr(min_length=1, max_length=50)]
    total_round_count: int = Field(gt=0, lt=100)
    application_closed_on: datetime.datetime

    @field_validator('application_closed_on')
    @classmethod
    def validate_application_closed_on(cls, application_closed_on: datetime.datetime):
        application_closed_on = application_closed_on.replace(tzinfo=datetime.timezone.utc)
        if application_closed_on < datetime.datetime.now(datetime.UTC):
            raise ValueError("Application Closing Date Time must be after current Date Time")
        return application_closed_on


class JobResponse(BaseModel):
    id: int
    posted_at: datetime.datetime
    company_name: str
    job_description: str
    ctc: float
    applicable_degree: str
    applicable_branches: List[str]
    total_round_count: int
    current_round: int
    application_closed_on: datetime.datetime


class NextRoundRequest(BaseModel):
    applicants_id_list: List[conint(gt=0, lt=10**8)]
    message: str = Field(min_length=1, max_length=10**4)


class NextRoundResponse(BaseModel):
    job_id: int
    selected_applicants_id: List[int]
    message: str

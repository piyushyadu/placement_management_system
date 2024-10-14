from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
import datetime


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
    id: int = Field(gt=0, le=10**8)
    answer: str = Field(min_length=1, max_length=10**4)

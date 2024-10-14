from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from logger.logger import Logger
from pydantic import BaseModel, Field, field_validator
from buisness_layer.candidate import Candidate
import re
from exceptions.candidate_exceptions import UsedUsernameException, UsedEmailException
from constants import Patterns
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException, JobNotFoundException
from exceptions.candidate_exceptions import NotApplicableJobException, ClosedJobException
from api.routes.authentication import candidate_auth_dependency
import datetime
from typing import List, Optional


router = APIRouter(
    prefix='/candidate',
    tags=['Candidate']
)


def get_candidate_logger() -> Logger:
    return Logger('./logger/logs.log', 'Candidate')


def get_candidate(db: Annotated[Session, Depends(get_db)],
                  log: Annotated[Logger, Depends(get_candidate_logger)],
                  request: Request) -> Candidate:
    return Candidate(db, log, request.state.user_id)


candidate_functionality_dependency = Annotated[Candidate, Depends(get_candidate)]


class QuestionAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)


class QuestionAskResponse(BaseModel):
    id: int
    questioner_id: int
    question: str
    asked_at: datetime.datetime


@router.post('/askQuestion', response_model=QuestionAskResponse)
def post_question(question_request: QuestionAskRequest,
                  candidate_functionality: candidate_functionality_dependency):
    question = candidate_functionality.post_question(question_request.question)
    return QuestionAskResponse(**question)


class QuestionData(BaseModel):
    id: int
    questioner_id: int
    asked_at: datetime.datetime
    question: str
    response_status: str
    answerer_id: Optional[str]
    answered_at: Optional[datetime.datetime]
    answer: Optional[str]


@router.get('/questions', response_model=List[QuestionData])
def get_questions(candidate_functionality: candidate_functionality_dependency,
                  page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):
    offset_count = (page - 1) * elements
    limit_count = elements
    question_list = candidate_functionality.get_question_responses(offset_count, limit_count)
    return question_list


class JobData(BaseModel):
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


@router.get('/jobs', response_model=List[JobData])
def get_jobs(candidate_functionality: candidate_functionality_dependency,
             page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):
    offset_count = (page - 1) * elements
    limit_count = elements
    job_list = candidate_functionality.get_applicable_job_postings(offset_count, limit_count)
    return job_list


class JobApplicationRequest(BaseModel):
    job_id: int = Field(gt=0, lt=10**10)


class JobApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int


@router.post('/applyJob', response_model=JobApplicationResponse)
def apply_job(candidate_functionality: candidate_functionality_dependency,
              request_body: JobApplicationRequest):
    try:
        application = candidate_functionality.apply_for_job(request_body.job_id)
    except JobNotFoundException:
        raise HTTPException(status_code=404, detail=f"Job not found.")
    except ClosedJobException:
        raise HTTPException(status_code=403, detail=f"Job is closed.")
    except NotApplicableJobException:
        raise HTTPException(status_code=403, detail=f"User is not applicable for job.")
    return JobApplicationResponse(**application)

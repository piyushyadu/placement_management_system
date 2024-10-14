from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from logger.logger import Logger
from pydantic import BaseModel, Field, field_validator, constr
from buisness_layer.job import Job
import re
from exceptions.candidate_exceptions import UsedUsernameException, UsedEmailException
from constants import Patterns
from exceptions.exceptions import DatabaseException, JobNotFoundException
from exceptions.candidate_exceptions import NotApplicableJobException, ClosedJobException
from api.routes.authentication import placement_officer_auth_dependency
import datetime
from typing import List, Optional
from api.routes.candidate import JobData


router = APIRouter(
    prefix='/job',
    tags=['Job']
)


def get_job_logger() -> Logger:
    return Logger('./logger/logs.log', 'Candidate')


def get_job(db: Annotated[Session, Depends(get_db)],
            log: Annotated[Logger, Depends(get_job_logger)],
            request: Request) -> Job:
    return Job(db, log, request.state.user_id)


job_functionality_dependency = Annotated[Job, Depends(get_job)]


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


@router.post('/createJob', response_model=JobData)
def create_job_posting(job_functionality: job_functionality_dependency,
                       create_job_request: CreateJobRequest):
    try:
        job = job_functionality.create_job_posting(**create_job_request.model_dump())
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JobData(**job)



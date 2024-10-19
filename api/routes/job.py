from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from typing import List, Union
from buisness_layer.job import Job
from buisness_layer.candidate import Candidate
from api.request_response import CreateJobRequest, UserData, NextRoundRequest, NextRoundResponse
from exceptions.exceptions import DatabaseException, JobNotFoundException
from exceptions.job_exception import NoQualifiedApplicantsException
from exceptions.candidate_exceptions import NotApplicableJobException, ClosedJobException, AlreadyAppliedJobException
from constants import ResourceName, EndpointName, RoleName, HttpErrorException
from logger.logger import Logger


router = APIRouter(
    tags=['Job']
)


def get_user(db: Annotated[Session, Depends(get_db)],
             request: Request):
    role = request.state.role
    if role == RoleName.PLACEMENT_OFFICER:
        return Job(db, request.state.log, request.state.user_id)
    if role == RoleName.CANDIDATE:
        return Candidate(db, request.state.log, request.state.user_id)


user_functionality_dependency = Annotated[Union[Job, Candidate], Depends(get_user)]


@router.post(EndpointName.JOB, status_code=status.HTTP_201_CREATED)
def create_job_posting(user_functionality: user_functionality_dependency,
                       create_job_request: CreateJobRequest,
                       request: Request):
    logger: Logger = request.state.log
    logger.log('Endpoint has received valid data formate.')

    job_data = dict(**create_job_request.model_dump())
    try:
        logger.log('Job creation initiated.')
        job = user_functionality.create_job_posting(job_data)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception as exception:
        logger.log(f'Unknown error: {str(exception)}.')
        raise HttpErrorException.STATUS_500
    else:
        logger.log('Job is created successfully.')
        return job
    finally:
        logger.log('Endpoint has returned Response.')


@router.get(EndpointName.JOBS, status_code=status.HTTP_200_OK)
def get_job_postings(user_functionality: user_functionality_dependency,
                     request: Request,
                     page: int = Query(1, gt=0, lt=10**8),
                     page_size: int = Query(20, gt=0, lt=200),
                     job_status: str = Query(None, enum=['open', 'closed']),
                     order_by_application_closed_on: bool = Query(None),
                     company_name: str = Query(None, min_length=1, max_length=100),
                     max_ctc: float = Query(None, ge=0, le=10*6),
                     min_ctc: float = Query(None, ge=0, le=10**6)):

    logger = request.state.log
    logger.log('Endpoint has received valid data formate.')
    offset_count = (page - 1) * page_size
    limit_count = page_size
    print(offset_count, limit_count)
    conditions = dict(
        job_status=job_status,
        order_by_application_closed_on=order_by_application_closed_on,
        company_name=company_name,
        max_ctc=max_ctc,
        min_ctc=min_ctc
    )
    try:
        role = request.state.role
        if role == RoleName.CANDIDATE:
            logger.log('Fetch applicable job postings initiated.')
            job_postings = user_functionality.get_applicable_job_postings(offset_count, limit_count, conditions)
        elif role == RoleName.PLACEMENT_OFFICER:
            logger.log('Fetch all job postings initiated.')
            job_postings = user_functionality.get_job_postings(offset_count, limit_count, conditions)
        else:
            logger.log(f"Unexpected behaviour: encountered unknown role '{role}'.")
            raise HttpErrorException.STATUS_501
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception as exception:
        logger.log(f'Unknown error: {str(exception)}.')
        raise HttpErrorException.STATUS_500
    else:
        logger.log('Job postings are returned successfully')
        return job_postings
    finally:
        logger.log('Endpoint has returned Response.')


@router.post(EndpointName.APPLY_JOB)
def apply_for_job(user_functionality: user_functionality_dependency,
                  request: Request,
                  job_id: int = Path(gt=0, lt=10**8)):

    logger: Logger = request.state.log
    logger.log('Endpoint has received valid data formate.')
    try:
        logger.log('Apply for job is initiated.')
        application = user_functionality.apply_for_job(job_id)
    except JobNotFoundException:
        raise HTTPException(status_code=404, detail=f"Job not found.")
    except ClosedJobException:
        raise HTTPException(status_code=403, detail=f"Job is closed.")
    except NotApplicableJobException:
        raise HTTPException(status_code=403, detail=f"User is not applicable for job.")
    except AlreadyAppliedJobException:
        raise HTTPException(status_code=409, detail=f"User has already applied for job.")
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception as exception:
        logger.log(f'Unknown error: {str(exception)}.')
        raise HttpErrorException.STATUS_500
    else:
        logger.log('Applied for job successfully')
        return application
    finally:
        logger.log('Endpoint has returned Response.')


@router.get(EndpointName.JOB_APPLICANTS, status_code=status.HTTP_200_OK)
def get_job_applicants(user_functionality: user_functionality_dependency,
                       job_id: int = Path(gt=0, lt=10**8),
                       page: int = Query(1, gt=0, lt=10**8),
                       page_size: int = Query(20, gt=1, lt=10 ** 8)):
    offset_count = (page - 1) * page_size
    limit_count = page_size
    try:
        users = user_functionality.get_job_applicants(job_id, offset_count, limit_count)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        raise HttpErrorException.STATUS_500
    else:
        return users


@router.patch(EndpointName.MOVE_JOB, status_code=status.HTTP_200_OK)
def move_job_to_next_round(user_functionality: user_functionality_dependency,
                           request_body: NextRoundRequest,
                           job_id: int = Path(gt=0, lt=10**8)):
    try:
        response = user_functionality.move_job_next_round(job_id,
                                                          request_body.applicants_id_list,
                                                          request_body.message)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except JobNotFoundException as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))
    except NoQualifiedApplicantsException:
        response = dict(
            job_id=job_id,
            selected_applicants_id=[],
            message=request_body.message
        )
        return response
    except Exception:
        raise HttpErrorException.STATUS_500
    else:
        return response










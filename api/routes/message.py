from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from typing import Union
from buisness_layer.job import Job
from buisness_layer.candidate import Candidate
from exceptions.exceptions import DatabaseException
from constants import EndpointName, HttpErrorException


router = APIRouter(
    tags=['Message']
)


def get_user(db: Annotated[Session, Depends(get_db)],
             request: Request):
    return Candidate(db, request.state.log, request.state.user_id)


user_functionality_dependency = Annotated[Union[Job, Candidate], Depends(get_user)]


@router.get(EndpointName.GET_MESSAGES)
def get_received_messages(user_functionality: user_functionality_dependency,
                          page: int = Query(1, gt=0, lt=10**8),
                          page_size: int = Query(20, gt=0, lt=200)):

    offset_count = (page - 1) * page_size
    limit_count = page_size
    try:
        messages = user_functionality.get_mass_messages(offset_count, limit_count)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        raise HttpErrorException.STATUS_500
    else:
        return messages













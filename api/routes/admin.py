from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from logger.logger import Logger
from pydantic import BaseModel, Field, field_validator
from buisness_layer.admin import Admin
import re
from exceptions.admin_exceptions import SelfStatusSetException
from constants import Patterns
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException, JobNotFoundException, UserNotFoundException
from api.routes.authentication import admin_auth_dependency
import datetime
from typing import List, Optional


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


def get_admin_logger() -> Logger:
    return Logger('./logger/logs.log', 'Admin', )


def get_admin(db: Annotated[Session, Depends(get_db)],
              log: Annotated[Logger, Depends(get_admin_logger)],
              request: Request) -> Admin:
    return Admin(db, log, request.state.user_id)


admin_functionality_dependency = Annotated[Admin, Depends(get_admin)]


class UserData(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime
    first_name: str
    last_name: str
    approval_status: str
    role: str


@router.get('/pendingAccounts', response_model=List[UserData])
def get_pending_accounts(admin_functionality: admin_functionality_dependency,
                         page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):
    offset_count = (page - 1) * elements
    limit_count = elements
    users = admin_functionality.get_unapproved_accounts(offset_count, limit_count)
    return users


class DecideApprovalStatusRequest(BaseModel):
    id: int = Field(gt=0, lt=10**8)


class DecideApprovalStatusResponse(BaseModel):
    id: int
    username: str
    approval_status: str


@router.patch('/decideApprovalStatus', response_model=DecideApprovalStatusResponse)
def set_account_approval_status(admin_functionality: admin_functionality_dependency,
                                request_body: DecideApprovalStatusRequest,
                                status: str = Query(enum=['refused', 'approved'])):
    try:
        approval_response = admin_functionality.set_account_approval_status(request_body.id, status)
    except SelfStatusSetException:
        raise HTTPException(status_code=403, detail="User is not allowed to change their own approval status")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Given user id is not found")
    else:
        return DecideApprovalStatusResponse(**approval_response)











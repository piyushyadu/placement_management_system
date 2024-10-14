from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from typing import List
from buisness_layer.admin import Admin
from api.request_response import UserData, DecideApprovalStatusRequest, DecideApprovalStatusResponse
from exceptions.admin_exceptions import SelfStatusSetException
from exceptions.exceptions import UserNotFoundException, DatabaseException
from constants import ResourceName, EndpointName

router = APIRouter(
    prefix=ResourceName.APPROVAL,
    tags=['Approval']
)


def get_admin(db: Annotated[Session, Depends(get_db)],
              request: Request):
    return Admin(db, request.state.log, request.state.user_id)


admin_functionality_dependency = Annotated[Admin, Depends(get_admin)]


@router.get(EndpointName.PENDING_ACCOUNTS, response_model=List[UserData])
def get_pending_accounts(admin_functionality: admin_functionality_dependency,
                         page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):
    offset_count = (page - 1) * elements
    limit_count = elements
    try:
        users = admin_functionality.get_unapproved_accounts(offset_count, limit_count)
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    else:
        return users


@router.patch(EndpointName.DECIDE_APPROVAL_STATUS, response_model=DecideApprovalStatusResponse)
def set_account_approval_status(admin_functionality: admin_functionality_dependency,
                                request_body: DecideApprovalStatusRequest):
    try:
        approval_response = admin_functionality.set_account_approval_status(request_body.id,
                                                                            request_body.approval_status)
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    except SelfStatusSetException:
        raise HTTPException(status_code=403, detail="User is not allowed to change their own approval status")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Given user id is not found")
    else:
        return DecideApprovalStatusResponse(**approval_response)

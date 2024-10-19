from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from buisness_layer.admin import Admin
from exceptions.admin_exceptions import SelfStatusSetException
from exceptions.exceptions import UserNotFoundException, DatabaseException
from constants import ResourceName, EndpointName, HttpErrorException

router = APIRouter(
    tags=['Account']
)


def get_admin(db: Annotated[Session, Depends(get_db)],
              request: Request):
    return Admin(db, request.state.log, request.state.user_id)


admin_functionality_dependency = Annotated[Admin, Depends(get_admin)]


@router.get(EndpointName.VIEW_ACCOUNTS, status_code=status.HTTP_200_OK)
def get_account_list(admin_functionality: admin_functionality_dependency,
                     request: Request,
                     approval_status: str = Query('pending', enum=['pending', 'approved', 'refused']),
                     page: int = Query(1, gt=0), page_size: int = Query(20, gt=0)):
    logger = request.state.log

    offset_count = (page - 1) * page_size
    limit_count = page_size
    try:
        users = admin_functionality.get_unapproved_accounts(approval_status, offset_count, limit_count)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        logger.log(
            message='Unknown error occurred.',
            level='error'
        )
        raise HttpErrorException.STATUS_500
    else:
        logger.log('Successful response from endpoint is returned.')
        return users


@router.patch(EndpointName.DECIDE_APPROVAL_STATUS, status_code=status.HTTP_200_OK)
def set_account_approval_status(admin_functionality: admin_functionality_dependency,
                                request: Request,
                                account_id: int = Path(gt=0, lt=10**8),
                                approval_status: str = Query(enum=['pending', 'refused', 'approved'])):
    logger = request.state.log

    try:
        approval_response = admin_functionality.set_account_approval_status(account_id,
                                                                            approval_status)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except SelfStatusSetException as exception:
        logger.log(str(exception))
        raise HTTPException(status_code=403, detail=str(exception))
    except UserNotFoundException as exception:
        logger.log(str(exception))
        raise HTTPException(status_code=404, detail=str(exception))
    except Exception:
        logger.log(
            message='Unknown error occurred.',
            level='error'
        )
        raise HttpErrorException.STATUS_500
    else:
        logger.log('Successful response from endpoint is returned.')
        return approval_response

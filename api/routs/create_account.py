from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from logger.logger import Logger
from pydantic import BaseModel, Field
from buisness_layer.create_account import CreateAccount

from exceptions.candidate_exceptions import UsedUsernameException, UsedEmailException


router = APIRouter(
    prefix='/createAccount',
    tags=['createAccount']
)


def get_create_account_logger() -> Logger:
    return Logger('./logger/create_account.log', 'CreateAccount')


def get_create_account(db: Session = Depends(get_db),
                       log: Logger = Depends(get_create_account_logger)) -> CreateAccount:
    return CreateAccount(db, log)


def get_api_logger() -> Logger:
    return Logger('./logger/api/create_account.log', 'api_create_account')


class CandidateAccountRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    degree: str
    branch: str
    cgpa: float = Field(ge=0, le=10)


@router.post('/candidate')
def create_candidate(candidate_account_request: CandidateAccountRequest,
                     account_creator: Annotated[CreateAccount, Depends(get_create_account)],
                     logger: Annotated[Logger, Depends(get_api_logger)]):

    logger.log(
        component='create_candidate',
        message=f'user(email={candidate_account_request.email}) is trying to create account',
        level='info'
    )
    candidate = dict(**candidate_account_request.model_dump())
    try:
        added_user = account_creator.create_candidate(candidate)
    except UsedUsernameException:
        raise HTTPException(status_code=400, detail="user is already registered with give username")
    except UsedEmailException:
        raise HTTPException(status_code=400, detail="user is already registered with give email")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    else:
        return added_user

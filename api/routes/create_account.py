from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from pydantic import BaseModel, Field, field_validator
from buisness_layer.create_account import CreateAccount
import re
from exceptions.candidate_exceptions import UsedUsernameException, UsedEmailException
from constants import Patterns, ResourceName, EndpointName


router = APIRouter(
    prefix=ResourceName.CREATE_ACCOUNT,
    tags=['CreateAccount']
)


def get_create_account(db: Annotated[Session, Depends(get_db)],
                       request: Request) -> CreateAccount:
    return CreateAccount(db, request.state.log)


class CandidateAccountRequest(BaseModel):
    username: str = Field(pattern=Patterns.USERNAME, max_length=100)
    email: str = Field(pattern=Patterns.EMAIL, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(pattern=Patterns.NAME, max_length=100)
    last_name: str = Field(pattern=Patterns.NAME, max_length=100)
    degree: str = Field(pattern=Patterns.NAME, max_length=100)
    branch: str = Field(pattern=Patterns.NAME, max_length=100)
    cgpa: float = Field(ge=0, le=10)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit.')
        if not re.search(r'\W', value):
            raise ValueError('Password must contain at least one special character.')
        return value


class CandidateAccountResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str


@router.post(EndpointName.CANDIDATE, response_model=CandidateAccountResponse)
def create_candidate(candidate_account_request: CandidateAccountRequest,
                     account_creator: Annotated[CreateAccount, Depends(get_create_account)],
                     request: Request):

    logger = request.state.log

    candidate = dict(**candidate_account_request.model_dump())

    try:
        added_user = account_creator.create_candidate(candidate)
    except UsedUsernameException:
        detail = f"Username '{candidate['username']}' already exist."
        logger(

        )
        raise HTTPException(status_code=409, detail=f"Username '{candidate['username']}' already exist.")

    except UsedEmailException:
        raise HTTPException(status_code=400, detail=f"Email '{candidate['email']}' is in use.")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    else:
        return CandidateAccountResponse(**added_user)

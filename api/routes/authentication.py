from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from database_layer.database import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from buisness_layer.authentication import Authentication
from logger.logger import Logger


router = APIRouter(
    tags=['Authentication']
)

crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = "$2b$12$LNR07r5RZs2ECmVx0CiSvumyuCoL0VQJnSHVafdKC.ZksDdZbgjlS"
ALGORITHM = 'HS256'
TOKEN_EXP_TIME_MIN = 60 * 12


def get_authentication_logger() -> Logger:
    return Logger('./logger/logs.log', 'Authentication')


def get_authentication(db: Session = Depends(get_db),
                       log: Logger = Depends(get_authentication_logger)) -> Authentication:
    return Authentication(db, log)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get('/login', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 authenticator: Annotated[Authentication, Depends(get_authentication)]):
    user = authenticator.authenticate(username=form_data.username, password=form_data.password)
    if not user.get('is_valid'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

    username = user.get('username')
    user_id = user.get('id')
    role = user.get('role')
    approval_status = user.get('approval_status')
    token = create_access_token(username, user_id, role, approval_status, timedelta(minutes=TOKEN_EXP_TIME_MIN))
    return {'access_token': token, 'token_type': 'bearer'}


def create_access_token(username: str, user_id: int, role: str, approval_status: str, expires_date: timedelta):
    expires = datetime.now(timezone.utc) + expires_date
    encode = {'sub': username, 'id': user_id, 'role': role, 'approval_status': approval_status, 'exp': expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_admin(token: Annotated[str, Depends(oauth_bearer)]):
    return get_user(token, 'admin')


admin_auth_dependency = Annotated[dict, Depends(get_admin)]


def get_candidate(token: Annotated[str, Depends(oauth_bearer)]):
    return get_user(token, 'candidate')


candidate_auth_dependency = Annotated[dict, Depends(get_candidate)]


def get_placement_officer(token: Annotated[str, Depends(oauth_bearer)]):
    return get_user(token, 'placement officer')


placement_officer_auth_dependency = Annotated[dict, Depends(get_placement_officer)]


def get_user(token: str, expected_role: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        approval_status: str = payload.get('approval_status')
        if (
                username is None or user_id is None or
                role is None or role != expected_role or
                approval_status is None or approval_status != 'approved'
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='could not validate user')
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user')


def get_user2(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user')
    else:
        return payload

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette import status
from api.routes.authentication import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from typing import List
from logger.logger import Logger
import uuid
from constants import EndpointName, ResourceName

authorization_detail = {
    'no_auth': [ResourceName.HEALTH, ResourceName.LOGIN,
                ResourceName.CREATE_ACCOUNT],
    'admin': [ResourceName.APPROVAL],
    'candidate': [ResourceName.Question + EndpointName.ASK_QUESTION,
                  ResourceName.Question + EndpointName.VIEW_ASKED_QUESTIONS],
    'placement_officer': [ResourceName.Question + EndpointName.VIEW_ASKED_QUESTIONS,
                          ResourceName.Question + EndpointName.ANSWER_QUESTION]
}


class RoleAuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            path = request.url.path
            request.state.log = Logger('./log_data.log', str(uuid.uuid4()))

            if len(path) == 0:
                return

            if RoleAuthorizationMiddleware.start_with_any_of(path, authorization_detail['no_auth']):
                response = await call_next(request)
                return response

            user = RoleAuthorizationMiddleware.get_user(request)

            if (
                user['role'] == 'admin'
                and not RoleAuthorizationMiddleware.start_with_any_of(path, authorization_detail['admin'])
            ):
                raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
            elif (
                user['role'] == 'candidate'
                and not RoleAuthorizationMiddleware.start_with_any_of(path, authorization_detail['candidate'])
            ):
                raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
            elif (
                user['role'] == 'placement_officer'
                and not RoleAuthorizationMiddleware.start_with_any_of(path, authorization_detail['placement_officer'])
            ):
                raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")

            request.state.user_id = user['user_id']
            request.state.role = user['role']

        except HTTPException as exception:
            return JSONResponse(
                status_code=exception.status_code,
                content={"detail": exception.detail}
            )

        response = await call_next(request)
        return response

    @staticmethod
    def get_user(request: Request):
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Authorization header is missing')

        token = auth_header[len('Bearer '):]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            username: str = payload.get('sub')
            user_id: int = payload.get('id')
            role: str = payload.get('role')
            approval_status: str = payload.get('approval_status')
            if (
                    username is None or user_id is None
                    or role is None or approval_status is None
                    or approval_status != 'approved'
            ):
                raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='could not validate user')
        else:
            return dict(
                username=username,
                user_id=user_id,
                role=role
            )

    @staticmethod
    def start_with_any_of(path: str, allowed_paths: List[str]):
        for allowed_path in allowed_paths:
            if path.startswith(allowed_path):
                return True
        return False

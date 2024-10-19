from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette import status
from api.routes.authentication import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from logger.logger import Logger
from constants import EndpointName, ResourceName, RoleName, HttpErrorException
import datetime

SECURED_ENDPOINTS = {
    'GET': {
        EndpointName.VIEW_ASKED_QUESTIONS: [
            RoleName.PLACEMENT_OFFICER,
            RoleName.CANDIDATE
        ],
        EndpointName.VIEW_ACCOUNTS: [
            RoleName.ADMIN
        ],
        EndpointName.JOBS: [
            RoleName.PLACEMENT_OFFICER,
            RoleName.CANDIDATE
        ],
        EndpointName.JOB_APPLICANTS: [
            RoleName.PLACEMENT_OFFICER
        ],
        EndpointName.GET_MESSAGES: [
            RoleName.CANDIDATE
        ]
    },
    'POST': {
        EndpointName.ASK_QUESTION: [
            RoleName.CANDIDATE
        ],
        EndpointName.JOB: [
            RoleName.PLACEMENT_OFFICER
        ],
        EndpointName.APPLY_JOB: [
            RoleName.CANDIDATE
        ]
    },
    'PATCH': {
        EndpointName.ANSWER_QUESTION: [
            RoleName.PLACEMENT_OFFICER
        ],
        EndpointName.DECIDE_APPROVAL_STATUS: [
            RoleName.ADMIN
        ],
        EndpointName.MOVE_JOB: [
            RoleName.PLACEMENT_OFFICER
        ]
    }
}


class RoleAuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        http_method = request.method
        clint_ip = request.client.host
        clint_port = request.client.port

        logger = Logger(log_file='./logger/log_data.log',
                        log_name=f'{clint_ip}:{clint_port} - {http_method} {path}')
        request.state.log = logger

        logger.log('Request initiated.')

        try:
            endpoints = SECURED_ENDPOINTS[http_method].keys()
            flag = True
            for endpoint in endpoints:
                if RoleAuthorizationMiddleware.is_matched(endpoint, path):
                    logger.log('Request require authorization.')
                    flag = False
                    user = RoleAuthorizationMiddleware.get_user(request, logger)

                    if user['role'] not in SECURED_ENDPOINTS[http_method][endpoint]:
                        logger.log('Authorization failed.', 'warning')
                        raise HttpErrorException.STATUS_403

                    logger.log('Authorization successful.')
                    request.state.user_id = user['user_id']
                    request.state.role = user['role']
                    logger.log(f"User id is '{user['user_id']}' and role is '{user['role']}'")

            if flag:
                logger.log("Request don't required authorization.")

        except HTTPException as exception:
            return JSONResponse(
                status_code=exception.status_code,
                content={"detail": exception.detail}
            )
        except Exception as exception:
            logger.log(
                message=f"Unexpected error occurred => {str(exception)}",
                level='error'
            )
            raise HttpErrorException.STATUS_500
        else:
            logger.log('Request sent to endpoint.')

            request_sent_time = datetime.datetime.now(datetime.UTC)
            response = await call_next(request)
            response_received_time = datetime.datetime.now(datetime.UTC)
            time_taken = response_received_time - request_sent_time

            if response.status_code == 422:
                logger.log(f'Request data formate is invalid')

            logger.log(f'Response received from endpoint with status code = {response.status_code}')
            logger.log('Response received from endpoint')
            logger.log(f"Time taken to process request by endpoint '{time_taken}'.")

            return response
        finally:
            logger.log('Response is returned successfully.')

    @staticmethod
    def get_user(request: Request, logger: Logger):
        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Bearer '):
            logger.log('Authorization header is missing.', 'warning')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Authorization header is missing.')

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
            ):
                logger.log('Missing information in token payload.', 'warning')
                raise HttpErrorException.STATUS_403
            if approval_status != 'approved':
                logger.log('User is not approved.', 'warning')
                raise HttpErrorException.STATUS_403
        except JWTError:
            logger.log('Failed to decode token.', 'warning')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        else:
            return dict(
                username=username,
                user_id=user_id,
                role=role
            )

    @staticmethod
    def is_matched(endpoint, path):
        endpoint = endpoint.lstrip('/').split('/')
        path = path.lstrip('/').split('/')

        if len(endpoint) != len(path):
            return False

        for i, j in zip(endpoint, path):
            if i[0] != '{' and i != j:
                return False

        return True

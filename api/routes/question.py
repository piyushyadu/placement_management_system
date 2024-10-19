from fastapi import APIRouter, Depends, Query, Request, status, Path, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from typing import Union
from buisness_layer.candidate import Candidate
from buisness_layer.job import Job
from api.request_response import QuestionAskRequest, QuestionDataResponse, QuestionAnswerRequest
from exceptions.exceptions import DatabaseException, QuestionNotFoundException
from constants import ResourceName, EndpointName, RoleName, HttpErrorException
from logger.logger import Logger

router = APIRouter(
    tags=['Question']
)


def get_user(db: Annotated[Session, Depends(get_db)],
             request: Request):
    if request.state.role == RoleName.PLACEMENT_OFFICER:
        return Job(db, request.state.log, request.state.user_id)
    elif request.state.role == RoleName.CANDIDATE:
        return Candidate(db, request.state.log, request.state.user_id)


user_dependency = Annotated[Union[Job, Candidate], Depends(get_user)]


@router.post(EndpointName.ASK_QUESTION, status_code=status.HTTP_201_CREATED)
def post_question(question_request: QuestionAskRequest,
                  user_functionality: user_dependency,
                  request: Request):
    logger: Logger = request.state.log
    try:
        question = user_functionality.post_question(question_request.question)
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        logger.log(
            message='Unknown error occurred.',
            level='error'
        )
        raise HttpErrorException.STATUS_500
    else:
        logger.log(
            message='Successful response from endpoint is returned.',
            level='info'
        )
        return question


@router.get(EndpointName.VIEW_ASKED_QUESTIONS, status_code=status.HTTP_200_OK)
def get_questions(user_functionality: user_dependency,
                  request: Request,
                  page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):

    logger: Logger = request.state.log
    offset_count = (page - 1) * elements
    limit_count = elements
    try:
        if request.state.role == RoleName.CANDIDATE:
            question_list = user_functionality.get_question_responses(offset_count, limit_count)
        elif request.state.role == RoleName.PLACEMENT_OFFICER:
            question_list = user_functionality.get_pending_questions(offset_count, limit_count)
        else:
            raise HttpErrorException.STATUS_501
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        logger.log(
            message='Unknown error occurred.',
            level='error'
        )
        raise HttpErrorException.STATUS_500
    else:
        logger.log(
            message='Successful response from endpoint is returned.',
            level='info'
        )
        return question_list


@router.patch(EndpointName.ANSWER_QUESTION, response_model=QuestionDataResponse)
def answer_question(user_functionality: user_dependency,
                    question_request: QuestionAnswerRequest,
                    request: Request,
                    question_id: int = Path(gt=0, lt=10**8)):

    logger = request.state.log
    try:
        answer_response = user_functionality.answer_asked_question(question_id, question_request.answer)
    except QuestionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Question id not found')
    except DatabaseException:
        raise HttpErrorException.STATUS_500
    except Exception:
        logger.log(
            message='Unknown error occurred.',
            level='error'
        )
        raise HttpErrorException.STATUS_500
    else:
        logger.log(
            message='Successful response from endpoint is returned.',
            level='info'
        )
        return QuestionDataResponse(**answer_response)

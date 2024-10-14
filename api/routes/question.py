from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import Annotated
from sqlalchemy.orm import Session
from database_layer.database import get_db
from typing import List, Union
from buisness_layer.candidate import Candidate
from buisness_layer.job import Job
from api.request_response import QuestionAskResponse, QuestionAskRequest, QuestionDataResponse, QuestionAnswerRequest
from exceptions.exceptions import DatabaseException
from constants import ResourceName, EndpointName, RoleName

router = APIRouter(
    prefix=ResourceName.Question,
    tags=['Question']
)


def get_user(db: Annotated[Session, Depends(get_db)],
             request: Request):
    if request.state.role == RoleName.PLACEMENT_OFFICER:
        return Job(db, request.state.log, request.state.user_id)
    elif request.state.role == RoleName.CANDIDATE:
        return Candidate(db, request.state.log, request.state.user_id)


user_dependency = Annotated[Union[Job, Candidate], Depends(get_user)]


@router.post(EndpointName.ASK_QUESTION, response_model=QuestionAskResponse)
def post_question(question_request: QuestionAskRequest,
                  user_functionality: user_dependency):
    try:
        question = user_functionality.post_question(question_request.question)
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error.')
    else:
        return QuestionAskResponse(**question)


@router.get(EndpointName.VIEW_ASKED_QUESTIONS, response_model=List[QuestionDataResponse])
def get_questions(user_functionality: user_dependency,
                  request: Request,
                  page: int = Query(1, gt=0), elements: int = Query(20, gt=0)):

    offset_count = (page - 1) * elements
    limit_count = elements
    try:
        if request.state.role == RoleName.CANDIDATE:
            question_list = user_functionality.get_question_responses(offset_count, limit_count)
        elif request.state.role == RoleName.PLACEMENT_OFFICER:
            question_list = user_functionality.get_pending_questions(offset_count, limit_count)
        else:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='Feature not implemented')
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error.')
    else:
        return question_list


@router.patch(EndpointName.ANSWER_QUESTION, response_model=QuestionDataResponse)
def answer_question(user_functionality: user_dependency,
                    question_request: QuestionAnswerRequest):
    try:
        answer_response = user_functionality.answer_asked_question(question_request.id, question_request.answer)
    except DatabaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error.')
    else:
        return QuestionDataResponse(**answer_response)

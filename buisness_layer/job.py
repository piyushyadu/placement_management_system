from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException
import datetime


class Job:
    def __init__(self, db: Session, logger: Logger, user_id):
        self.db = db
        self.logger = logger
        self.user_id = user_id

    def create_job_posting(self, job_details):
        applicable_branches = '|' + '|'.join(job_details.get('applicable_branches')) + '|'
        job_details['applicable_branches'] = applicable_branches
        job = models.Job(**job_details)
        try:
            self.db.add(job)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            raise exception
        else:
            self.db.refresh(job)
            added_job = Job.convert_orm_object_to_dict(job)
            return added_job

    @staticmethod
    def convert_orm_object_to_dict(orm_object):
        data = orm_object.__dict__
        data = {key: data[key] for key in data if key[0] != '_'}
        return data

    def get_pending_question_responses(self, offset_count: int, limit_count: int):
        try:
            questions = (
                self.db.query(models.Question)
                .order_by(desc(models.Question.asked_at))
                .filter(models.Question.response_status == 'pending')
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_all_question_responses',
                message=f'user(id:{self.user_id}) is unable to fetch questions asked by users from database',
                level='error'
            )
            raise exception

        questions_data = [question for question in questions]
        questions_data = list(map(Job.convert_orm_object_to_dict, questions_data))
        self.logger.log(
            component='get_all_question_responses',
            message=f'questions are returned successfully',
            level='info'
        )
        return questions_data

    def answer_asked_question(self, question_id: int, answer: str):
        try:
            question = (
                self.db.query(models.Question)
                .filter(models.Question.id == question_id)
                .first()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_all_question_responses',
                message=f'user(id:{self.user_id}) is unable to fetch question asked by users from database',
                level='error'
            )
            raise exception

        question.response_status = 'answered'
        question.answerer_id = self.user_id
        question.answered_at = datetime.datetime.now(datetime.UTC)
        question.answer = answer
        self.db.add(question)

        self.db.refresh(question)
        answered_question = Job.convert_orm_object_to_dict(question)
        return answered_question

    def get_job_postings(self, offset_count: int, limit_count: int):
        try:
            jobs = (
                self.db.query(models.Job)
                .order_by(asc(models.Job.application_closed_on))
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_job_postings',
                message=f'unable to fetch job postings from database',
                level='error'
            )
            raise exception

        jobs_data = [job for job in jobs]
        jobs_data = list(map(Job.convert_orm_object_to_dict, jobs_data))
        self.logger.log(
            component='get_job_postings',
            message='job postings are returned',
            level='info'
        )
        return jobs_data






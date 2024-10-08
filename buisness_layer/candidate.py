from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException
from exceptions.candidate_exceptions import NotApplicableJobException, ClosedJobException
import datetime


class Candidate:
    def __init__(self, db: Session, logger: Logger, user_id: int):
        self.db = db
        self.logger = logger
        self.user_id = user_id

    def post_question(self, question: str):
        new_question = models.Question(
            questioner_id=self.user_id,
            question=question
        )
        try:
            self.db.add(new_question)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            self.logger.log(
                component='post_question',
                message='unable to add a new question in database',
                level='error'
            )
            raise exception
        else:
            self.db.refresh(new_question)
            added_question = dict(id=new_question.id,
                                  questioner_id=new_question.questioner_id,
                                  question=new_question.question)
            self.logger.log(
                component='post_question',
                message=f'candidate(id={self.user_id}) has '
                        f'successfully asked a question(id={new_question.id})',
                level='info'
            )
            return added_question

    def get_question_responses(self, offset_count: int, limit_count: int):
        try:
            questions = (
                self.db.query(models.Question)
                .order_by(desc(models.Question.asked_at))
                .filter(models.Question.questioner_id == self.user_id)
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_question_responses',
                message=f'unable to fetch questions asked by user(id={self.user_id}) from database',
                level='error'
            )
            raise exception

        questions_data = [question for question in questions]
        questions_data = list(map(Candidate.convert_orm_object_to_dict, questions_data))
        self.logger.log(
            component='get_question_responses',
            message=f'response of questions are returned',
            level='info'
        )
        return questions_data

    @staticmethod
    def convert_orm_object_to_dict(orm_object):
        data = orm_object.__dict__
        data = {key: data[key] for key in data if key[0] != '_'}
        return data

    def get_mass_messages(self, offset_count: int, limit_count: int):
        try:
            messages = (
                self.db.query(models.MassMessageReceiver)
                .join(models.MassMessage, models.MassMessage.id == models.MassMessageReceiver.mass_message_id)
                .order_by(desc(models.MassMessageReceiver.message.sent_at))
                .filter(models.MassMessageReceiver.receiver_id == self.user_id)
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_mass_messages',
                message=f'unable to fetch mass message received by user(id={self.user_id}) from database',
                level='error'
            )
            raise exception

        messages_data = [message for message in messages]
        messages_data = list(map(Candidate.convert_orm_object_to_dict, messages_data))
        self.logger.log(
            component='get_mass_messages',
            message=f'received mass messages are returned',
            level='info'
        )
        return messages_data

    def get_applicable_job_postings(self, offset_count: int, limit_count: int):
        try:
            candidate = self.db.query(models.Candidate).filter(models.Candidate.user_id == self.user_id).first()
            branch_filter_string = '%|' + candidate.branch + '|%'
            jobs = (
                self.db.query(models.Job)
                .order_by(asc(models.Job.application_closed_on))
                .filter(models.Job.application_closed_on >= datetime.datetime.now(datetime.UTC))
                .filter(models.Job.applicable_degree == candidate.degree)
                .filter(models.Job.applicable_branches.like(branch_filter_string))
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_applicable_job_postings',
                message=f'unable to fetch job postings or candidate from database',
                level='error'
            )
            raise exception

        jobs_data = [job for job in jobs]
        jobs_data = list(map(Candidate.convert_orm_object_to_dict, jobs_data))
        self.logger.log(
            component='get_applicable_job_postings',
            message='applicable job postings are returned',
            level='info'
        )
        return jobs_data

    def apply_for_job(self, job_id: int):
        try:
            job = self.db.query(models.Job).filter(models.Job.id == job_id).first()
            candidate = self.db.query(models.Candidate).filter(models.Candidate == self.user_id).first()
        except DatabaseFetchException as exception:
            self.logger.log(
                component='apply_for_job',
                message=f'user(id={self.user_id}) is not able to fetch his data',
                level='error'
            )
            raise exception

        if not Candidate.is_job_open(job):
            raise ClosedJobException
        if not Candidate.is_user_applicable_for_job(job, candidate):
            raise NotApplicableJobException

        job_application = models.JobApplication(job_id=job_id, applicants_id=self.user_id)
        try:
            self.db.add(job_application)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            self.logger.log(
                component='apply_for_job',
                message=f'user(id={self.user_id}) is not able to apply for job',
                level='error'
            )
            raise exception
        else:
            self.db.refresh(job_application)
            added_job_application = dict(id=job_application.id,
                                         job_id=job_application.job_id,
                                         applicant_id=job_application.applicant_id)
            return added_job_application

    @staticmethod
    def is_job_open(job: models.Job):
        if job.application_closed_on < datetime.datetime.now(datetime.UTC):
            return False
        return True

    @staticmethod
    def is_user_applicable_for_job(job: models.Job, candidate: models.Candidate):
        if job.applicable_degree != candidate.degree:
            return False
        if candidate.branch not in job.applicable_branches.split(','):
            return False
        return True


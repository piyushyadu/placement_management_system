from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import (DatabaseAddException, DatabaseFetchException, JobNotFoundException,
                                   DatabaseDeleteException, QuestionNotFoundException)
from exceptions.job_exception import MoveOpenJobException, NoQualifiedApplicantsException
import datetime
from typing import List, Optional
from database_layer.database import Base


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
            self.logger.log('Trying to insert job data in db.')
            self.db.add(job)
            self.db.commit()
        except DatabaseAddException as exception:
            self.logger.log('Failed to insert job data in db.', 'error')
            self.db.rollback()
            self.logger.log('Query rollback completed.')
            raise exception
        else:
            self.logger.log('Job data inserted in db successfully.')
            self.db.refresh(job)
            self.logger.log('Retrieved job data from db.')
            added_job = Job.convert_orm_object_to_dict(job)
            added_job['applicable_branches'] = added_job.get('applicable_branches').lstrip('|').rstrip('|').split('|')
            self.logger.log('Returned created job data.')
            return added_job

    @staticmethod
    def convert_orm_object_to_dict(orm_object):
        data = orm_object.__dict__
        data = {key: data[key] for key in data if key[0] != '_'}
        return data

    def get_pending_questions(self, offset_count: int, limit_count: int):
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
                message='Unable to fetch data from db.',
                level='error'
            )
            raise exception
        else:
            self.logger.log(
                message='Questions are retrieved from db successfully.',
                level='info'
            )
            questions_data = [question for question in questions]
            questions_data = list(map(Job.convert_orm_object_to_dict, questions_data))
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
                message='Unable to fetch data from db.',
                level='error'
            )
            raise exception
        else:
            self.logger.log(
                message='Question is retrieved from db successfully.',
                level='info'
            )
        if not question:
            raise QuestionNotFoundException(question_id)
        try:
            question.response_status = 'answered'
            question.answerer_id = self.user_id
            question.answered_at = datetime.datetime.now(datetime.UTC)
            question.answer = answer
            self.db.add(question)
            self.db.commit()
        except DatabaseAddException as exception:
            self.logger.log(
                message='Unable to update data in db.',
                level='error'
            )
            raise exception
        else:
            self.logger.log(
                message='Question is answered successfully.',
                level='info'
            )
            self.db.refresh(question)
            answered_question = Job.convert_orm_object_to_dict(question)
            return answered_question

    def get_job_postings(self, offset_count: int, limit_count: int, conditions: dict):
        try:
            self.logger.log('Trying to retrieve job data from db.')
            jobs = self.db.query(models.Job)

            order_condition = conditions.get('order_by_application_closed_on')
            if order_condition:
                jobs = jobs.order_by(desc(models.Job.application_closed_on))
            else:
                jobs = jobs.order_by(desc(models.Job.posted_at))

            open_job = conditions.get('job_status')
            if open_job == 'open':
                jobs = jobs.filter(models.Job.application_closed_on >= datetime.datetime.now(datetime.UTC))
            elif open_job == 'closed':
                jobs = jobs.filter(models.Job.application_closed_on < datetime.datetime.now(datetime.UTC))

            company_name = conditions.get('company_name')
            if company_name:
                jobs = jobs.filter(models.Job.company_name.like(company_name + '%'))

            max_ctc = conditions.get('max_ctc')
            if max_ctc:
                jobs = jobs.filter(models.Job.ctc <= max_ctc)

            min_ctc = conditions.get('min_ctc')
            if min_ctc:
                jobs = jobs.filter(models.Job.ctc >= min_ctc)

            jobs = jobs.offset(offset_count).limit(limit_count).all()
        except DatabaseFetchException as exception:
            self.logger.log('Failed to retrieve job data from db.', 'error')
            raise exception
        else:
            self.logger.log('Successfully retrieved job data from db.')

        jobs_data = [Job.convert_orm_object_to_dict(job) for job in jobs]
        for job_data in jobs_data:
            job_data['applicable_branches'] = job_data.get('applicable_branches').lstrip('|').rstrip('|').split('|')
        self.logger.log('Successfully returned list of job posting.')
        return jobs_data

    def get_job_applicants(self, job_id: int, offset_count: int, limit_count: int):
        try:
            job_applicants = (self.db.query(models.JobApplication)
                              .filter(models.JobApplication.job_id == job_id)
                              .offset(offset_count)
                              .limit(limit_count)
                              .all())
        except DatabaseFetchException as exception:
            raise exception

        job_applicants = [job_applicant.applicant for job_applicant in job_applicants]
        job_applicants = list(map(Job.convert_orm_object_to_dict, job_applicants))

        return job_applicants

    def move_job_next_round(self, job_id: int, applicants_id_list: List[int], message: str):
        try:
            job = self.db.query(models.Job).filter(models.Job.id == job_id).first()
        except DatabaseFetchException as exception:
            raise exception

        if job is None:
            raise JobNotFoundException(job_id)
        if not Job.is_job_open(job):
            raise MoveOpenJobException(job_id)

        try:
            job_applications = (self.db.query(models.JobApplication)
                                .filter(models.JobApplication.job_id == job_id).all())
        except DatabaseFetchException as exception:
            raise exception

        applicants_id_list = set(applicants_id_list)
        selected_applicants_id_list = []
        for job_application in job_applications:
            if job_application.applicant_id in applicants_id_list:
                applicants_id_list.remove(job_application.applicant_id)
                selected_applicants_id_list.append(job_application.applicant_id)
            else:
                self.delete_orm_objects(job_application)

        if len(selected_applicants_id_list) == 0:
            try:
                self.delete_orm_objects(job)
            except DatabaseDeleteException as exception:
                self.db.rollback()
                raise exception
            raise NoQualifiedApplicantsException(job_id)

        mass_message_data = dict(
            message=message,
            job_id=job_id,
            sender_id=self.user_id
        )
        mass_message = models.MassMessage(**mass_message_data)

        try:
            self.db.add(mass_message)
            self.db.commit()
            self.db.refresh(mass_message)
            for selected_applicant_id in selected_applicants_id_list:
                mass_message_receiver_data = dict(
                    mass_message_id=mass_message.id,
                    receiver_id=selected_applicant_id
                )
                mass_message_receiver = models.MassMessageReceiver(**mass_message_receiver_data)
                self.db.add(mass_message_receiver)
                self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            raise exception
        job_status = 'in_progress'
        current_round = job.current_round + 1
        if current_round > job.total_round_count:
            job_status = 'completed'
            try:
                self.delete_orm_objects(job)
            except DatabaseDeleteException as exception:
                raise exception
            return dict(
                job_id=job_id,
                selected_applicants_id=selected_applicants_id_list,
                message=message,
                job_status=job_status
            )

        try:
            job.current_round += 1
            self.db.add(job)
            self.db.commit()
        except DatabaseAddException as exception:
            raise exception
        next_round_data = dict(
            job_id=job_id,
            selected_applicants_id=selected_applicants_id_list,
            message=message,
            job_status=job_status
        )
        if len(applicants_id_list) != 0:
            next_round_data['warning'] = "Applicants who was not in previous round is not allowed to be in next round."
        print(next_round_data)
        return next_round_data

    @staticmethod
    def is_job_open(job: models.Job):
        application_closed_on = job.application_closed_on.replace(tzinfo=datetime.timezone.utc)
        if application_closed_on < datetime.datetime.now(datetime.UTC):
            return False
        return True

    def delete_orm_objects(self, orm_objects: Base):
        try:
            self.db.delete(orm_objects)
            self.db.commit()
        except DatabaseDeleteException as exception:
            self.db.rollback()
            raise exception

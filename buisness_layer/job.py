from sqlalchemy.orm import Session
from sqlalchemy import desc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException


class Job:
    def __init__(self, db: Session, logger: Logger, user_id: int):
        self.db = db
        self.logger = logger
        self.user_id = user_id

    def create_job_posting(self, job_details):
        job = models.Job(**job_details)
        try:
            self.db.add(job)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            self.logger.log(
                component='create_job_posting',
                message='unable to insert new job posting in database',
                level='error'
            )
            raise exception
        else:
            self.db.refresh(job)
            added_job = dict(id=job.id, company_name=job.company_name)
            return added_job



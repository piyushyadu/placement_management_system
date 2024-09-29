from sqlalchemy.orm import Session
from sqlalchemy import desc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException


class Admin:
    def __init__(self, db: Session, logger: Logger, user_id: int):
        self.db = db
        self.logger = logger
        self.user_id = user_id

    def get_unapproved_account(self, offset_count: int, limit_count: int):
        try:
            users = (
                self.db.query(models.User)
                .order_by(desc(models.User.created_at))
                .filter(models.User.approval_status == 'pending')
                .offset(offset_count)
                .limit(limit_count)
                .all()
            )
        except DatabaseFetchException as exception:
            self.logger.log(
                component='get_unapproved_account',
                message='unable to fetch unapproved account from database',
                level='error'
            )
            raise exception

        users_data = [user for user in users]
        users_data = list(map(Admin.convert_orm_object_to_dict, users_data))
        self.logger.log(
            component='get_unapproved_account',
            message=f'unapproved accounts are returned',
            level='info'
        )
        return users_data

    @staticmethod
    def convert_orm_object_to_dict(orm_object):
        data = orm_object.__dict__
        data = {key: data[key] for key in data if key[0] != '_'}
        return data

    def set_account_approval_status(self, account_id: int, approval_status: str):
        try:
            user = self.db.query(models.User).filter(models.User.id == account_id).first()
        except DatabaseFetchException as exception:
            self.logger.log(
                component='set_account_approval_status',
                message=f'unable to set status of user(id:{account_id}) to status:{approval_status} in database',
                level='error'
            )
            raise exception

        user.approval_status = approval_status
        try:
            self.db.add(user)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            self.logger.log(
                component='set_account_approval_status',
                message='unable to set approval status in database',
                level='error'
            )
            raise exception
        else:
            self.db.refresh(user)
            approved_user = dict(id=user.id,
                                 username=user.username,
                                 approval_status=user.approval_status)
            self.logger.log(
                component='post_question',
                message=f'status of user({user.id}) is set to {user.approval_status}',
                level='info'
            )
            return approved_user

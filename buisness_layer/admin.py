from sqlalchemy.orm import Session
from sqlalchemy import desc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseAddException, DatabaseFetchException, UserNotFoundException
from exceptions.admin_exceptions import SelfStatusSetException


class Admin:
    def __init__(self, db: Session, logger: Logger, user_id: int):
        self.db = db
        self.logger = logger
        self.user_id = user_id

    def get_unapproved_accounts(self, offset_count: int, limit_count: int):
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
            raise exception

        users_data = [user for user in users]
        users_data = list(map(Admin.convert_orm_object_to_dict, users_data))
        for user_data in users_data:
            user_data.pop('hashed_password', None)
        return users_data

    @staticmethod
    def convert_orm_object_to_dict(orm_object):
        data = orm_object.__dict__
        data = {key: data[key] for key in data if key[0] != '_'}
        return data

    def set_account_approval_status(self, account_id: int, approval_status: str):
        if account_id == self.user_id:
            raise SelfStatusSetException(self.user_id)
        try:
            user = self.db.query(models.User).filter(models.User.id == account_id).first()
        except DatabaseFetchException as exception:
            raise exception

        if user is None:
            raise UserNotFoundException(self.user_id)
        user.approval_status = approval_status
        try:
            self.db.add(user)
            self.db.commit()
        except DatabaseAddException as exception:
            self.db.rollback()
            raise exception
        else:
            self.db.refresh(user)
            approved_user = dict(id=user.id,
                                 username=user.username,
                                 approval_status=user.approval_status)
            return approved_user

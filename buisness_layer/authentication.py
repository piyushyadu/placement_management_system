from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from logger.logger import Logger
from database_layer import models
from exceptions.exceptions import DatabaseFetchException
from buisness_layer.create_account import crypt_context


class Authentication:
    def __init__(self, db: Session, logger: Logger):
        self.db = db
        self.logger = logger

    def authenticate(self, username: str, password: str):
        try:
            user = self.db.query(models.User).filter(models.User.username == username).first()
        except DatabaseFetchException as exception:
            raise exception

        if not user:
            return dict(is_valid=False)

        if not crypt_context.verify(password, user.hashed_password):
            return dict(is_valid=False)

        return dict(is_valid=True, username=user.username,
                    id=user.id, role=user.role, approval_status=user.approval_status)

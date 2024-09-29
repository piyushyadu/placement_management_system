from sqlalchemy.orm import Session
from logger.logger import Logger
from exceptions.exceptions import DatabaseAddException
from exceptions.candidate_exceptions import UsedUsernameException, UsedEmailException
from database_layer import models
from passlib.context import CryptContext


crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class CreateAccount:
    def __init__(self, db: Session, logger: Logger):
        self.db = db
        self.logger = logger

    def create_candidate(self, candidate: dict):
        """
        Create a new candidate based on provided candidate details.
        :param candidate: A dictionary containing candidate details.
            The expected keys are:
            - username (str): username of candidate.
            - email (str): email of candidate.
            - password (str): password created by candidate.
            - first_name (str): first name of candidate.
            - last_name (str): last name of candidate.
            - degree (str): degree which candidate is pursuing.
            - branch (str): branch which candidate is studying.
            - cgpa (float): current cgpa of candidate.
        :type candidate: dict
        :return: A dictionary containing id, username, email and role of created candidate
        :rtype: dict
        :raise UsedUsernameException: If username is used to create other account.
        :raise UsedEmailException: If email is used to create other account.
        :raise DatabaseAddException: If got any error while inserting data in database.
        """
        username: str = candidate.get('username')
        user_model = self.db.query(models.User).filter(models.User.username == username).first()
        if user_model is not None:
            raise UsedUsernameException

        email: str = candidate.get('email')
        user_model = self.db.query(models.User).filter(models.User.email == email).first()
        if user_model is not None:
            raise UsedEmailException

        new_user_data = dict(username=candidate.get('username'),
                             email=candidate.get('email'),
                             hashed_password=crypt_context.hash(candidate.get('password')),
                             first_name=candidate.get('first_name'),
                             last_name=candidate.get('last_name'),
                             role='candidate')
        new_candidate_data = dict(degree=candidate.get('degree'),
                                  branch=candidate.get('branch'),
                                  cgpa=candidate.get('cgpa'))
        try:
            new_user = models.User(**new_user_data)
            new_candidate = models.Candidate(**new_candidate_data)
            new_user.candidate = new_candidate
            self.db.add(new_user)
            self.db.commit()
        except DatabaseAddException as e:
            self.db.rollback()
            self.logger.log(
                component='create_candidate',
                message='unable to insert insert data in table',
                level='error'
            )
            raise e
        else:
            self.db.refresh(new_user)
            added_user = dict(id=new_user.id,
                              newusername=new_user.username,
                              email=new_user.email,
                              role=new_user.role)
            self.logger.log(
                component='create_candidate',
                message=f'new user(id={new_user.id}) is successfully created',
                level='info'
            )
            return added_user

from database_layer.database import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
import datetime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    approval_status = Column(String, default='pending')
    role = Column(String, nullable=False)

    candidate = relationship('Candidate', back_populates='user', uselist=False)
    asked_question = relationship('Question',
                                  foreign_keys='Question.questioner_id',
                                  back_populates='questioner')
    answered_question = relationship('Question',
                                     foreign_keys='Question.answerer_id',
                                     back_populates='answerer')
    applied_jobs = relationship('JobApplication', back_populates='applicant')
    sent_mass_messages = relationship('MassMessage', back_populates='sender')
    received_mass_messages = relationship('MassMessageReceiver', back_populates='receiver')


class Candidate(Base):
    __tablename__ = 'candidate'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True, index=False)
    degree = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    cgpa = Column(Float, nullable=False)

    user = relationship('User', back_populates='candidate')


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, index=True)
    questioner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    asked_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    question = Column(String, nullable=False)
    response_status = Column(String, default='pending')
    answerer_id = Column(Integer, ForeignKey('user.id'))
    answered_at = Column(DateTime)
    answer = Column(String)

    questioner = relationship('User',
                              foreign_keys=[questioner_id],
                              back_populates='asked_question')
    answerer = relationship('User',
                            foreign_keys=[answerer_id],
                            back_populates='answered_question')


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True, index=True)
    posted_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    company_name = Column(String, nullable=False)
    job_description = Column(String, nullable=False)
    ctc = Column(Float, nullable=False)
    applicable_degree = Column(String, nullable=False)
    applicable_branches = Column(String, nullable=False)
    total_round_count = Column(Integer, nullable=False)
    current_round = Column(Integer, default=0)
    application_closed_on = Column(DateTime, nullable=False)

    applicants = relationship('JobApplication', back_populates='job')
    related_mass_messages = relationship('MassMessage', back_populates='related_job')


class JobApplication(Base):
    __tablename__ = 'job_application'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('job.id'))
    applicant_id = Column(Integer, ForeignKey('user.id'))

    job = relationship('Job', back_populates='applicants')
    applicant = relationship('User', back_populates='applied_jobs')


class MassMessage(Base):
    __tablename__ = 'mass_message'

    id = Column(Integer, primary_key=True, index=True)
    sent_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    message = Column(String, nullable=False)
    job_id = Column(Integer, ForeignKey('job.id'))
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    receivers = relationship('MassMessageReceiver', back_populates='message')
    sender = relationship('User', back_populates='sent_mass_messages')
    related_job = relationship('Job', back_populates='related_mass_messages')


class MassMessageReceiver(Base):
    __tablename__ = 'mass_message_receiver'

    id = Column(Integer, primary_key=True, index=True)
    mass_message_id = Column(Integer, ForeignKey('mass_message.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))

    message = relationship('MassMessage', back_populates='receivers')
    receiver = relationship('User', back_populates='received_mass_messages')

from database_layer.database import engine, get_db
from database_layer import models
from logger.logger import Logger
from buisness_layer.create_account import CreateAccount
from buisness_layer.candidate import Candidate
from buisness_layer.admin import Admin
from buisness_layer.job import Job


models.Base.metadata.create_all(bind=engine)

db = get_db()

a=None

# candidate = CreateAccount(next(db), Logger('logger/create_account_log.log', 'CreateAccount'))
# a = dict(username='faraaz',
#          email='faraaz@gmail.com',
#          password='root',
#          first_name='faraaz',
#          last_name='zaidi',
#          degree='B.Tech',
#          branch='cse',
#          cgpa=9.2)
# a=candidate.create_candidate(a)

candidate = Candidate(next(db), Logger('logger/candidate_log.log', 'Candidate'), 1)
# a=candidate.post_question('watchGuard interview in which room?')
# a=candidate.get_question_responses(0, 10)
a=candidate.get_applicable_job_postings(0, 10)

# admin = Admin(next(db), Logger('logger/admin_log.log', 'Admin'), 1)
# a=admin.set_account_approval_status(1, 'approved')

# import datetime
# job = Job(next(db), Logger('logger/job_log.log', 'Job'), 1)
# job_detail = dict(
#     company_name='watchGuard',
#     job_description='sde role',
#     ctc=9.43,
#     applicable_degree='bachelor of technology',
#     applicable_branches=['computer science and engineering', 'mechanical engineering'],
#     total_round_count=3,
#     application_closed_on=datetime.datetime.now(datetime.UTC)+datetime.timedelta(days=5)
# )
# a = job.create_job_posting(job_detail)

from pprint import pprint
pprint(a)
print("done")
print('done')

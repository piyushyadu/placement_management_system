from database_layer.database import engine, get_db
from database_layer import models
from logger.logger import Logger
from buisness_layer.create_account import CreateAccount
from buisness_layer.candidate import Candidate
from buisness_layer.admin import Admin


models.Base.metadata.create_all(bind=engine)

db = get_db()

a=None
# candidate = CreateAccount(next(db), Logger('logger/candidate_log.log', 'Candidate'))
#
# a = dict(username='faraaz',
#          email='faraaz@gmail.com',
#          password='root',
#          first_name='faraaz',
#          last_name='zaidi',
#          degree='B.Tech',
#          branch='cse',
#          cgpa=9.2)
# a=candidate.create_candidate(a)

# candidate = Candidate(next(db), Logger('logger/candidate_log.log', 'Candidate'), 1)
# # a=candidate.post_question('watchGuard interview when?')
# a=candidate.get_question_responses(0, 10)

admin = Admin(next(db), Logger('logger/admin_log.log', 'Candidate'), 1)
a=admin.set_account_approval_status(2, 'approved')

print(a)
print("done")

from database_layer.database import engine, get_db
from database_layer import models
from logger.logger import Logger
from buisness_layer.create_account import CreateAccount
from buisness_layer.candidate import Candidate
from buisness_layer.admin import Admin


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

# candidate = Candidate(next(db), Logger('logger/candidate_log.log', 'Candidate'), 1)
# a=candidate.post_question('watchGuard interview in which room?')
# a=candidate.get_question_responses(0, 10)

admin = Admin(next(db), Logger('logger/admin_log.log', 'Admin'), 1)
a=admin.set_account_approval_status(1, 'approved')

from pprint import pprint
pprint(a)
print("done")

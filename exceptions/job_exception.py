
class JobException(Exception):
    pass


class MoveOpenJobException(JobException):
    def __init__(self, job_id):
        super().__init__(f"Can't move open job '{job_id}' for next round")


class NoQualifiedApplicantsException(JobException):
    def __init__(self, job_id):
        super().__init__(f"No qualified applicants for job '{job_id}'")

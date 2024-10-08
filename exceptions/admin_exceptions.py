
class AdminException(Exception):
    """Base class for all candidate related exception"""
    pass


class SelfStatusSetException(AdminException):
    def __init__(self, admin_id):
        super().__init__(f"admin(id={admin_id}) can't modify his own status")

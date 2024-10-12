
class Patterns:
    USERNAME = r'^[a-zA-Z][a-zA-Z0-9_.]{5,29}$'
    EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    NAME = r"^[a-zA-Z\s]{1,50}$"



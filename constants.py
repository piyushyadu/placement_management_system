
class Patterns:
    USERNAME = r'^[a-zA-Z][a-zA-Z0-9_.]{2,29}$'
    EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
    NAME = r"^[a-zA-Z]{1,50}$"


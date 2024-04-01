from database_handler import Database
from load_resources import ResourceValues

class UserHandler():
    def __init__(self):
        self.db = Database(ResourceValues.database_file)

    @staticmethod
    def validate_username_string(username):
        if username and len(username.strip()) > 4:
            return True
        else:
            raise Exception(ResourceValues.invalid_username_error)

    @staticmethod
    def validate_password_string(password):
        if password and len(password.strip()) > 6:
            return True
        else:
            raise Exception(ResourceValues.invalid_password_error)

    def username_exist(self, username):
        if not self.db.username_exists(username):
            raise Exception(ResourceValues.username_does_not_exist_error)

    def login(self, username, password):
        self.validate_username_string(username)
        self.validate_password_string(password)

        self.username_exist(username)

        if self.db.verify_password(username, password):
            return True

        else:
            raise Exception(ResourceValues.incorrect_login_details_error)



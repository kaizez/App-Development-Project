import hashlib
import time

class User:
    def __init__(self, email, username, password, user_id=None, last_login=None, status='active', is_admin=False):
        self.__email = email
        self.__username = username
        self.__password = password
        self.__user_id = user_id or str(int(time.time()))
        self.__last_login = last_login or time.time()
        self.__status = status
        self.__is_admin = is_admin

    # Getters
    def get_email(self):
        return self.__email

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_user_id(self):
        return self.__user_id

    def get_last_login(self):
        return self.__last_login

    def get_status(self):
        return self.__status

    def is_admin(self):
        return self.__is_admin

    # Setters
    def set_username(self, username):
        self.__username = username

    def set_status(self, status):
        self.__status = status

    def set_last_login(self, last_login):
        self.__last_login = last_login

    def set_admin(self, is_admin):
        self.__is_admin = is_admin

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, input_password):
        return self.__password == self.hash_password(input_password)

    def update_last_login(self):
        self.__last_login = time.time()

    def to_dict(self):
        return {
            'email': self.__email,
            'username': self.__username,
            'password': self.__password,
            'user_id': self.__user_id,
            'last_login': self.__last_login,
            'status': self.__status,
            'is_admin': self.__is_admin
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            user_id=data['user_id'],
            last_login=data['last_login'],
            status=data['status'],
            is_admin=data.get('is_admin', False)  # Default to False for backward compatibility
        )
from models.UserOut import UserOut


class SystemUser(UserOut):
    password: str
    role: str
    fullname: str
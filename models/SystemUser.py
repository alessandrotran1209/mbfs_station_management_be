from models.UserOut import UserOut
from typing import Union


class SystemUser(UserOut):
    password: str
    role: str
    fullname: str
    group: Union[str, None]
from uuid import UUID

from pydantic import BaseModel


class UserOut(BaseModel):
    username: str

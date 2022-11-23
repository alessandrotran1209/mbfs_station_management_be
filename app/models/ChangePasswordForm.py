from pydantic import BaseModel

class ChangePasswordForm(BaseModel):
    password: str
    newPassword: str
    dupNewPassword: str

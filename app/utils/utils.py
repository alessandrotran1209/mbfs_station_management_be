from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQCLwRUH/gyLAIZx/5/wlgGQvE+UUNvzOn9xoAmM1Be4qcsx4fsnYxOYLYG3GTxX9jLsefo6zhx5evTlZWDLFBFUlW7bHYTauo9cxRNWYrWQ33QcWvVH/fOl5UKd3pGKRbocpwhvwgyKH1N/nN8EgSnE3DiFfykrHDGGrbcy8yldYaj52C2fzaFc8Hm5AaWV030DcQshDwMlLHDXht6irk/DGf1wE4Zw4/4EPR9md5sVIQUkqoaWrP3OdPadRWsLoPSHPdloIl2wJx5KEj9eP0QO0FAEG/w1DRVe6Pti+yEBjtp123V5XYgHs91azaHOMhcECzShTprI9tkkB7GQKhFt'   # should be kept secret
JWT_REFRESH_SECRET_KEY = "AAAAB3NzaC1yc2EAAAADAQABAAABAQCr3kp2zb+4CdNL522znsn/ImlEB3nGeJtbJ0Ps6Q0g3z1fSYq43esm4aUvM8inInUDLHPOiNnV02nP4VGDMbhkU575DZTwmQ6uGawhCicHE3gEdwmK0yzH5nqoajfxdo45rCKN953P5v17QHBdvKhCoWJG6jl395BJWjThNZQu7vEd9+/SENINAa7Pz48rmV7ejVpvQUeDlQ8zlsCqsCTSKqt5GOIl+YEZ0I4b8F3qkUx+LJMxaD2I8vFIow3C2rS/bZyj7sjpjQ6wUVlR6FPg0j1Bd5hI2sOHjEdCDb8XWGWt6LUPiB764o11ZFe0Q1VHKu9M/q6AWctE3lEyoxfD"    # should be kept secret

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: int = None, role: str = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None, role: str = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

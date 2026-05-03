from jose import jwt
from datetime import datetime, timedelta

from src.utils.settings import Settings

SECRET_KEY = Settings.SECRET_KEY  # ⚠️ change this
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2400


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
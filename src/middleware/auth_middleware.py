from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.utils.security.auth import bearer_scheme
from src.utils.security.jwt import verify_access_token
from src.utils.db.session import get_db
from src.models.user import User
from src.utils.exception.custom_exception import CustomException


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),

):

    token = credentials.credentials

    payload = verify_access_token(token)

    if not payload:
        raise CustomException(
            statusCode=401,
            message="Invalid or expired token"
        )

    user_id = payload.get("sub")


    if not user_id:
        raise CustomException(
            statusCode=401,
            message="User not found"
        )

    return user_id
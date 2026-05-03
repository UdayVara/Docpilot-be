from fastapi import HTTPException
from sqlalchemy.orm import Session

from User.Schema.LoginSchema import LoginSchema
from src.models.user import User
from src.User.Schema.SignupSchema import SignupSchema
from src.utils.security.jwt import create_access_token
from src.utils.security.security import hash_password,verify_password


def sign_up(body: SignupSchema, db: Session):

    existing_user = db.query(User).filter(User.email == body.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=body.name,
        email=body.email,
        password=hash_password(body.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔹 create token
    token = create_access_token({
        "sub": str(new_user.id),
        "email": new_user.email
    })

    return {
        "message": "User created",
        "access_token": token,
        "statusCode": 201,
    }



def login(body:LoginSchema, db: Session):

    # 🔹 find user
    user = db.query(User).filter(User.email == body.Email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # 🔹 verify password
    if not verify_password(body.Password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # 🔹 generate token
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "statusCode": 200,
    }
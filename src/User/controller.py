from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.User.Schema.LoginSchema import LoginSchema
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



def loginService(body:LoginSchema, db: Session):
    print("Inside loginService")
    # 🔹 find user
    existing_user = db.query(User).filter(User.email == body.email).first()
    print("User : ",existing_user)
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    verifyPassResult = verify_password(body.password, existing_user.password)
    print("result:",verifyPassResult)
    # 🔹 verify password
    if not verify_password(body.password, existing_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # 🔹 generate token
    token = create_access_token({
        "sub": str(existing_user.id),
        "email": existing_user.email
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "statusCode": 200,
        "user":existing_user
    }
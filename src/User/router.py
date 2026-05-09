from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from src.utils.db.session import get_db
from src.User.Schema.SignupSchema import SignupSchema
from src.User.Schema.LoginSchema import LoginSchema
from src.User.controller import sign_up,loginService
router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.post("/signup",description="Sign Up")
def signup(body:SignupSchema,db: Session = Depends(get_db)):
    return sign_up(body,db)

@router.post("/login",description="Login")
def login(body:LoginSchema,db: Session = Depends(get_db)):
    print(f"Email : {body.email}, password : {body.password}")
    return loginService(body,db)
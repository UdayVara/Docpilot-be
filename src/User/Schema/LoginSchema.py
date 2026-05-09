from pydantic import EmailStr, BaseModel, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password:str = Field(min_length=8, max_length=20)
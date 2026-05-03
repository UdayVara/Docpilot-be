from pydantic import EmailStr, BaseModel, Field


class LoginSchema(BaseModel):
    Email: EmailStr
    Password:str = Field(min_length=8, max_length=20)
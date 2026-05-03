from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class SignupSchema(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=8, max_length=20)
    email: EmailStr
    phone: str

    # 🔹 Phone validation
    @field_validator("phone")
    def validate_phone(cls, value):
        if not re.fullmatch(r"^[6-9]\d{9}$", value):
            raise ValueError("Invalid phone number")
        return value

    # 🔹 Password validation
    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Must contain at least one number")
        return value
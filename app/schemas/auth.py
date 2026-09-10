from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)


class AdminUserResponse(BaseModel):
    email: EmailStr
    role: str

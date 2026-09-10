from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    message: str = Field(min_length=10, max_length=4000)


class ContactResponse(BaseModel):
    id: int
    message: str


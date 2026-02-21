from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    org_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    name: str
    role: str
    org_id: str

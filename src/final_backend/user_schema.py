from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class UserCreate(BaseModel):
    num: int
    username: str
    password: str
    password2: str
    email: EmailStr

    @field_validator("username", "email", "password", check_fields=False)
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @field_validator("password2")
    def passwords_match(cls, v, info: FieldValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class UserUpdate(BaseModel):
    username: str = None
    password: str = None
    email: EmailStr = None

    @field_validator("username", "password", "email", check_fields=False)
    def not_empty(cls, v):
        if v and not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

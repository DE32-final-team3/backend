from pydantic import BaseModel, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


# 사용자 생성 시 필요한 데이터 정의
class UserCreate(BaseModel):
    ID: str
    email: EmailStr
    nickname: str
    profile: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str


class UserUpdate(BaseModel):
    nickname: str = None
    password: str = None

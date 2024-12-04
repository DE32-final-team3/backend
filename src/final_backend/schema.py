from pydantic import BaseModel, EmailStr
from typing import Optional


# 사용자 생성 시 필요한 데이터 정의
class UserCreate(BaseModel):
    email: EmailStr
    nickname: str
    profile: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None

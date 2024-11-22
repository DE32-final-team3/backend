from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo


# 사용자 생성 시 필요한 데이터 정의
class UserCreate(BaseModel):
    ID: str
    email: EmailStr
    nickname: str
    password: str
    password2: str

    # 유효성 검증
    @field_validator("nickname", "email", "password", check_fields=False)
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
    email: str


class UserUpdate(BaseModel):
    nickname: str = None
    password: str = None

    @field_validator("nickname", "password", check_fields=False)
    def not_empty(cls, v):
        if v and not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

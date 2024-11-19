from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User


# bcrypt 알고리즘을 사용하여 비밀번호를 암호화
# pwd_context 객체를 생성하고 pwd_context 객체를 사용하여 비밀번호를 암호화하여 저장
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    # User 모델을 사용하여 사용자 객체 생성
    db_user = User(
        username=user_create.username,
        password=pwd_context.hash(user_create.password),
        email=user_create.email,
    )
    db.add(db_user)
    db.commit()
    return {"유저" " " f"'{db_user.username}' 생성 완료."}


def get_existing_user(db: Session, user_create: UserCreate):
    return (
        db.query(User)  # User 모델을 사용하여 DB에서 사용자 데이터를 조회
        .filter(
            # 조건을 사용하여 DB에서 주어진 이름이나 이메을과 일치하는 사용자를 찾음
            (User.username == user_create.username)
            | (User.email == user_create.email)
        )
        .first()  # 조건에 맞는 첫 번째 결과 반환
    )


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def delete_user(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        print("Log: 유저" "" f'"{username}" 삭제 완료.')
        return {"유저" "" f'"{username}" 삭제 완료.'}
    else:
        print("Log: 유저" "" f'"{username}"를 찾을 수 없습니다.')

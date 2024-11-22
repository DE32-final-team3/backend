from passlib.context import CryptContext
from sqlalchemy.orm import Session
from bcrypt import checkpw
from src.final_backend.user_schema import UserCreate
from src.final_backend.models import User
from jigutime import jigu

# bcrypt 알고리즘을 사용하여 비밀번호를 암호화
# pwd_context 객체를 생성하고 pwd_context 객체를 사용하여 비밀번호를 암호화하여 저장
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    # User 모델을 사용하여 사용자 객체 생성
    db_user = User(
        nickname=user_create.nickname,
        password=pwd_context.hash(user_create.password),
        email=user_create.email,
        create_at=jigu.now(),
    )
    db.add(db_user)
    db.commit()
    return {"유저" " " f"'{db_user.nickname}' 생성 완료."}


def get_existing_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_existing_name(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()


def delete_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and checkpw(password.encode(), user.password.encode()):
        db.delete(user)
        db.commit()
        print("Log: 유저" "" f'"{email}" 삭제 완료.')
        return {"유저" "" f'"{email}" 삭제 완료.'}
    else:
        print("Log: 유저" "" f'"{email}"를 찾을 수 없습니다.')
        return None


def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def update_user_info(db: Session, user: User, updated_data: dict):
    for key, value in updated_data.items():
        if key == "password" and value is not None:
            value = pwd_context.hash(value)

        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def generate_temporary_password(db, user, length=8):
    import secrets
    import string
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # 임시 비밀번호 생성
    characters = string.ascii_letters + string.digits  # 대소문자 + 숫자
    temporary_password = "".join(secrets.choice(characters) for _ in range(length))

    # 암호화하여 DB에 저장
    User.password = pwd_context.hash(temporary_password)
    db.commit()
    db.refresh(user)

    # 생성된 비밀번호 반환
    return temporary_password


def send_reset_email(email: str, content: str):
    """
    msg = MIMEText(f"다음은 임시 비밀번호입니다:\n\n{content}\n\n로그인 후 비밀번호를 변경하세요.")
    msg["Subject"] = "임시 비밀번호 발급 안내"
    msg["From"] = "your_email@example.com"
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_email_password")
        server.sendmail(msg["From"], [email], msg.as_string())
    """
    return content

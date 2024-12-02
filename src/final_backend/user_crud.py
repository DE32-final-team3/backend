from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.final_backend.schema import UserCreate
from src.final_backend.models import User, Following, UserTaste
from jigutime import jigu
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string, secrets, os, smtplib


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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def delete_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and pwd_context.verify(password, user.password):
        db.delete(user)
        db.commit()
        print("Log: 유저" "" f'"{email}" 삭제 완료.')
        return {"Log: 유저" "" f'"{email}" 삭제 완료.'}
    else:
        print("Log: 유저 비밀번호가 틀립니다.")
        return None


def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def update_user_info(db: Session, user: User, updated_data: dict):

    if not isinstance(user, User):
        raise ValueError("Provided user must be an instance of User model.")

    for key, value in updated_data.items():
        if key == "password" and value is not None:
            value = pwd_context.hash(value)

        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def generate_temporary_password(db: Session, user: User, length=8):

    # 임시 비밀번호 생성
    characters = string.ascii_letters + string.digits  # 대소문자 + 숫자
    temporary_password = "".join(secrets.choice(characters) for _ in range(length))

    # 암호화하여 DB에 저장
    user.password = pwd_context.hash(temporary_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 생성된 비밀번호 반환
    return temporary_password


SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_reset_email(email: str, content: str):
    # SMTP 서버 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD

    # 이메일 메시지 설정
    msg = MIMEMultipart()
    msg["From"] = "tunetalk"
    msg["To"] = email
    msg["Subject"] = "Tunetalk 임시 비밀번호 발급 안내"

    body_text = f"요청한 임시 비밀번호입니다. 로그인 후 비밀번호를 변경하세요."
    body_html = f"""
    <html>
    <head></head>
    <body>
      <h3>Tunetalk 임시 비밀번호 발급 안내</h3>
      <p>요청한 임시 비밀번호입니다</p>
      <p><strong>{content}</strong></p>
      <p>반드시 로그인 후 비밀번호를 변경하세요.</p>
    </body>
    </html>
    """

    # MIME 타입 설정
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], msg["To"], msg.as_string())
        print("이메일 전송 성공")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return None


def update_profile(db: Session, user: User, image_path: str):

    user.profile = image_path
    db.add(user)
    db.commit()
    db.refresh(user)
    print("프로일 이미지 저장 완료.")
    return user


def update_user_taste(db: Session, tastes: list[dict]):
    for taste in tastes:
        # Query the UserTaste table
        existing_taste = (
            db.query(UserTaste).filter(UserTaste.user_id == taste["user_id"]).first()
        )
        if existing_taste:
            # Update existing user taste
            existing_taste.acousticness = taste.get(
                "acousticness", existing_taste.acousticness
            )
            existing_taste.danceability = taste.get(
                "danceability", existing_taste.danceability
            )
            existing_taste.instrumentalness = taste.get(
                "instrumentalness", existing_taste.instrumentalness
            )
            existing_taste.energy = taste.get("energy", existing_taste.energy)
            existing_taste.tempo = taste.get("tempo", existing_taste.tempo)
            existing_taste.valence = taste.get("valence", existing_taste.valence)
            existing_taste.speechiness = taste.get(
                "speechiness", existing_taste.speechiness
            )
        else:
            # Insert a new user taste
            new_taste = UserTaste(
                user_id=taste["user_id"],
                acousticness=taste.get("acousticness"),
                danceability=taste.get("danceability"),
                instrumentalness=taste.get("instrumentalness"),
                energy=taste.get("energy"),
                tempo=taste.get("tempo"),
                valence=taste.get("valence"),
                speechiness=taste.get("speechiness"),
            )
            db.add(new_taste)
    db.commit()


def add_follow(db: Session, user_id: str, following: str):
    # Check if the follow relationship already exists
    existing = (
        db.query(Following)
        .filter(
            Following.user_id == user_id,
            Following.following == following,
        )
        .first()
    )
    user = db.query(User).filter(User.id == user_id).first()
    f_user = db.query(User).filter(User.id == following).first()
    if not existing:
        # Create new follow relationship
        follow = Following(
            user_id=user_id,
            following=following,
        )
        db.add(follow)
        db.commit()
        return {
            "message": f"({user.nickname}) 유저가 ({f_user.nickname}) 유저를 팔로우 합니다.",
            "user": user.nickname,
            "f_user": f_user.nickname,
        }
    else:
        return {
            "message": f"유저 ({user.nickname})가 이미 ({f_user.nickname})를 팔로우 중 입니다."
        }


def follow_delete(db: Session, user_id: str, following: str):
    # Check if the follow relationship already exists
    existing = (
        db.query(Following)
        .filter(
            Following.user_id == user_id,
            Following.following == following,
        )
        .first()
    )
    user = db.query(User).filter(User.id == user_id).first()
    f_user = db.query(User).filter(User.id == following).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {
            "message": f"유저 ({user.nickname})가 유저 ({f_user.nickname})를 언팔로우 합니다.",
            "user": {"id": user.id, "nickname": user.nickname},
            "f_user": {"id": f_user.id, "nickname": f_user.nickname},
        }
    else:
        return {
            "message": f"유저 ({user.nickname})가 유저 ({f_user.nickname})를 팔로우 중이 아닙니다."
        }

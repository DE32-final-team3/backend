from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string, secrets, os, smtplib

from odmantic import AIOEngine, ObjectId
from src.final_backend.models import User
from passlib.context import CryptContext


# bcrypt 알고리즘을 사용하여 비밀번호를 암호화
# pwd_context 객체를 생성하고 pwd_context 객체를 사용하여 비밀번호를 암호화하여 저장
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(engine: AIOEngine, user_data: dict):
    # User 모델을 사용하여 사용자 객체 생성
    user = User(
        email=user_data.email,
        nickname=user_data.nickname,
        password=pwd_context.hash(user_data.password),
        profile=user_data.profile,
    )
    await engine.save(user)
    return {"message": f"유저 '{user.nickname}' 생성 완료."}


async def get_existing_email(engine: AIOEngine, email: str):
    return await engine.find_one(User, User.email == email)


async def get_existing_name(engine: AIOEngine, nickname: str):
    return await engine.find_one(User, User.nickname == nickname)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def delete_user(engine: AIOEngine, email: str, password: str):
    user = await engine.find_one(User, User.email == email)
    if user and pwd_context.verify(password, user.password):
        # 기존 프로필 이미지 삭제
        if user.profile and os.path.exists(user.profile):
            os.remove(user.profile)
        await engine.delete(user)
        return {"message": f"유저 '{email}' 삭제 완료."}
    else:
        return {"message": "유저 비밀번호가 틀립니다."}


async def update_user_info(engine: AIOEngine, user: User, updated_data: dict):
    for key, value in updated_data.items():
        if key == "password" and value is not None:
            value = pwd_context.hash(value)
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    await engine.save(user)
    return user


async def generate_temporary_password(engine: AIOEngine, user: User, length=8):

    # 임시 비밀번호 생성
    characters = string.ascii_letters + string.digits  # 대소문자 + 숫자
    temporary_password = "".join(secrets.choice(characters) for _ in range(length))

    # 암호화하여 DB에 저장
    user.password = pwd_context.hash(temporary_password)
    await engine.save(user)
    return temporary_password


SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


async def send_reset_email(email: str, content: str):
    # SMTP 서버 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD

    # 이메일 메시지 설정
    msg = MIMEMultipart()
    msg["From"] = "Cinetalk"
    msg["To"] = email
    msg["Subject"] = "Cinetalk 임시 비밀번호 발급 안내"

    body_text = f"요청한 임시 비밀번호입니다. 로그인 후 비밀번호를 변경하세요."
    body_html = f"""
    <html>
    <head></head>
    <body>
      <h3>Cinetalk 임시 비밀번호 발급 안내</h3>
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
        print(f"이메일 전송 오류: {e}")
        return None


async def add_follow(engine: AIOEngine, id: str, follow_id: str):
    userId = ObjectId(id)
    followingId = ObjectId(follow_id)
    # 현재 사용자를 찾기 위해 nickname으로 조회
    user = await engine.find_one(User, User.id == userId)
    if not user:
        return {"error": "해당 id를 가진 사용자를 찾을 수 없습니다."}

    # 팔로우할 사용자를 찾기 위해 following_nickname으로 조회
    following_user = await engine.find_one(User, User.id == followingId)
    if not following_user:
        return {"error": "해당 following_id를 가진 사용자를 찾을 수 없습니다."}

    # 이미 팔로우하고 있는지 확인
    if user.following and followingId in user.following:
        return {
            "message": f"유저 {user.nickname}가 이미 {following_user.nickname}를 팔로우 중 입니다."
        }

    if user.following:
        user.following.append(followingId)
    else:
        user.following = [followingId]
    await engine.save(user)

    return {
        "message": f"{user.nickname} 유저가 {following_user.nickname} 유저를 팔로우 합니다.",
        "user": user.nickname,
        "f_user": following_user.nickname,
    }


async def delete_follow(engine: AIOEngine, id: str, follow_id: str):
    userId = ObjectId(id)
    followingId = ObjectId(follow_id)

    user = await engine.find_one(User, User.id == userId)
    if not user:
        return {"error": "해당 id를 가진 사용자를 찾을 수 없습니다."}

    following_user = await engine.find_one(User, User.id == followingId)
    if not following_user:
        return {"error": "해당 following_id를 가진 사용자를 찾을 수 없습니다."}

    if not user.following or followingId not in user.following:
        return {
            "message": f"유저 {user.nickname}가 유저 {following_user.nickname}를 팔로우 중이 아닙니다."
        }
    user.following.remove(followingId)

    await engine.save(user)
    return {
        "message": f"유저 {user.nickname}가 유저 {following_user.nickname}를 언팔로우 합니다.",
        "user": user.nickname,
        "f_user": following_user.nickname,
    }

async def update_movie_list(engine: AIOEngine, user: User, new_movie_list: List[str]):
    # 기존 영화 목록을 새 목록으로 교체
    user.movie_list = new_movie_list
    # 업데이트된 사용자 객체 저장
    await engine.save(user)
    return user

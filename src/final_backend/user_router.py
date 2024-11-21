from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets, pytz
from src.final_backend.database import get_db
from src.final_backend import user_crud, user_schema
from src.final_backend.user_schema import UserUpdate
from src.final_backend.models import User
from src.final_backend.user_crud import (
    get_user,
    pwd_context,
    send_reset_email,
    update_user_info,
    generate_temporary_password,
)


# APIRouter는 여러 엔드포인트를 그룹화하고 관리할 수 있도록 도와주는 객체
router = APIRouter(
    prefix="/api/user",  # 엔드포인트 경로에 /api/user 추가
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 로그인시 필요한 토큰,키,알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"


@router.post("/create", status_code=status.HTTP_200_OK)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    # DB에서 기존 사용자가 있는지 확인
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        print("이미 존재하는 사용자입니다.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다."
        )
    # def create_user 호출하여 새로운 사용자 생성
    create = user_crud.create_user(db=db, user_create=_user_create)
    user_name = _user_create.username
    print(f"새로운 유저 '{user_name}' 생성 완료")
    return create


@router.delete("/delete", status_code=status.HTTP_200_OK)
def user_delete(
    username: str = None, password: str = None, db: Session = Depends(get_db)
):
    delete_result = user_crud.delete_user(db, username=username, password=password)

    if delete_result is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"알림": "Username을 찾을 수 없습니다."},
        )

    if "error" in delete_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다."
        )
    return delete_result


@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = user_crud.get_user(db, form_data.username)
    if not user:
        print("일치하지 않은 아이디 입니다.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="일치하지 않은 아이디 입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not pwd_context.verify(form_data.password, user.password):
        print("일치하지 않은 비밀번호 입니다")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="일치하지 않은 비밀번호 입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    KST = pytz.timezone("Asia/Seoul")
    # access token 생성
    data = {
        "sub": user.username,
        "exp": datetime.now(KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"'{user.username}' 로그인 성공")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.put("/update", status_code=status.HTTP_200_OK)
def update_user_info(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = user_crud.update_user_info(
        db, user=current_user, updated_data=update_data.dict(exclude_unset=True)
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user information.",
        )
    return {"message": "회원정보 변경 완료", updated_user.username: updated_user}


@router.post("/reset-password-request")
def reset_password_request(username: str, email: str, db: Session = Depends(get_db)):
    # username만으로 사용자 확인
    user_by_username = db.query(User).filter(User.username == username).first()
    if not user_by_username:
        raise HTTPException(status_code=404, detail="해당 아이디를 찾을 수 없습니다.")

    # email만으로 사용자 확인
    user_by_email = db.query(User).filter(User.email == email).first()
    if not user_by_email:
        raise HTTPException(
            status_code=404, detail="해당 이메일로 가입된 유저가 없습니다."
        )
    # username과 email로 사용자 확인
    user = db.query(User).filter(User.username == username, User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="아이디와 이메일이 일치하지 않습니다."
        )

    # 임시 비밀번호 생성
    temporary_password = generate_temporary_password()

    # 이메일로 임시 비밀번호 전송
    send_reset_email(email, f"임시 비밀번호: {temporary_password}")
    return {
        "message": f"임시 비밀번호가 이메일로 전송되었습니다. 로그인 후 비밀번호를 변경하세요."
    }

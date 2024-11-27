from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from starlette import status
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
import pytz, os, shutil
from src.final_backend.database import get_db
from src.final_backend import user_crud
from src.final_backend.user_schema import UserCreate, UserUpdate, Token
from src.final_backend.models import User
from src.final_backend.user_crud import (
    pwd_context,
    send_reset_email,
    generate_temporary_password,
    get_user,
)

# APIRouter는 여러 엔드포인트를 그룹화하고 관리할 수 있도록 도와주는 객체
router = APIRouter(
    prefix="/api/user",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 로그인시 필요한 토큰,키,알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 120
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


@router.post("/email", status_code=status.HTTP_200_OK)
def emailcheck(email=str, db: Session = Depends(get_db)):
    user = user_crud.get_existing_email(db, email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 이메일입니다."
        )
    return {"message": "사용자가 존재하지 않습니다."}


@router.post("/nickname", status_code=status.HTTP_200_OK)
def namecheck(nickname=str, db: Session = Depends(get_db)):
    user = user_crud.get_existing_name(db, nickname)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 닉네임입니다."
        )
    return {"message": "사용자가 존재하지 않습니다."}


@router.post("/create", status_code=status.HTTP_200_OK)
def user_create(_user_create: UserCreate, db: Session = Depends(get_db)):
    create = user_crud.create_user(db=db, user_create=_user_create)
    if not create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="회원가입이 불가능 합니다."
        )
    user_name = _user_create.nickname
    print(f"새로운 유저 '{user_name}' 생성 완료")
    return create


@router.delete("/delete", status_code=status.HTTP_200_OK)
def user_delete(_user_create: UserCreate, db: Session = Depends(get_db)):
    delete_result = user_crud.delete_user(db, _user_create.email, _user_create.password)

    if delete_result is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"알림": "유저 비밀번호가 틀립니다."},
        )

    if "error" in delete_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다."
        )
    return delete_result


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = user_crud.get_user(db, email=form_data.username)
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
    # 토큰 생성
    KST = pytz.timezone("Asia/Seoul")
    data = {
        "sub": user.email,
        "exp": datetime.now(KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"'{user.nickname}' 로그인 성공")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


@router.post("/validate")
def current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # 토큰 검증
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 사용자 검색
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception

    return user


@router.put("/update", status_code=status.HTTP_200_OK)
def update_user_info(
    update_data: UserUpdate,
    current_user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    updated_user = user_crud.update_user_info(
        db, user=current_user, updated_data=update_data.model_dump(exclude_unset=True)
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user information.",
        )
    return {
        "message": "회원정보 변경 완료",
        "nickname": updated_user.nickname,
        "email": updated_user.email,
    }


@router.post("/reset-password-request")
def reset_password_request(email: str, nickname: str, db: Session = Depends(get_db)):
    # email만으로 사용자 확인
    user_by_email = db.query(User).filter(User.email == email).first()
    if not user_by_email:
        raise HTTPException(
            status_code=404, detail="해당 이메일로 가입된 유저가 없습니다."
        )

    # nickname만으로 사용자 확인
    user_by_nickname = db.query(User).filter(User.nickname == nickname).first()
    if not user_by_nickname:
        raise HTTPException(status_code=404, detail="해당 아이디를 찾을 수 없습니다.")

    # nickname과 email로 사용자 확인
    user = db.query(User).filter(User.nickname == nickname, User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="아이디와 이메일이 일치하지 않습니다."
        )

    # 임시 비밀번호 생성
    temporary_password = generate_temporary_password(db, user)

    # 이메일로 임시 비밀번호 전송
    send_reset_email(email, temporary_password)
    return {
        "message": f"임시 비밀번호가 이메일로 전송되었습니다. 로그인 후 비밀번호를 변경하세요."
    }


@router.post("/upload_profile", status_code=status.HTTP_200_OK)
def upload_profile_image(
    file: UploadFile = File(...),
    id: str = "",  # 현재 사용자 정보
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저 고유 id가 일치하지 않습니다.")
    # 업로드된 파일 저장 경로 설정
    upload_directory = "user_profile_images"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    file_location = os.path.join(upload_directory, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 파일 경로를 DB에 저장
    updated_user = user_crud.update_profile(db, user, file_location)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="프로필 이미지 업데이트에 실패했습니다.",
        )

    return {"message": "프로필 이미지 업로드 완료", "file_path": file_location}


@router.get("/profile/get_image", status_code=status.HTTP_200_OK)
def get_profile_image(id: str, db: Session = Depends(get_db)):
    # DB에서 사용자 조회
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저 고유 id가 일치하지 않습니다.")

    # 프로필 이미지 경로 확인
    if not user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필 이미지가 존재하지 않습니다.",
        )

    # 이미지 파일의 경로 확인
    if not os.path.exists(user.profile):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="서버에서 프로필 이미지 파일을 찾을 수 없습니다.",
        )

    # 이미지 파일을 반환
    return FileResponse(user.profile)

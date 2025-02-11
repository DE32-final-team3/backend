import uuid
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from starlette import status
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
import pytz, os, shutil
from src.final_backend import user_crud
from src.final_backend.schema import (
    UserCreate,
    UserUpdate,
    Token,
    UserMovieLists,
    PasswordRequest,
)
from src.final_backend.models import User
from src.final_backend.user_crud import (
    generate_email_verification_code,
    get_existing_email,
    get_existing_name,
    create_user,
    send_email_verification,
    send_reset_email,
    generate_temporary_password,
    update_user_info,
    add_follow,
    delete_follow,
    update_movie_list,
    get_user_info_from_follow_id,
    verify_email_code,
)
from odmantic import AIOEngine, ObjectId
from src.final_backend.database import DATABASE_URL
from motor.motor_asyncio import AsyncIOMotorClient

# APIRouter는 여러 엔드포인트를 그룹화하고 관리할 수 있도록 도와주는 객체
user_router = APIRouter(prefix="/user", tags=["User"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 로그인시 필요한 토큰,키,알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 120
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# AIOEngine을 FastAPI에서 사용할 수 있도록 설정
async def get_engine():
    client = AsyncIOMotorClient(DATABASE_URL)
    return AIOEngine(client=client, database="cinetalk")


async def chat_engine():
    client = AsyncIOMotorClient(DATABASE_URL)
    return AIOEngine(client=client, database="chat")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@user_router.post("/check/email", status_code=status.HTTP_200_OK)
async def emailcheck(email=str, engine: AIOEngine = Depends(get_engine)):
    existing_email = await get_existing_email(engine, email)
    if existing_email:
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    # 인증 코드 생성
    verification_code = await generate_email_verification_code(engine, email)

    await send_email_verification(email, verification_code)
    return {"message": f"인증번호가 이메일로 전송되었습니다."}


@user_router.post("/verify/email", status_code=status.HTTP_200_OK)
async def verify_email(email: str, code: str, engine: AIOEngine = Depends(get_engine)):
    return await verify_email_code(engine, email, code)


@user_router.post("/check/nickname", status_code=status.HTTP_200_OK)
async def namecheck(nickname=str, engine: AIOEngine = Depends(get_engine)):
    existing_name = await get_existing_name(engine, nickname)
    if existing_name:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")
    return {"message": "사용 가능한 닉네임입니다."}


@user_router.post("/create", status_code=status.HTTP_200_OK)
async def user_create(
    _user_create: UserCreate, engine: AIOEngine = Depends(get_engine)
):
    create = await create_user(engine=engine, user_data=_user_create)
    if not create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="회원가입이 불가능 합니다."
        )
    # new_user = await create_user(engine, user_create.dict())
    user_name = _user_create.nickname
    print(f"유저 '{user_name}' 생성 완료.")
    return create


@user_router.delete("/delete", status_code=status.HTTP_200_OK)
async def user_delete(
    password_request: PasswordRequest,
    token: str = Depends(oauth2_scheme),
    engine: AIOEngine = Depends(get_engine),
    chat_engine: AIOEngine = Depends(chat_engine),
):
    # 토큰 검증
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 검증 불가",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 비밀번호로 유저 삭제
    try:
        delete_result = await user_crud.delete_user(
            engine,
            chat_engine,
            user_email=user_email,
            password=password_request.password,
        )
        print(password_request)
        return delete_result
    except HTTPException as e:
        raise e


@user_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    engine: AIOEngine = Depends(get_engine),
):
    user = await get_existing_email(engine, form_data.username)
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


@user_router.post("/info")
async def get_user_info(
    token: str = Depends(oauth2_scheme),
    engine: AIOEngine = Depends(get_engine),
):
    # 토큰 검증
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 검증 불가",
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
    user = await get_existing_email(engine, email=email)
    if user is None:
        raise credentials_exception

    return user


@user_router.put("/update", status_code=status.HTTP_200_OK)
async def update_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_user_info),
    engine: AIOEngine = Depends(get_engine),
):
    updated_user = await update_user_info(
        engine,
        user=current_user,
        updated_data=update_data.model_dump(exclude_unset=True),
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="회원정보 변경 실패.",
        )
    return {
        "message": "회원정보 변경 완료",
        "nickname": updated_user.nickname,
        "email": updated_user.email,
    }


@user_router.post("/password/reset")
async def reset_password_request(email: str, engine: AIOEngine = Depends(get_engine)):
    # email만으로 사용자 확인
    user_by_email = await get_existing_email(engine, email)
    if not user_by_email:
        raise HTTPException(
            status_code=404, detail="해당 이메일로 가입된 유저가 없습니다."
        )

    user = await engine.find_one(User, User.email == email)
    # 임시 비밀번호 생성
    temporary_password = await generate_temporary_password(engine, user)
    # 이메일로 임시 비밀번호 전송
    await send_reset_email(email, temporary_password)
    return {
        "message": f"임시 비밀번호가 이메일로 전송되었습니다. 로그인 후 비밀번호를 변경하세요."
    }


@user_router.post("/profile/upload", status_code=status.HTTP_200_OK)
async def upload_profile_image(
    id: str,
    file: UploadFile = File(...),
    engine: AIOEngine = Depends(get_engine),
):

    user = await engine.find_one(User, User.id == ObjectId(id))
    if not user:
        raise HTTPException(status_code=404, detail="일치하는 유저 id가 없습니다.")

    if user.profile and os.path.exists(user.profile):
        os.remove(user.profile)
    # 업로드된 파일 저장 경로 설정
    upload_directory = "profile_images"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    file_ext = file.content_type.split("/")[-1]

    file_location = os.path.join(upload_directory, f"{uuid.uuid4()}.{file_ext}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 사용자 프로필 이미지 경로 업데이트
    user.profile = file_location

    # 사용자 정보 저장
    await engine.save(user)

    return {"message": "프로필 이미지 업로드 완료", "file_path": user.profile}


@user_router.get("/profile/get", status_code=status.HTTP_200_OK)
async def get_profile_image(id: str, engine: AIOEngine = Depends(get_engine)):

    user = await engine.find_one(User, User.id == ObjectId(id))
    if not user:
        raise HTTPException(status_code=404, detail="일치하는 유저 id가 없습니다.")

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


@user_router.post("/follow")
async def follow_user(
    id: str, following_id: str, engine: AIOEngine = Depends(get_engine)
):
    result = await add_follow(engine, id, following_id)
    user = result.get("user")
    f_user = result.get("f_user")
    print(f"유저 {user}님이 유저 {f_user}님을 팔로우 합니다.")
    return result


@user_router.delete("/follow/delete")
async def follow_Delete(
    id: str, following_id: str, engine: AIOEngine = Depends(get_engine)
):
    result = await delete_follow(engine, id, following_id)
    user = result.get("user")
    f_user = result.get("f_user")
    print(f"유저 {user}님이 유저 {f_user}님을 언팔로우 합니다.")
    return result


@user_router.get("/follow/info")
async def follow_user_getInfo(follow_id: str, engine: AIOEngine = Depends(get_engine)):
    result = await get_user_info_from_follow_id(engine, follow_id)
    print(f"유저 정보: {result}")
    return result


@user_router.put("/update/movies", status_code=status.HTTP_200_OK)
async def update_user_movies(
    movie_data: UserMovieLists,
    current_user: User = Depends(get_user_info),
    engine: AIOEngine = Depends(get_engine),
):
    updated_user = await update_movie_list(
        engine,
        user=current_user,
        new_movie_list=movie_data.movie_list or [],
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="영화 목록 업데이트 실패.",
        )
    return {
        "message": "영화 목록 업데이트 완료",
        "movie_list": updated_user.movie_list,
    }

@user_router.get("/get/movies", status_code=status.HTTP_200_OK)
async def get_user_movies(
    user_id: str,
    engine: AIOEngine = Depends(get_engine),
):
    user = await engine.find_one(User, User.id == ObjectId(user_id))
    
    if not user:
        raise HTTPException(status_code=404, detail="일치하는 유저를 찾을 수 없습니다.")
    
    return {
        "user_id": user_id,
        "movie_list": user.movie_list or [], 
    }

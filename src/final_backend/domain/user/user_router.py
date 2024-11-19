from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema


# APIRouter는 여러 엔드포인트를 그룹화하고 관리할 수 있도록 도와주는 객체
router = APIRouter(
    prefix="/api/user",  # 엔드포인트 경로에 /api/user 추가
)


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
def user_delete(username: str = None, db: Session = Depends(get_db)):
    delete_result = user_crud.delete_user(db, username=username)

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

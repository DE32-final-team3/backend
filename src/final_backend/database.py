from sqlalchemy import create_engine  # DB와 연결하는 엔진 생성
from sqlalchemy.ext.declarative import (
    declarative_base,
)  # 테이블과 클래스를 연결 하는데 사용되는 기본 클래스 생성
from sqlalchemy.orm import sessionmaker  # DB와 상호작용 하는 세션 생성 모듈

# Database 접속 주소
DATABASE_URL = "mariadb+pymysql://root:1234@127.0.0.1:3307/userdb"
# DB와 연결을 관리하는 엔진 객체 생성
engine = create_engine(DATABASE_URL)
# 데이터베이스와 통신할 때 필요한 세션을 생성.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 데이터베이스 테이블과 Python 클래스를 연결할 수 있는 기본 클래스를 생성합니다.
Base = declarative_base()


# Base를 상속받은 모든 클래스를 기반으로 데이터베이스에 테이블 생성(테이블 존재시 생성 X)
def create_tables():
    from src.final_backend.models import Base

    Base.metadata.create_all(engine)


# 데이터베이스 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db  # 생성한 세션 객체 반환
    finally:
        db.close()

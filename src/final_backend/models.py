from sqlalchemy import Column, String, DateTime
from src.final_backend.database import Base
from jigutime import jigu
import uuid


# Base를 상속받아 User 클래스 생성
class User(Base):
    __tablename__ = "user"
    ID = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False
    )
    email = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(16), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    create_at = Column(DateTime(timezone=True), default=jigu.now())

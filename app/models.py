from database import Base
from sqlalchemy import Column, String, DateTime
from jigutime import jigu
import uuid


# Base를 상속받아 User 클래스 생성
class User(Base):
    __tablename__ = "user"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False
    )
    email = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(16), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False, index=True)
    profile = Column(String(255))
    create_at = Column(DateTime(timezone=True), default=jigu.now())
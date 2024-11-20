from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base
from jigutime import jigu


# Base를 상속받아 User 클래스 생성
class User(Base):
    __tablename__ = "user"
    num = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    create_at = Column(DateTime(timezone=True), default=jigu.now())

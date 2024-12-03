from odmantic import Model
from typing import Optional
from jigutime import jigu
import uuid


# Base를 상속받아 User 클래스 생성
class User(Model):
    ID: str = uuid.uuid4().hex
    email: str
    nickname: str
    password: str
    profile: Optional[str] = None
    movie_list: Optional[str] = None
    create_at: Optional[str] = None
    # create_at = Column(DateTime(timezone=True), default=jigu.now())

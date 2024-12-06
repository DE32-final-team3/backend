from odmantic import Model, ObjectId
from typing import Optional, List


# Base를 상속받아 User 클래스 생성
class User(Model):
    email: str
    nickname: str
    password: str
    profile: Optional[str] = None
    movie_list: Optional[List[int]] = []
    following: Optional[List[ObjectId]] = []

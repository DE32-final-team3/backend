from odmantic import Model, ObjectId
from typing import Optional, List

class User(Model):
    email: str
    nickname: str
    password: str
    profile: Optional[str] = None
    movie_list: Optional[List[int]] = []
    following: Optional[List[ObjectId]] = []

class Movie(Model):
    movie_id: int
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    original_language: Optional[str] = None
    genres: List[int] = []
    release_date: Optional[str] = None
    cast: Optional[List[dict]] = None
    director: Optional[dict] = None
from pydantic import BaseModel, EmailStr
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional


# 사용자 생성 시 필요한 데이터 정의
class UserCreate(BaseModel):
    id: str
    email: EmailStr
    nickname: str
    profile: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str


class UserUpdate(BaseModel):
    nickname: str = None
    password: str = None


class TrackBase(BaseModel):
    id: str
    name: Optional[str]
    artist: Optional[str]
    image: Optional[str]


class TrackAudioFeatures(BaseModel):
    id: str
    acousticness: Optional[float]
    danceability: Optional[float]
    instrumentalness: Optional[float]
    energy: Optional[float]
    tempo: Optional[float]
    valence: Optional[float]
    speechiness: Optional[float]


class UserPlaylistBase(BaseModel):
    user_id: str
    track_id: str


class UserPlaylistBase(BaseModel):
    user_id: str
    track_id: str


class UserTasteBase(BaseModel):
    user_id: str
    acousticness: float = None
    danceability: float = None
    instrumentalness: float = None
    energy: float = None
    tempo: float = None
    valence: float = None
    speechiness: float = None

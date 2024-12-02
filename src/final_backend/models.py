from src.final_backend.database import Base
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, PrimaryKeyConstraint
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
    password = Column(String(100), nullable=False)
    profile = Column(String(255))
    create_at = Column(DateTime(timezone=True), default=jigu.now())


class Track(Base):
    __tablename__ = "track"

    id = Column(String(255), nullable=False, primary_key=True)
    name = Column(String(255), nullable=True)
    artist = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    acousticness = Column(Float, nullable=True)
    danceability = Column(Float, nullable=True)
    instrumentalness = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    tempo = Column(Float, nullable=True)
    valence = Column(Float, nullable=True)
    speechiness = Column(Float, nullable=True)


class UserPlaylist(Base):
    __tablename__ = "user_playlist"

    user_id = Column(String(255), ForeignKey("user.id"), nullable=False)
    track_id = Column(String(255), ForeignKey("track.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("user_id", "track_id"),)


class Following(Base):
    __tablename__ = "following"

    user_id = Column(String(255), ForeignKey("user.id"), nullable=False)
    following = Column(String(255), ForeignKey("user.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("user_id", "following"),)


class UserTaste(Base):
    __tablename__ = "user_taste"

    user_id = Column(String(255), ForeignKey("user.id"), primary_key=True)
    acousticness = Column(Float, nullable=True)
    danceability = Column(Float, nullable=True)
    instrumentalness = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    tempo = Column(Float, nullable=True)
    valence = Column(Float, nullable=True)
    speechiness = Column(Float, nullable=True)

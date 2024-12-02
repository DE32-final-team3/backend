from sqlalchemy.orm import Session
from src.final_backend.models import Track, UserPlaylist
from src.final_backend.schema import TrackBase, TrackAudioFeatures, UserPlaylistBase


# Track 기본 정보를 저장하는 함수
def insert_track_info(db: Session, tracks: list[TrackBase]):
    for track in tracks:
        db_track = db.query(Track).filter(Track.id == track.id).first()
        if db_track:
            # 기존 데이터 업데이트
            db_track.name = track.name
            db_track.artist = track.artist
            db_track.image = track.image
        else:
            # 새 데이터 삽입
            db_track = Track(
                id=track.id, name=track.name, artist=track.artist, image=track.image
            )
            db.add(db_track)
    db.commit()


# Audio Features를 업데이트하는 함수
def update_audio_features(db: Session, features: list[TrackAudioFeatures]):
    for feature in features:
        db_track = db.query(Track).filter(Track.id == feature.id).first()
        if db_track:
            db_track.acousticness = feature.acousticness
            db_track.danceability = feature.danceability
            db_track.instrumentalness = feature.instrumentalness
            db_track.energy = feature.energy
            db_track.tempo = feature.tempo
            db_track.valence = feature.valence
            db_track.speechiness = feature.speechiness
    db.commit()


# 플레이리스트에 트랙 추가
def add_to_playlist(db: Session, playlist: UserPlaylistBase):
    existing_entry = (
        db.query(UserPlaylist)
        .filter(
            UserPlaylist.user_id == playlist.user_id,
            UserPlaylist.track_id == playlist.track_id,
        )
        .first()
    )
    if not existing_entry:
        db_entry = UserPlaylist(
            user_id=playlist.user_id,
            track_id=playlist.track_id,
        )
        db.add(db_entry)
        db.commit()


# 플레이리스트에서 트랙 제거
def remove_from_playlist(db: Session, playlist: UserPlaylistBase):
    db_entry = (
        db.query(UserPlaylist)
        .filter(
            UserPlaylist.user_id == playlist.user_id,
            UserPlaylist.track_id == playlist.track_id,
        )
        .first()
    )
    if db_entry:
        db.delete(db_entry)
        db.commit()


# 트랙 전체 데이터 가져오기
def get_all_tracks(db: Session):
    tracks = db.query(Track).all()
    return [
        {
            "id": track.id,
            "name": track.name,
            "artist": track.artist,
            "image": track.image,
            "acousticness": track.acousticness,
            "danceability": track.danceability,
            "instrumentalness": track.instrumentalness,
            "energy": track.energy,
            "tempo": track.tempo,
            "valence": track.valence,
            "speechiness": track.speechiness,
        }
        for track in tracks
    ]


# 특정 사용자의 플레이리스트에서 트랙 가져오기
def get_tracks_by_user(db: Session, user_id: str):
    tracks = (
        db.query(Track)
        .join(UserPlaylist, Track.id == UserPlaylist.track_id)
        .filter(UserPlaylist.user_id == user_id)
        .all()
    )
    return [
        {
            "id": track.id,
            "name": track.name,
            "artist": track.artist,
            "image": track.image,
            "acousticness": track.acousticness,
            "danceability": track.danceability,
            "instrumentalness": track.instrumentalness,
            "energy": track.energy,
            "tempo": track.tempo,
            "valence": track.valence,
            "speechiness": track.speechiness,
        }
        for track in tracks
    ]

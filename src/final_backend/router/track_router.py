from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.final_backend.database import get_db
from src.final_backend.schema import TrackBase, TrackAudioFeatures
from src.final_backend.track_crud import (
    insert_track_info,
    update_audio_features,
    get_all_tracks,
)

track_router = APIRouter(prefix="/api/tracks", tags=["Track"])


@track_router.post("/init")
def create_tracks(tracks: list[TrackBase], db: Session = Depends(get_db)):
    insert_track_info(db, tracks)
    return {"message": "Tracks inserted successfully"}


@track_router.put("/audio-features/")
def update_features(features: list[TrackAudioFeatures], db: Session = Depends(get_db)):
    update_audio_features(db, features)
    return {"message": "Audio features updated successfully"}


@track_router.get("/all")
def get_tracks(db: Session = Depends(get_db)):
    tracks = get_all_tracks(db)
    return {"tracks": tracks}

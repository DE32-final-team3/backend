from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.final_backend.database import get_db
from src.final_backend.schema import UserPlaylistBase
from src.final_backend.track_crud import (
    add_to_playlist,
    remove_from_playlist,
    get_tracks_by_user,
)

playlist_router = APIRouter(prefix="/api/playlist", tags=["Playlist"])


@playlist_router.post("/add")
def add_track(playlist: UserPlaylistBase, db: Session = Depends(get_db)):
    add_to_playlist(db, playlist)
    return {"message": "Track added to playlist successfully"}


@playlist_router.delete("/delete")
def remove_track(playlist: UserPlaylistBase, db: Session = Depends(get_db)):
    remove_from_playlist(db, playlist)
    return {"message": "Track removed from playlist successfully"}


@playlist_router.get("/{user_id}")
def get_user_tracks(user_id: str, db: Session = Depends(get_db)):
    tracks = get_tracks_by_user(db, user_id)
    return {"tracks": tracks}

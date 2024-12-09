from fastapi import APIRouter, HTTPException, Query, Body
from src.final_backend.movie_crud import save_movie_to_db, fetch_movies_by_ids, fetch_all_movies
import logging

# APIRouter 생성 시 prefix와 tags 설정
movie_router = APIRouter(prefix="/movie", tags=["Movie"])

# 영화 저장 엔드포인트
@movie_router.post("/save")
async def save_movie(movie: dict = Body(...)):
    try:
        result = await save_movie_to_db(movie)
        return result
    except Exception as e:
        logging.error(f"Error saving movie with data {movie}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save movie.")

# 모든 영화 조회 엔드포인트
@movie_router.get("/all")
async def get_all_movies():
    try:
        movies = await fetch_all_movies()
        return {"movies": movies}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch movies.")

# 영화 ID로 조회 엔드포인트
@movie_router.get("/list")
async def get_movies_by_ids(movie_ids: list[int] = Query(...)):
    try:
        movies = await fetch_movies_by_ids(movie_ids)
        if not movies:
            return {"message": "No movies found for the provided IDs."}
        return {"movies": movies}
    except Exception as e:
        logging.error(f"Exception in /movies/list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch movies.")
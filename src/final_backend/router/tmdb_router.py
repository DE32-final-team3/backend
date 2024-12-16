from fastapi import APIRouter, HTTPException, Query
import httpx
from typing import List, Optional

# APIRouter 생성
tmdb_router = APIRouter(prefix="/tmdb", tags=["Front"])

# TMDb API Key
tmdbApiKey = 'c9508eddcf9d0115e9bf51cc56429772'

# TMDb 영화 검색 엔드포인트
@tmdb_router.get("/search")
async def search_movies(q: str, limit: Optional[int] = 10, page: Optional[int] = 1):
    """
    TMDb 영화 검색 엔드포인트.
    영화 정보를 검색하고 출연진, 감독, 장르, 제작 국가를 포함한 결과를 반환합니다.
    """
    if not q:
        raise HTTPException(status_code=400, detail='Query parameter "q" is required')

    async with httpx.AsyncClient() as client:
        try:
            # TMDb API에 영화 검색 요청
            response = await client.get('https://api.themoviedb.org/3/search/movie', params={
                'api_key': tmdbApiKey,
                'query': q,
                'page': page,
                'language': 'ko-KR',
                'include_adult': 'false',
            })
            response.raise_for_status()
            movies = response.json().get('results', [])

            # 영화 세부 정보 추가
            movie_details = []
            for movie in movies[:limit]:  # limit 만큼 결과 제한
                try:
                    # 출연진 및 감독 정보 요청
                    credits_response = await client.get(f'https://api.themoviedb.org/3/movie/{movie["id"]}/credits', params={
                        'api_key': tmdbApiKey,
                        'language': 'ko-KR',
                    })
                    credits_response.raise_for_status()
                    credits_data = credits_response.json()

                    # 출연진 및 감독 정보 추출
                    cast = [
                        {"id": actor["id"], "name": actor["name"]}
                        for actor in credits_data["cast"] if actor["character"]
                    ][:8]  # 상위 8명만 포함
                    director = next(
                        (crew for crew in credits_data["crew"] if crew["job"] == "Director"), None
                    )
                    director_info = {
                        "id": director["id"] if director else '0',
                        "name": director["name"] if director else '감독 정보 없음'
                    }

                    # 영화 장르 및 제작 국가 정보 요청
                    detail_response = await client.get(f'https://api.themoviedb.org/3/movie/{movie["id"]}', params={
                        'api_key': tmdbApiKey,
                        'language': 'ko-KR',
                    })
                    detail_response.raise_for_status()
                    detail_data = detail_response.json()

                    genres = ', '.join([genre['name'] for genre in detail_data.get('genres', [])]) or '장르 정보 없음'
                    production_countries = ', '.join([country['name'] for country in detail_data.get('production_countries', [])]) or '제작 국가 정보 없음'

                    movie_details.append({
                        **movie,
                        "cast": cast,
                        "director": director_info,
                        "genres": genres,
                        "production_countries": production_countries
                    })
                except Exception as e:
                    # 세부 정보 요청 실패 시 기본값 설정
                    movie_details.append({
                        **movie,
                        "cast": [{"id": '0', "name": '출연진 정보 없음'}],
                        "director": {"id": '0', "name": '감독 정보 없음'},
                        "genres": '장르 정보 없음',
                        "production_countries": '제작 국가 정보 없음'
                    })

            return {"results": movie_details}
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Failed to fetch data from TMDb API")

# 영화 ID를 기반으로 YouTube 트레일러 URL 반환 엔드포인트
@tmdb_router.get("/{movieId}/videos")
async def get_movie_videos(movieId: int):
    """
    TMDb 영화 ID를 기반으로 유튜브 트레일러 URL을 반환합니다.
    """
    if movieId <= 0:
        raise HTTPException(status_code=400, detail="Invalid movie ID")

    async with httpx.AsyncClient() as client:
        try:
            # TMDb API에 영화 비디오 정보 요청
            response = await client.get(f'https://api.themoviedb.org/3/movie/{movieId}/videos', params={
                'api_key': tmdbApiKey,
                'language': 'ko-KR',
            })
            response.raise_for_status()

            videos = response.json().get('results', [])
            if not videos:
                raise HTTPException(status_code=404, detail="No videos found for this movie")

            youtube_trailer = next((video for video in videos if video['site'] == 'YouTube'), None)
            if youtube_trailer:
                return {"trailerUrl": f"https://www.youtube.com/watch?v={youtube_trailer['key']}"}
            else:
                raise HTTPException(status_code=404, detail="YouTube trailer not found")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch video data from TMDb: {e}")
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.final_backend.router import user_router
from src.final_backend.router.movie_router import movie_router

app = FastAPI()

# * = 모든 도메인 요청 허용
origins = ["*"]

app.add_middleware(
    CORSMiddleware,  # CORS는 브라우저에서 다른 도메인에 대한 요청을 처리할 수 있게 도와주>는 메커니즘
    allow_origins=origins,  # 모든 도메인에서 API를 호출할 수 있도록 허용
    allow_credentials=True,  # 쿠키를 포함한 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메서드(GET, POST 등)를 허용
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용
)

# user_router 모듈에 정의된 API 라우팅을 FastAPI 애플리케이션에 등록
app.include_router(user_router.user_router)

# movie_router 등록
app.include_router(movie_router)
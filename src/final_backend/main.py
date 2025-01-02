from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.final_backend.router.user_router import user_router
from src.final_backend.router.movie_router import movie_router
from src.final_backend.router.sim_router import sim_router
from src.final_backend.router.tmdb_router import tmdb_router
from motor.motor_asyncio import AsyncIOMotorClient
from src.final_backend.database import DATABASE_URL

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

app.include_router(user_router)
app.include_router(movie_router)
app.include_router(sim_router)
app.include_router(tmdb_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


async def create_ttl_index():
    # MongoDB 클라이언트 연결
    client = AsyncIOMotorClient(DATABASE_URL)  # MongoDB URL
    db = client["cinetalk"]  # 데이터베이스 이름
    collection = db["email_verification"]  # 컬렉션 이름

    # TTL Index 생성
    await collection.create_index("expires_at", expireAfterSeconds=0)


@app.on_event("startup")
async def startup_event():
    # 앱 시작 시 TTL Index 생성
    await create_ttl_index()

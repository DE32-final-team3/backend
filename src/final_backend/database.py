import os
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_IP = os.getenv("DB_IP")
DB_PORT = os.getenv("DB_PORT")
DATABASE_URL = f"mongodb://root:{DB_PASSWORD}@{DB_IP}:{DB_PORT}"

# MongoDB와 연결 설정
client = AsyncIOMotorClient(DATABASE_URL)
engine = AIOEngine(client=client, database="cinetalk")

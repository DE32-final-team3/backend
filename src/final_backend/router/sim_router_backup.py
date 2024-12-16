from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import logging

# MongoDB 설정
# MONGO_URI = "mongodb://root:team3@172.17.0.1:27017/?authSource=admin"
MONGO_URI = "mongodb://root:cine@3.37.94.149:27017/?authSource=admin"
# DB_NAME = "similarity"
DB_NAME = "cinetalk"
# COLLECTION_NAME = "20241205"  # 테스트용 고정 컬렉션 이름
COLLECTION_NAME = "20241215_similarity"

# APIRouter 생성
sim_router = APIRouter(prefix="/similarity", tags=["Similarity"])

# MongoDB 데이터 가져오기 엔드포인트
@sim_router.get("/all")
async def get_similarity_data():
    """
    MongoDB에서 similarity 데이터를 가져옵니다.
    """
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]

            # 컬렉션 전체 데이터 가져오기
            all_docs = list(collection.find({}))

            # ObjectId를 문자열로 변환
            for doc in all_docs:
                doc["_id"] = str(doc["_id"])

            return {"status": "success", "data": all_docs}

    except Exception as e:
        logging.error(f"Error fetching data from MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data from MongoDB.")

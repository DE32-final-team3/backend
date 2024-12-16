from fastapi import APIRouter, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime
import logging

# MongoDB 설정
MONGO_URI = "mongodb://root:cine@3.37.94.149:27017/?authSource=admin"
DB_NAME = "cinetalk"

# APIRouter 생성
sim_router = APIRouter(prefix="/similarity", tags=["Similarity"])

# 유저 ID로 상위 유사도 유저 조회 엔드포인트
@sim_router.get("/top")
async def get_top_similar_users(
    user_id: str = Query(..., description="Target user ID"),
    top_n: int = Query(10, description="Number of similar users to return")
):
    execution_date = datetime.now().strftime('%Y%m%d')
    collection_name = f"{execution_date}_similarity"

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]

            # MongoDB에서 유저 ID에 해당하는 데이터 검색
            user_doc = collection.find_one({"_id": user_id})
            if not user_doc:
                raise HTTPException(status_code=404, detail="User ID not found in similarity data.")

            # 유사도 데이터 추출 및 정렬
            similarity_scores = [
                {"user_id": key, "similarity": value}
                for key, value in user_doc.items()
                if key not in ["_id", "index"]
            ]
            sorted_scores = sorted(similarity_scores, key=lambda x: x["similarity"], reverse=True)

            # 상위 N명의 유저 반환
            top_users = [{"user_id": user["user_id"], "similarity": user["similarity"]} for user in sorted_scores[:top_n]]

            return {"user_id": user_id, "top_similar_users": top_users}
    except Exception as e:
        logging.error(f"Error fetching top {top_n} similar users for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch similarity data.")

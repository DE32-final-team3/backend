from fastapi import APIRouter, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging

# MongoDB 설정
MONGO_URI = "mongodb://root:cine@3.37.94.149:27017/?authSource=admin"
DB_NAME = "cinetalk"

# APIRouter 생성
sim_router = APIRouter(prefix="/similarity", tags=["Similarity"])

# MongoDB 데이터 가져오기 및 정렬 엔드포인트
@sim_router.get("/user")
async def get_sorted_similarity_data(
    index: str = Query(..., description="Target index to sort data"),
    top_n: int = Query(10, description="Number of top results to return")
):
    
    # collection_name = f"{datetime.now().strftime('%Y%m%d')}_similarity"
    collection_name = f"{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}_similarity"

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db[collection_name]

            # 컬렉션 전체 데이터 가져오기
            all_docs = list(collection.find({}))

            # ObjectId를 문자열로 변환
            for doc in all_docs:
                doc["_id"] = str(doc["_id"])

            # 기준 index 데이터 검색
            target_doc = next((doc for doc in all_docs if doc.get("index") == index), None)
            if not target_doc:
                raise HTTPException(status_code=404, detail=f"Index {index} not found in similarity data.")

            # 정렬 가능한 데이터만 필터링 (자기 자신 및 동일한 ID 제외)
            sortable_items = [
                {"user_id": key, "similarity": value}
                for key, value in target_doc.items()
                if key not in ["_id", "index"] and key != index and isinstance(value, (int, float))
            ]

            # 유사도 값 기준으로 내림차순 정렬
            sorted_items = sorted(sortable_items, key=lambda x: x["similarity"], reverse=True)

            # 상위 N개의 결과만 반환
            return sorted_items[:top_n]

    except Exception as e:
        logging.error(f"Error fetching and sorting data for index {index}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch and sort similarity data.")
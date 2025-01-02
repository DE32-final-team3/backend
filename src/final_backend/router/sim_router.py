from fastapi import APIRouter, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import logging

# MongoDB 설정
MONGO_URI = "mongodb://root:cine@3.37.94.149:27017/?authSource=admin"
DB_NAME = "cinetalk"
USER_COLLECTION = "user"

# APIRouter 생성
sim_router = APIRouter(prefix="/similarity", tags=["Similarity"])

# MongoDB 데이터 가져오기 및 정렬 엔드포인트
@sim_router.get("/list")
async def get_similar_users(
    index: str = Query(..., description="Target index to sort data"),
    top_n: int = Query(10, description="Number of top results to return")
):
    
    # collection_name = f"{datetime.now().strftime('%Y%m%d')}_similarity"
    # collection_name = f"{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}_similarity"
    today = f"{datetime.now().strftime('%Y%m%d')}_similarity"
    yesterday = f"{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}_similarity"

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]

            if today in db.list_collection_names():
                collection = db[today]
            elif yesterday in db.list_collection_names():
                collection = db[yesterday]
            else:
                raise HTTPException(status_code=404, detail="No similarity data")

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


@sim_router.get("/details")
async def get_user_details_by_similarity(
    index: str = Query(..., description="Target index to sort data"),
    top_n: int = Query(10, description="Number of top similar users to fetch")
):
    collection_name = f"{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}_similarity"

    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            similarity_collection = db[collection_name]

            # 기준 index 데이터 검색
            target_doc = similarity_collection.find_one({"index": index})
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
            
            # 상위 N개의 user_id 추출
            user_id_list = [item["user_id"] for item in sorted_items[:top_n]]

            # MongoDB에서 user_id 리스트로 상세 데이터 조회
            user_object_ids = [ObjectId(user_id) for user_id in user_id_list]
            user_collection = db[USER_COLLECTION]
            users = user_collection.find({"_id": {"$in": user_object_ids}})

            # 결과를 리스트로 변환
            user_details = [
                {
                    "user_id": str(user["_id"]),
                    "nickname": user.get("nickname", "닉네임 없음"),
                    "email": user.get("email", "이메일 없음"),
                    "profile": user.get("profile", "프로필 없음"),
                    "similarity": next(
                        (item["similarity"] for item in sorted_items if item["user_id"] == str(user["_id"])),
                        None
                    )  # 정렬된 데이터에서 similarity 추가
                }
                for user in users
            ]

            # 정렬된 결과 반환
            return sorted(user_details, key=lambda x: x["similarity"], reverse=True)

    except Exception as e:
        logging.error(f"Error fetching user details for index {index}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user details.")
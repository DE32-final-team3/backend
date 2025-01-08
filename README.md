# Backend
## 1. 설치 방법
```
docker compose up --build -d
docker compose down 
```

**docker-compose.yml**
```python
services:
  fastapi-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi
    ports:
      - "8000:8000"
    environment:
      # Doppler Token 환경 변수 설정
      DOPPLER_TOKEN: ${DOPPLER_TOKEN}
    volumes:
      - /home/ubuntu/profile_images:/app/profile_images
```

**Dockerfile**
```python
FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y curl

RUN curl -Ls https://cli.doppler.com/install.sh | sh

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["doppler", "run", "--", "uvicorn", "src.final_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 2. API 엔드포인트
### User


### Movie 
1. 영화 저장<br>
    `POST /movie/save`

    - 요청 본문: 저장할 영화를 나타내는 JSON 객체.
    
2. 모든 영화 조회<br>
    `GET /movie/all`
    
    - 설명: 데이터베이스에 저장된 모든 영화를 조회

3. 영화 ID로 조회<br>
    `GET /movie/list`

    - 쿼리 매개변수:   
        - `movie_ids` (list[int]): 조회할 영화 ID 목록.
    - 예시: `/movie/list?movie_ids=1&movie_ids=2`

### Similarity 
**MongoDB 설정**

- MongoDB URI: `mongodb://root:cine@3.37.94.149:27017/?authSource=admin`
- 데이터베이스 이름: cinetalk
- 사용자 컬렉션: user

1. 유사도 기반 사용자 정보 조회<br>
    `GET /similarity/details`

    - 쿼리 매개변수: 
        - `index` (str, 필수): 데이터를 정렬할 대상 인덱스.
    - 설명: 
        - 유사도 데이터 필터링 및 정렬_id 및 자기 자신(index) 데이터를 제외한 나머지 데이터를 대상으로 필터링.
        - 유사도 값을 기준으로 내림차순 정렬.
        - 사용자 세부 정보 조회
        - 상위 유사도 사용자 ID를 기반으로 user 컬렉션에서 사용자 정보를 추출

### TMDB 
1. 영화 검색<br>
    `GET /tmdb/search`

    - 쿼리 매개변수:
        - `q` (str): 검색할 영화 제목.
        - `limit` (int, 기본값: 10): 반환할 영화의 최대 개수.
        - `page` (int, 기본값: 1): TMDB 검색 API에서 요청할 페이지 번호.

2. 영화 ID로 트레일러 반환<br>
    `GET /tmdb/{movieId}/videos`
    
    - 경로 매개변수:
        - movieId (int): 영화 ID.
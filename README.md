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

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치 (curl)
RUN apt-get update && apt-get install -y curl

# Doppler CLI 설치
RUN curl -Ls https://cli.doppler.com/install.sh | sh

# 애플리케이션 파일 복사
COPY . .

# 종속성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 시작 명령어
CMD ["doppler", "run", "--", "uvicorn", "src.final_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 2. API 엔드포인트
### User
1. 회원가입 기능 
2. 회원삭제 기능 : username을 이용하여 삭제
                  (추후 변경 필요)

### Movie 
1. 영화 저장<br>
    `POST /movie/save`

    - 요청 본문: 저장할 영화를 나타내는 JSON 객체.
    
2. 모든 영화 조회<br>
    `GET /movie/all`
    
    - 설명: 데이터베이스에 저장된 모든 영화를 조회

3. 영화 ID로 조회<br>
    `GET /movie/list`

    - 쿼리 매개변수: movie_ids (list[int], 필수): 조회할 영화 ID 목록.
    - 예시: `/movie/list?movie_ids=1&movie_ids=2`

### Similarity 

### TMDB 

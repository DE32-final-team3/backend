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
**MongoDB 설정**

- MongoDB URI: `mongodb://root:cine@3.37.94.149:27017/?authSource=admin`
- 데이터베이스 이름: cinetalk
- 사용자 컬렉션: user

1. 이메일 확인<br>
   `POST /user/check/email`

    - 쿼리 매개변수:
      - `email`: 조회할 email
    - 설명: 데이터베이스에 중복되는 email이 있는지 확인 후
            입력한 email에 회원가입을 위한 인증코드 발송

2. 이메일 인증<br>
    `POST /user/verify/email`

    - 쿼리 매개변수:
      - `code`: 6자리 인증코드
    - 설명: 회원가입하려는 email에 전송된 인증코드 검증

3. 닉네임 확인<br>
    `POST /user/check/nickname`

    - 쿼리 매개변수:
      - `nickname`: 사용하려는 닉네임
    - 설명: 닉네임 중복확인
  
4. 유저 생성(회원가입)<br>
    `POST /user/create`

      - Request body
        - `email`(str): 이메일형식,<br>
          `nickname`(str): 닉네임,<br>
          `profile`(str): 프로필사진경로,<br>
          `password`(str): 비밀번호(hash처리)<br>
      - 설명: 이메일, 닉네임, 비밀번호 입력하여 유저 정보를 데이터베이스에 생성

5. 유저 삭제(회원탈퇴)<br>
    `DELETE /user/delete`

    - Request body
      - `password`(str): 비밀번호(hash처리)
    - 설명: jwt token 검증 후 입력한 비밀번호가 유저 정보와 일치 시 데이터베이스의 유저 정보 삭제
  
6. 로그인<br>
    `POST /user/login`

      - Request body
        - `username`(str): 이메일형식,<br>
          `password`(str): 비밀번호(hash처리)
      - 설명: 이메일, 비밀번호 일치 여부 확인 후 jwt token 생성하여 로그인

7. 유저 정보 <br>
    `POST /user/info`

     - 설명: jwt token을 검증하여 로그인한 유저의 정보를 유지









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

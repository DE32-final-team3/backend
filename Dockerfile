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
#CMD ["uvicorn", "src.final_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["doppler", "run", "--", "uvicorn", "src.final_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
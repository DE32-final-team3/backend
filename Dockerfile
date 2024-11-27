FROM python:3.11

WORKDIR /app

ENV PYTHONPATH=/app

# 필수 패키지 설치 (curl), Doppler CLI 설치
#RUN apt-get update && apt-get install -y curl \
    #curl -Ls https://cli.doppler.com/install.sh | sh 

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 시작 명령어
#CMD ["uvicorn", "src.final_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["doppler", "run", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
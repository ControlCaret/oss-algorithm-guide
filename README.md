# 오픈소스소프트웨어실습 기말고사 대체과제
## Streamlit + FastAPI + Docker + AWS EC2 기반 추천 웹 애플리케이션

### API 키 설정
- `backend/.env` 내에 `GEMINI_API_KEY` 환경 변수 설정

### Docker 빌드 및 실행 방법

#### 서비스 빌드 및 백그라운드 구동
```bash
docker compose up --build -d
```

#### 서비스 중지
```bash
docker compose down
```

# FitPick Django + Docker 실행 안내


- 데스크톱 UI: Flet (`main.py`, `views/`)
- 기존 API: FastAPI (`backend/app.py`)
- 추가 웹 화면: Django (`django_portal/`, `django_dashboard/`)
- 데이터베이스: 두 서버가 함께 사용하는 기존 SQLite (`clothes.db`)
- 컨테이너 실행: Docker Compose (`docker-compose.yml`)

## 가장 쉬운 실행 방법

Docker Desktop을 실행한 뒤, 이 `clothing_app` 폴더에서 다음 명령을 실행합니다.

```bash
docker compose up --build
```

환경에 따라 `docker compose` 대신 아래 명령을 사용합니다.

```bash
docker-compose up --build
```

실행 후 확인할 주소:

- Django 대시보드: http://localhost:8001
- Django 상태 API: http://localhost:8001/health/
- FastAPI Swagger 문서: http://localhost:8000/docs
- FastAPI 상태 확인: http://localhost:8000/

종료:

```bash
docker compose down
```

## Django만 로컬에서 실행

```bash
pip install -r requirements.txt
python manage.py runserver 8001
```

## 기존 Flet 앱 실행

기존 실행 방식은 바뀌지 않았습니다.

```bash
python run_app.py
```

## 발표 때 설명할 수 있는 내용

`Docker Compose`가 FastAPI 서비스와 Django 서비스를 각각 컨테이너로 실행합니다.
두 서비스는 `FITPICK_DB_PATH` 환경변수를 통해 동일한 SQLite 파일을 공유합니다.
Django는 기존 앱 데이터를 읽어 사용자, 옷, 추천 이력, 즐겨찾기, 저장 코디 수와 최근 등록 옷을 웹 대시보드로 보여줍니다.

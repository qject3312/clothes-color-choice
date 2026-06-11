# FitPick 핏픽

FitPick은 사용자가 보유한 옷을 등록하고, 색상·온도·체형·퍼스널 컬러·선호 스타일을 바탕으로 코디를 추천해주는 Python 기반 데스크톱 앱입니다.

사용자는 옷을 사진으로 등록하거나 직접 입력할 수 있으며, 앱은 등록된 옷 정보를 바탕으로 맞춤 코디, 온도별 코디, 오늘의 추천 코디를 제공합니다.

## 주요 기능

- 회원가입 및 로그인
- 게스트 모드 시작
- 사진으로 옷 등록
- 직접 입력으로 옷 등록
- 사진 대표 색상 자동 추출
- 내 옷장 관리
- 맞춤 코디 추천
- 코디해보기
- 온도별 추천
- 오늘의 추천 코디
- 저장 코디 관리
- 프로필 조회 및 수정
- FastAPI 백엔드 자동 실행
- Django 기반 관리자 대시보드
- Docker Compose 실행 지원

## 프로젝트 실행 방법

저장소를 clone합니다.

```bash
git clone https://github.com/qject3312/clothes-color-choice.git
cd clothes-color-choice
```

최종 앱 폴더로 이동합니다.

```bash
cd clothing_app_final
```

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

앱을 실행합니다.

```bash
python run_app.py
```

정상적으로 실행되면 로그인 또는 회원가입 화면이 나타납니다.

## Windows 실행

Windows에서는 다음 파일을 실행할 수 있습니다.

```text
start_windows.bat
```

또는 터미널에서 다음 명령어를 사용할 수 있습니다.

```bash
cd clothing_app_final
python run_app.py
```

## macOS 실행

macOS에서는 다음 파일을 실행할 수 있습니다.

```text
start_mac.command
```

권한 문제가 발생하면 다음 명령어를 한 번 실행합니다.

```bash
cd clothing_app_final
chmod +x start_mac.command start_mac.sh
./start_mac.command
```

## Docker 및 Django 대시보드 실행

최종본에는 데스크톱 앱 외에도 Django 기반 대시보드와 Docker Compose 실행 구성이 포함되어 있습니다.

Docker Desktop을 실행한 뒤 다음 명령어를 사용합니다.

```bash
cd clothing_app_final
docker compose up --build
```

환경에 따라 아래 명령어를 사용할 수도 있습니다.

```bash
docker-compose up --build
```

실행 후 확인할 수 있는 주소는 다음과 같습니다.

| 주소 | 설명 |
|---|---|
| `http://localhost:8001` | Django 대시보드 |
| `http://localhost:8001/health/` | Django 상태 확인 |
| `http://localhost:8000/docs` | FastAPI Swagger 문서 |
| `http://localhost:8000/` | FastAPI 상태 확인 |

종료하려면 다음 명령어를 사용합니다.

```bash
docker compose down
```

## 프로젝트 구조

```text
clothing_app_final/
  main.py
  run_app.py
  api_client.py
  backend_runner.py
  app_paths.py
  backend/
  logic/
  model/
  views/
  django_portal/
  django_dashboard/
  app_data/
  requirements.txt
  requirements-docker.txt
  Dockerfile
  docker-compose.yml
```

## 주요 폴더 설명

| 경로 | 설명 |
|---|---|
| `main.py` | 앱 메인 진입점 |
| `run_app.py` | Windows/macOS 공통 실행용 파일 |
| `api_client.py` | 앱과 FastAPI 백엔드를 연결하는 HTTP 통신 모듈 |
| `backend_runner.py` | 앱 실행 시 백엔드 서버 자동 실행 담당 |
| `app_paths.py` | 운영체제별 DB 및 이미지 경로 처리 |
| `backend/` | FastAPI 서버, SQLite DB, API 스키마 관련 파일 |
| `logic/` | 색상 처리, 사진 분석, 추천 알고리즘 등 핵심 로직 |
| `model/` | 옷과 사용자 데이터 모델 |
| `views/` | 앱 화면 구성 파일 |
| `django_portal/` | Django 프로젝트 설정 |
| `django_dashboard/` | Django 관리자/대시보드 화면 |
| `app_data/images/` | 등록된 옷 사진 저장 위치 |

## 사용 기술

| 구분 | 기술 |
|---|---|
| 언어 | Python |
| UI | Flet |
| 백엔드 | FastAPI, Uvicorn |
| 웹 대시보드 | Django |
| 데이터베이스 | SQLite |
| 이미지 처리 | Pillow |
| HTTP 통신 | requests |
| 컨테이너 | Docker, Docker Compose |
| 버전 관리 | Git, GitHub |

## 문서

- [사용자 가이드](./USER_GUIDE.md)
- [관리자 및 개발자 가이드](./DEVELOPER_GUIDE.md)

## GitHub Repository

https://github.com/qject3312/clothes-color-choice

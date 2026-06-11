# FitPick 핏픽 관리자 및 개발자 가이드

FitPick은 사용자가 보유한 옷을 등록하고, 등록된 옷의 색상·종류·특징·온도·사용자 정보를 바탕으로 코디를 추천하는 Python 기반 데스크톱 앱입니다.

이 문서는 최종 배포 폴더인 `clothing_app_final`을 기준으로 프로젝트를 설치, 실행, 테스트, 관리하기 위한 관리자 및 개발자용 가이드입니다.

## 목차

1. 개발 환경
2. 설치 방법
3. 실행 방법
4. Windows 및 macOS 실행
5. 프로젝트 구조
6. 주요 기능 구조
7. 데이터베이스 및 데이터 관리
8. 백엔드 API
9. 추천 알고리즘
10. Django 대시보드 및 Docker 실행
11. 테스트 방법
12. Git 브랜치 관리
13. 문제 해결 및 주의사항
14. 관리자 확인 체크리스트

---

## 1. 개발 환경

프로젝트 개발 및 실행에 사용되는 주요 기술은 다음과 같습니다.

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
| 실행 플랫폼 | Windows, macOS |

---

## 2. 설치 방법

GitHub 저장소를 clone합니다.

```bash
git clone https://github.com/qject3312/clothes-color-choice.git
cd clothes-color-choice
```

최신 UI 최종 브랜치로 이동합니다.

```bash
git fetch origin
git switch ui_update_v4
```

브랜치가 로컬에 없다면 다음 명령어로 생성 후 이동합니다.

```bash
git switch -c ui_update_v4 origin/ui_update_v4
```

최종 앱 폴더로 이동합니다.

```bash
cd clothing_app_final
```

가상환경을 생성합니다.

```bash
python3 -m venv .venv
```

가상환경을 활성화합니다.

macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

만약 requirements 설치가 되지 않거나 파일이 없는 경우, 필요한 패키지를 직접 설치합니다.

```bash
pip install flet pillow requests fastapi uvicorn sqlalchemy python-multipart django
```

---

## 3. 실행 방법

최종 앱 폴더로 이동합니다.

```bash
cd clothing_app_final
```

권장 실행 파일을 사용하여 프로그램을 실행합니다.

```bash
python run_app.py
```

정상적으로 실행되면 로그인 또는 회원가입 화면이 나타납니다.

앱 실행 시 FastAPI 백엔드 서버가 자동으로 실행되도록 구성되어 있습니다. 자동 실행에 실패할 경우 별도 터미널에서 백엔드 서버를 실행해야 할 수 있습니다.

---

## 4. Windows 및 macOS 실행

### 4.1 Windows 실행

Windows에서는 다음 배치 파일을 사용할 수 있습니다.

```text
start_windows.bat
```

또는 터미널에서 직접 실행할 수 있습니다.

```bash
cd clothing_app_final
python run_app.py
```

### 4.2 macOS 실행

macOS에서는 다음 실행 파일을 사용할 수 있습니다.

```text
start_mac.command
```

권한 문제가 발생하면 다음 명령어를 한 번 실행합니다.

```bash
cd clothing_app_final
chmod +x start_mac.command start_mac.sh
./start_mac.command
```

또는 터미널에서 직접 실행할 수 있습니다.

```bash
cd clothing_app_final
python run_app.py
```

---

## 5. 프로젝트 구조

최종본의 주요 폴더 구조는 다음과 같습니다.

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

각 파일 및 폴더의 역할은 다음과 같습니다.

| 경로 | 설명 |
|---|---|
| `main.py` | Flet 앱 메인 진입점 |
| `run_app.py` | Windows/macOS 공통 실행용 파일 |
| `api_client.py` | Flet 앱과 FastAPI 백엔드를 연결하는 HTTP 통신 모듈 |
| `backend_runner.py` | 앱 실행 시 백엔드 서버 자동 실행 담당 |
| `app_paths.py` | 운영체제별 DB 및 이미지 경로 처리 |
| `backend/` | FastAPI 서버, SQLite DB, API 스키마 관련 파일 |
| `logic/` | 색상 처리, 사진 분석, 추천 알고리즘 등 핵심 로직 |
| `model/` | 옷과 사용자 데이터 모델 |
| `views/` | Flet 기반 화면 구성 파일 |
| `django_portal/` | Django 프로젝트 설정 |
| `django_dashboard/` | Django 관리자/대시보드 화면 |
| `app_data/images/` | 등록된 옷 사진 저장 위치 |
| `requirements.txt` | 일반 실행에 필요한 Python 패키지 목록 |
| `requirements-docker.txt` | Docker 실행에 필요한 패키지 목록 |
| `Dockerfile` | Docker 이미지 빌드 설정 |
| `docker-compose.yml` | FastAPI와 Django 서비스를 함께 실행하는 설정 |

---

## 6. 주요 기능 구조

### 6.1 사용자 관리

사용자 관리 기능은 회원가입, 로그인, 게스트 시작, 프로필 조회 및 수정 기능으로 구성됩니다.

주요 처리 내용은 다음과 같습니다.

- 아이디 중복 검사
- 비밀번호 저장 및 검증
- 사용자 프로필 정보 저장
- 체형, 피부톤, 퍼스널 컬러, 선호 스타일 관리
- 프로필 정보 수정
- 게스트 모드 지원

관련 파일 예시:

```text
backend/
logic/user_logic.py
model/user.py
api_client.py
views/
```

---

### 6.2 옷 관리

옷 관리 기능은 사진 등록, 직접 입력, 옷 목록 조회, 수정, 삭제 기능으로 구성됩니다.

저장되는 주요 정보는 다음과 같습니다.

- 사용자 아이디
- 카테고리
- 세부 종류
- 특징
- 색상 이름
- HEX 색상 코드
- 이미지 경로

관련 파일 예시:

```text
logic/storage.py
logic/image_logic.py
model/clothing.py
views/
```

---

### 6.3 이미지 처리

사진 등록 기능에서는 사용자가 선택한 이미지를 앱 내부 폴더에 저장하고, 이미지에서 대표 색상을 추출합니다.

주요 처리 내용은 다음과 같습니다.

- 이미지 파일 선택
- 이미지 파일 복사 및 저장
- 이미지 경로 저장
- 대표 색상 추출
- 옷장 화면에서 이미지 표시
- 운영체제별 이미지 경로 복구

관련 파일 예시:

```text
logic/image_logic.py
app_paths.py
app_data/images/
views/
```

---

### 6.4 코디 추천

추천 기능은 등록된 옷 조합을 생성하고, 각 조합에 점수를 부여하여 추천 결과를 제공합니다.

추천 기준은 다음과 같습니다.

| 항목 | 설명 |
|---|---|
| 색상 조합 | 상의와 하의의 색상 궁합 |
| 온도 적합도 | 입력한 기온과 옷 두께의 적합성 |
| 체형 보완 | 사용자 체형에 맞는 핏과 색상 |
| 퍼스널 컬러 | 사용자 퍼스널 컬러와 옷 색상 매칭 |
| 선호 스타일 | 사용자가 선택한 스타일과 옷 특징 매칭 |
| 상황 적합도 | 데일리, 학교, 데이트 등 상황 반영 |
| 코디 완성도 | 상하의, 아우터, 신발 조합 완성도 |

관련 파일 예시:

```text
logic/recommend_logic.py
views/
```

---

## 7. 데이터베이스 및 데이터 관리

이 프로젝트는 SQLite 데이터베이스를 사용하여 사용자 정보와 옷 정보를 저장합니다.

### 7.1 users 테이블

| 컬럼 | 설명 |
|---|---|
| `user_id` | 사용자 고유 아이디 |
| `password` | 비밀번호 저장 값 |
| `name` | 사용자 이름 |
| `gender` | 성별 |
| `height` | 키 |
| `weight` | 몸무게 |
| `body_type` | 체형 |
| `skin_tone` | 피부톤 |
| `personal_color` | 퍼스널 컬러 |
| `styles` | 선호 스타일 |

### 7.2 clothes 테이블

| 컬럼 | 설명 |
|---|---|
| `id` | 옷 고유 번호 |
| `user_id` | 소유 사용자 |
| `category` | 옷 종류 |
| `detail` | 세부 종류 |
| `feature` | 핏, 두께, 무드, 계절감 |
| `color_name` | 색상 이름 |
| `color_hex` | HEX 색상 코드 |
| `image_path` | 이미지 저장 경로 |

### 7.3 실행 데이터 관리

실행 중 생성되는 데이터 파일은 GitHub에 올리지 않는 것이 좋습니다.

```text
.venv/
__pycache__/
*.pyc
.DS_Store
clothing_app_final/clothes.db
clothing_app_final/clothes_data.json
clothing_app_final/data/
clothing_app_final/app_data/images/
```

---

## 8. 백엔드 API

백엔드는 사용자, 옷, 추천, 저장 코디 관련 API를 제공합니다.

| 메서드 | 경로 | 기능 |
|---|---|---|
| `POST` | `/users` | 회원가입 |
| `POST` | `/login` | 로그인 |
| `PUT` | `/users/{id}` | 사용자 정보 수정 |
| `GET` | `/clothes` | 옷 목록 조회 |
| `POST` | `/clothes` | 옷 등록 |
| `PUT` | `/clothes/{id}` | 옷 정보 수정 |
| `DELETE` | `/clothes/{id}` | 옷 삭제 |
| `POST` | `/evaluate-outfit` | 코디 평가 |
| `GET` | `/history` | 코디 평가 이력 조회 |
| `POST` | `/recommend-from-photo` | 사진 기반 색상 추천 |
| `POST` | `/recommend-by-cloth` | 개별 옷 기반 색상 추천 |
| `POST` | `/saved-outfits` | 저장 코디 등록 |
| `GET` | `/saved-outfits` | 저장 코디 조회 |
| `DELETE` | `/saved-outfits` | 저장 코디 삭제 |

---

## 9. 추천 알고리즘

추천 알고리즘은 등록된 옷 조합을 생성한 뒤, 각 조합에 점수를 부여하여 높은 점수의 코디를 추천합니다.

주요 평가 기준은 다음과 같습니다.

1. 색상 조합
2. 온도 적합도
3. 체형 보완
4. 퍼스널 컬러
5. 선호 스타일
6. 상황 적합도
7. 코디 완성도

추천 로직은 사용자가 등록한 옷이 많을수록 더 다양한 조합을 생성할 수 있습니다.

최소한 상의와 하의가 등록되어 있어야 기본적인 코디 추천이 가능합니다.

---

## 10. Django 대시보드 및 Docker 실행

최종본에는 기존 데스크톱 앱 외에도 Django 기반 대시보드와 Docker Compose 실행 구성이 포함되어 있습니다.

Docker Desktop을 실행한 뒤 `clothing_app_final` 폴더에서 다음 명령어를 실행합니다.

```bash
docker compose up --build
```

환경에 따라 아래 명령어를 사용할 수도 있습니다.

```bash
docker-compose up --build
```

실행 후 확인할 주소는 다음과 같습니다.

| 주소 | 설명 |
|---|---|
| `http://localhost:8001` | Django 대시보드 |
| `http://localhost:8001/health/` | Django 상태 확인 |
| `http://localhost:8000/docs` | FastAPI Swagger 문서 |
| `http://localhost:8000/` | FastAPI 상태 확인 |

종료 명령어는 다음과 같습니다.

```bash
docker compose down
```

---

## 11. 테스트 방법

최종본에는 기능 수정 사항을 확인하기 위한 테스트 파일이 포함되어 있습니다.

```bash
cd clothing_app_final
python test_feature_fixes.py
```

테스트 항목 예시는 다음과 같습니다.

| 테스트 항목 | 설명 |
|---|---|
| 버튼 UI 폭 확인 | 주요 버튼이 화면 폭에 맞게 표시되는지 확인 |
| 사진 파일명 기반 옷 종류 추측 | 한국어/영어 파일명에서 옷 종류를 추측하는지 확인 |
| 청바지 사진 추론 및 색상 추출 | 이미지에서 하의/청바지와 대표 색상을 추출하는지 확인 |
| Windows 이미지 경로 복구 | 다른 컴퓨터의 이미지 경로도 파일명 기준으로 복구하는지 확인 |
| 사진 등록 화면 빌드 | 사진 등록 화면이 정상 생성되는지 확인 |
| 추천 화면 빌드 | 맞춤 추천, 오늘의 추천, 코디해보기 화면이 정상 생성되는지 확인 |

추가로 기존 기능별 테스트 파일이 있는 경우 다음과 같이 실행할 수 있습니다.

```bash
cd clothing_app_final
python run_all_tests.py
```

---

## 12. Git 브랜치 관리

프로젝트에서 사용한 주요 브랜치는 다음과 같습니다.

| 브랜치 | 설명 |
|---|---|
| `main` | 기본 브랜치 |
| `backend-improvement` | 백엔드 기능 개발 브랜치 |
| `ui_update_v3` | 이전 UI 개선 브랜치 |
| `ui_update_v4` | 최신 UI 최종 업데이트 브랜치 |
| `docs-guides` | 사용자/관리자 가이드 작성 브랜치 |

문서 작업은 기능 코드와 분리하기 위해 `docs-guides` 브랜치에서 진행합니다.

문서 작성 후 커밋하는 방법은 다음과 같습니다.

```bash
git add README.md USER_GUIDE.md DEVELOPER_GUIDE.md
git commit -m "Update guides for final app"
git push origin docs-guides
```

---

## 13. 문제 해결 및 주의사항

### 13.1 ModuleNotFoundError가 발생하는 경우

필요한 패키지가 설치되지 않은 경우입니다. 오류 메시지에 나온 모듈명을 확인하고 설치합니다.

```bash
pip install -r requirements.txt
```

또는 필요한 패키지를 직접 설치합니다.

```bash
pip install flet pillow requests fastapi uvicorn sqlalchemy python-multipart django
```

### 13.2 requirements.txt 설치가 실패하는 경우

최종본 기준 requirements 파일은 `clothing_app_final/requirements.txt`에 있습니다.

```bash
cd clothing_app_final
pip install -r requirements.txt
```

그래도 실패하면 필요한 패키지를 직접 설치합니다.

```bash
pip install flet pillow requests fastapi uvicorn sqlalchemy python-multipart django
```

### 13.3 앱 화면이 운영체제마다 다르게 보이는 경우

Windows와 macOS는 화면 렌더링 방식이 다를 수 있습니다.

최종 시연 및 화면 캡처는 팀에서 정한 실행 환경을 기준으로 진행하는 것이 좋습니다.

### 13.4 이미지가 표시되지 않는 경우

이미지 파일 경로가 변경되었거나 이미지 파일이 삭제된 경우 표시되지 않을 수 있습니다.

이미지 등록 후에는 앱 내부 이미지 저장 폴더를 임의로 삭제하지 않는 것이 좋습니다.

### 13.5 백엔드 연결 오류가 발생하는 경우

앱 실행 시 백엔드 서버가 자동으로 실행되지 않을 수 있습니다.

이 경우 프로그램을 재시작하거나, 별도 터미널에서 백엔드 서버를 실행합니다.

```bash
cd clothing_app_final
uvicorn backend.app:app --reload
```

### 13.6 Docker 실행 오류가 발생하는 경우

Docker Desktop이 실행 중인지 확인합니다.

그 후 다음 명령어를 다시 실행합니다.

```bash
cd clothing_app_final
docker compose up --build
```

포트 충돌이 발생할 경우 8000번 또는 8001번 포트를 사용하는 다른 프로그램을 종료해야 합니다.

### 13.7 Git에 올리면 안 되는 파일

다음 파일들은 실행 중 자동으로 생성되는 파일이므로 GitHub에 올리지 않는 것이 좋습니다.

```text
.venv/
__pycache__/
*.pyc
.DS_Store
clothing_app_final/clothes.db
clothing_app_final/data/
clothing_app_final/app_data/images/
```

---

## 14. 관리자 확인 체크리스트

최종 제출 전 관리자는 다음 항목을 확인합니다.

- 최종 앱 폴더가 `clothing_app_final`인지 확인
- 실행 파일이 `run_app.py`인지 확인
- 앱이 정상 실행되는지 확인
- 회원가입 및 로그인이 가능한지 확인
- 사진 등록과 직접 등록이 가능한지 확인
- 내 옷장에서 등록한 옷이 표시되는지 확인
- 맞춤 추천과 온도별 추천이 작동하는지 확인
- 오늘의 추천과 저장 코디가 작동하는지 확인
- 프로필 수정이 작동하는지 확인
- Django 대시보드가 필요한 경우 정상 실행되는지 확인
- Docker Compose 실행이 필요한 경우 정상 작동하는지 확인
- 불필요한 실행 데이터 파일이 GitHub에 올라가지 않았는지 확인
- README, 사용자 가이드, 개발자 가이드가 최신 내용인지 확인

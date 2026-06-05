# 옷 추천 앱 (Flet 버전)

색상 조합과 온도를 기반으로 옷을 추천하는 풀스택 앱.
**Windows와 macOS 모두에서 동일하게 작동**합니다.

## 주요 기능

- 🔐 **로그인 / 회원가입** - FastAPI 백엔드 + SQLite
- 🏠 **홈** - 6개 메뉴 카드 그리드
- 📥 **옷 등록** - 사진 또는 직접 입력 (백엔드 저장)
- 👕 **내 옷장** - 등록된 옷 목록 + 삭제
- 🎨 **코디해보기** - 백엔드 평가 API 연동
- 💜 **맞춤 코디** - 색상 추천
- 🌡️ **온도별 추천** - 날씨 기반
- 📚 **오늘의 코디** - 히스토리
- 👤 **프로필** - 사용자 정보 + 통계

## 아키텍처

```
[Flet UI] ←→ [api_client.py] ←→ [FastAPI Backend] ←→ [SQLite DB]
```

- **Frontend**: Flet (Python)
- **Backend**: FastAPI (자동 실행)
- **DB**: SQLite (clothes.db)

## 빠른 실행

### Windows
프로젝트 폴더에서 `start_app.bat` 더블클릭.

### macOS / Linux
```bash
cd clothing_app
./run_mac.sh
```

> 첫 실행 시 의존성이 자동 설치됩니다.
> 백엔드(FastAPI)도 자동으로 함께 시작됩니다.

## 수동 설치

### 1. Python 설치 확인
Python 3.9 이상 필요.

### 2. 의존성 설치
```bash
pip install -r requirements.txt    # Windows
pip3 install -r requirements.txt   # macOS / Linux
```

### 3. 실행
```bash
python main.py    # Windows
python3 main.py   # macOS / Linux
```

`main.py`가 자동으로 백엔드도 함께 시작합니다.

## 폴더 구조

```
clothing_app/
├── main.py                  # Flet 진입점 + 라우팅
├── backend_runner.py        # FastAPI 백엔드 자동 실행
├── api_client.py            # 백엔드 API 호출
├── requirements.txt
├── start_app.bat            # Windows 실행
├── run_mac.sh               # macOS 실행
├── backend/                 # FastAPI 서버
│   ├── app.py
│   ├── api.py
│   ├── database.py
│   ├── schemas.py
│   └── outfit_logic.py
├── model/                   # 데이터 모델
│   ├── clothing.py
│   └── user.py
├── logic/                   # 비즈니스 로직
│   ├── color_logic.py
│   ├── recommend_logic.py
│   └── ...
└── views/                   # Flet UI
    ├── theme.py             # 디자인 토큰
    ├── components.py        # 공통 컴포넌트
    ├── auth_view.py         # 로그인/회원가입
    ├── home_view.py
    ├── register_view.py
    ├── list_view.py
    ├── coordinate_view.py
    ├── custom_view.py
    ├── temperature_view.py
    ├── today_view.py
    └── profile_view.py
```

## 호환성

| 항목 | Windows | macOS | Linux |
|-----|---------|-------|-------|
| 기본 동작 | ✅ | ✅ | ✅ |
| 한글 폰트 | ✅ (맑은 고딕) | ✅ (Apple SD Gothic) | ⚠️ Noto Sans 필요 |
| 사진 등록 | ✅ | ✅ | ✅ |
| 백엔드 자동 실행 | ✅ | ✅ | ✅ |

## 디자인 커스터마이징

`views/theme.py`의 토큰만 수정하면 전체 디자인이 한 번에 바뀝니다.

```python
COLORS["primary"] = "#ff6b9d"  # 메인 컬러를 핑크로
RADIUS["lg"] = 24              # 카드 모서리 더 둥글게
```

## 문제 해결

### "ConnectionError" 또는 백엔드 연결 실패
- 포트 8000이 사용 중일 수 있음 - 다른 프로세스 종료 후 재시도
- 또는 `게스트로 시작하기`로 오프라인 모드 사용

### Windows에서 한글 깨짐
터미널을 UTF-8 모드로: `chcp 65001`

### macOS에서 색상 안 보임
Python 3.14 사용 중이라면 3.12로 다운그레이드 권장:
```bash
brew install python@3.12
python3.12 main.py
```

### Flet 모듈 못 찾음
```bash
pip install -r requirements.txt
```

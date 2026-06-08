# FitPick 핏픽

FitPick은 사용자가 보유한 옷을 등록하고, 색상·온도·체형·퍼스널 컬러·선호 스타일을 바탕으로 코디를 추천해주는 Python 기반 데스크톱 앱입니다.

## 주요 기능

- 회원가입 및 로그인
- 사진으로 옷 등록
- 직접 입력으로 옷 등록
- 내 옷장 관리
- 맞춤 코디 추천
- 코디해보기
- 온도별 추천
- 오늘의 추천 코디
- 저장 코디 관리
- 프로필 조회 및 수정

## 프로젝트 실행 방법

저장소를 clone합니다.

```bash
git clone https://github.com/qject3312/clothes-color-choice.git
cd clothes-color-choice

````

필요한 패키지를 설치합니다.

```bash
pip install -r clothing_app/requirements.txt
````

앱을 실행합니다.

```bash
cd clothing_app
python main.py
```

정상적으로 실행되면 로그인 또는 회원가입 화면이 나타납니다.

## 프로젝트 구조

```text
clothing_app/
  main.py
  api_client.py
  backend/
  logic/
  model/
  ui/
  data/
  app_data/
```

## 사용 기술

| 구분      | 기술               |
| ------- | ---------------- |
| 언어      | Python           |
| 백엔드     | FastAPI, Uvicorn |
| 데이터베이스  | SQLite           |
| 이미지 처리  | Pillow           |
| HTTP 통신 | requests         |
| 버전 관리   | Git, GitHub      |

## 문서

* [사용자 가이드](./USER_GUIDE.md)
* [관리자 및 개발자 가이드](./DEVELOPER_GUIDE.md)

## GitHub Repository

https://github.com/qject3312/clothes-color-choice


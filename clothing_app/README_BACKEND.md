# Backend Guide

## 구현 기능

이 브랜치에서는 옷 추천 앱의 백엔드 기능을 보강했습니다.

구현한 기능은 다음과 같습니다.

1. 옷 데이터 저장 및 불러오기
2. 회원가입, 로그인, 사용자 정보 조회 및 수정
3. 옷 사진 파일 저장 및 삭제 관리
4. clothing_id 기반 옷 삭제
5. 기본 코디 추천
6. 온도 기반 코디 추천

## 주요 파일

- clothing_app/logic/storage.py
- clothing_app/logic/user_logic.py
- clothing_app/logic/image_logic.py
- clothing_app/logic/recommend_logic.py
- clothing_app/model/user.py

## 테스트 파일

- clothing_app/test_storage.py
- clothing_app/test_user.py
- clothing_app/test_image.py
- clothing_app/test_delete.py
- clothing_app/test_recommend.py
- clothing_app/run_all_tests.py

## 실행 환경 설정

프로젝트 루트에서 아래 명령어를 실행합니다.

python3 -m venv .venv  
source .venv/bin/activate  
pip install -r requirements.txt

## 전체 백엔드 테스트 실행

cd clothing_app  
python run_all_tests.py

## 개별 테스트 실행

python test_storage.py  
python test_user.py  
python test_image.py  
python test_delete.py  
python test_recommend.py

## 테스트 내용 요약

### test_storage.py

옷 데이터를 JSON 파일로 저장하고 다시 불러오는 기능을 테스트합니다.

### test_user.py

회원가입, 중복 회원가입 방지, 로그인, 사용자 정보 조회, 사용자 정보 수정, 잘못된 비밀번호 로그인 실패 처리를 테스트합니다.

### test_image.py

테스트 이미지를 생성한 뒤 앱 내부 이미지 폴더에 저장하고, 저장된 이미지 삭제까지 테스트합니다.

### test_delete.py

테스트용 옷을 추가한 뒤 clothing_id를 기준으로 삭제하고, 존재하지 않는 ID 삭제 실패 처리를 테스트합니다.

### test_recommend.py

등록된 옷을 기반으로 기본 코디 추천과 온도 기반 추천 기능을 테스트합니다.

## Git 제외 파일

다음 파일들은 실제 실행 데이터이므로 GitHub에 올리지 않습니다.

- .venv/
- clothing_app/clothes_data.json
- clothing_app/data/*.json
- clothing_app/images/clothes/*
- __pycache__/
- *.pyc
- .DS_Store

## 참고

UI 화면에서 직접 기능 확인이 어려운 경우에도, 백엔드 기능은 각 테스트 파일을 통해 독립적으로 검증할 수 있습니다.
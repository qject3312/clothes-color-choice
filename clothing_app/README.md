# 옷 추천 앱 (Flet 버전 - 전체 기능)

## 화면 구성

✅ **홈 화면** - 6개 메뉴 카드 그리드  
✅ **옷 등록 (선택)** - 사진 / 직접 입력 선택  
✅ **옷 등록 (직접)** - 종류, 색상, 특징 입력  
✅ **내 옷장** - 등록된 옷 목록 + 삭제  
✅ **코디해보기** - 상의/하의 매칭 평가  
✅ **맞춤 코디** - 색상 선택 → 어울리는 색 추천  
✅ **온도별 추천** - 기온 입력 → 의상 추천  
✅ **나의 코디** - 저장된 조합 보기  
✅ **프로필** - 사용자 정보 + 옷장 통계  

## 설치 및 실행

```bash
pip3 install flet
cd clothing_flet
python3 main.py
```

## 디자인 커스터마이징

`views/theme.py` 의 토큰 값을 수정하면 전체 디자인이 한 번에 바뀝니다.

```python
COLORS["primary"] = "#ff6b9d"   # 메인 컬러를 핑크로
RADIUS["lg"] = 24                # 카드 모서리 더 둥글게
```

## 구조

```
clothing_flet/
├── main.py                    # 진입점 + 라우팅
├── model/clothing.py          # 데이터 모델
├── logic/
│   ├── color_logic.py         # RGB → 색이름
│   └── recommend_logic.py     # 추천 알고리즘
└── views/
    ├── theme.py               # 디자인 토큰
    ├── components.py          # 공통 UI (상단바, 카드 등)
    ├── home_view.py
    ├── register_view.py
    ├── list_view.py
    ├── coordinate_view.py
    ├── custom_view.py
    ├── temperature_view.py
    ├── my_outfits_view.py
    └── profile_view.py
```

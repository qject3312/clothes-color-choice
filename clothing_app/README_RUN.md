# 핏픽 실행 방법

## Windows
1. Python 3.10 이상 설치
2. `clothing_app` 폴더에서 `start_windows.bat` 실행

직접 실행할 때는 터미널에서:
```bash
cd clothing_app
python run_app.py
```
또는
```bash
cd clothing_app
py run_app.py
```

## macOS
1. Python 3.10 이상 설치
2. `start_mac.command` 더블클릭

권한 오류가 나오면 터미널에서 한 번만 실행:
```bash
cd clothing_app
chmod +x start_mac.command start_mac.sh
./start_mac.command
```

직접 실행할 때는:
```bash
cd clothing_app
python3 run_app.py
```

## 호환성 보강 내용
- `run_app.py`를 추가해서 Windows/macOS 모두 같은 방식으로 실행 가능하게 했습니다.
- `app_paths.py`를 추가해서 DB와 이미지 저장 경로를 운영체제별로 자동 처리합니다.
- `clothes.db`, `app_data/images`는 앱 폴더 기준으로 생성/사용됩니다.
- 이미지 경로는 가능한 경우 상대경로로 저장되어 폴더를 다른 컴퓨터로 옮겨도 깨질 가능성을 줄였습니다.
- Windows 전용 `.bat` 외에 macOS용 `.command`, `.sh` 실행 파일을 추가했습니다.

## macOS에서 그래도 안 될 때
macOS 기본 Python/Tkinter 조합 문제일 수 있습니다. 이 경우 python.org에서 받은 Python 3.11 또는 3.12로 실행하는 것이 가장 안정적입니다.

## 사진 옷 종류 자동 추측 개선 내용
- 파일명 키워드(한국어/영어/쇼핑몰식 이름)를 더 많이 인식하도록 확장했습니다.
- 이미지의 배경색을 먼저 추정한 뒤, 옷으로 보이는 가장 큰 영역을 분리해서 분석합니다.
- 옷 영역의 가로/세로 비율, 위쪽/중앙/아래쪽 폭, 면적, 파란색 비율을 이용해 반팔·긴팔·셔츠·하의·청바지·슬랙스·신발·가방 등을 더 세분화해서 추측합니다.
- AI 모델을 새로 설치하지 않고 PIL 기반으로 동작하므로 Windows/Mac 호환성을 유지합니다.

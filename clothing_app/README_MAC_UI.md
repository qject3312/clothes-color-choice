# macOS 실행 안내

이 버전은 Flet 데스크톱 UI를 Windows와 macOS에서 같은 코드로 실행합니다.

## 실행

```bash
cd clothing_app
chmod +x install_requirements_mac.sh start_mac.sh start_mac.command
./install_requirements_mac.sh
./start_mac.sh
```

Finder에서 실행할 때는 `start_mac.command`를 더블클릭해도 됩니다.

## 실행이 되지 않으면

대부분 아래 둘 중 하나입니다.

1. 예전 압축파일이나 예전 Git 브랜치를 실행한 경우
2. macOS에 설치된 Python이 너무 오래된 경우

이때는 터미널에서 다음을 확인하세요.

```bash
python3 --version
```

Python 3.10 이상을 권장합니다. Windows에서 등록한 이미지 경로가 DB에 남아 있어도
macOS에서는 이미지 파일명으로 `app_data/images`에서 다시 찾습니다.

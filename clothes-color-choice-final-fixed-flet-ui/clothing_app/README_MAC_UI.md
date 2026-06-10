# macOS 실행 안내

이 버전은 가장 최근 수정본을 기준으로 macOS Tkinter 렌더링 차이를 줄이도록 패치한 버전입니다.

## 실행

```bash
cd clothing_app
chmod +x install_requirements_mac.sh start_mac.sh start_mac.command
./install_requirements_mac.sh
./start_mac.sh
```

Finder에서 실행할 때는 `start_mac.command`를 더블클릭해도 됩니다.

## macOS에서 버튼이 회색으로 보였던 이유

macOS 기본 Tkinter는 일반 `tk.Button`의 `bg`, `fg` 색상을 무시하는 경우가 있습니다.
그래서 이 버전에서는 macOS일 때 색상 버튼을 `Label` 기반 커스텀 버튼으로 자동 대체합니다.

## 그래도 구버전처럼 보이면

대부분 아래 둘 중 하나입니다.

1. 예전 압축파일이나 예전 Git 브랜치를 실행한 경우
2. macOS에 설치된 Python/Tkinter가 너무 오래된 경우

이때는 터미널에서 다음을 확인하세요.

```bash
python3 -m tkinter
python3 --version
```

Python은 3.10 이상을 권장합니다.

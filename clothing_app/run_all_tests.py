import subprocess
import sys


test_files = [
    "test_storage.py",
    "test_user.py",
    "test_image.py",
    "test_delete.py",
    "test_recommend.py",
]


for test_file in test_files:
    print(f"\n===== {test_file} 실행 =====")
    result = subprocess.run([sys.executable, test_file])

    if result.returncode != 0:
        print(f"{test_file} 실행 중 오류 발생")
        sys.exit(result.returncode)

print("\n모든 백엔드 테스트가 정상적으로 완료되었습니다.")

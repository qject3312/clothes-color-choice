import os
from PIL import Image

from logic.image_logic import save_clothing_image, delete_clothing_image, get_image_dir


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_IMAGE_PATH = os.path.join(BASE_DIR, "test_sample_image.png")


def create_test_image():
    image = Image.new("RGB", (100, 100), color=(255, 255, 255))
    image.save(TEST_IMAGE_PATH)


print("===== 테스트 이미지 생성 =====")
create_test_image()
print("테스트 이미지 경로:", TEST_IMAGE_PATH)
print("테스트 이미지 존재 여부:", os.path.exists(TEST_IMAGE_PATH))


print("\n===== 옷 이미지 저장 테스트 =====")
save_result = save_clothing_image(TEST_IMAGE_PATH)

print("저장 성공 여부:", save_result["success"])
print("메시지:", save_result["message"])
print("저장된 이미지 경로:", save_result["image_path"])
print("저장된 이미지 존재 여부:", os.path.exists(save_result["image_path"]))


print("\n===== 이미지 저장 폴더 확인 =====")
print("이미지 저장 폴더:", get_image_dir())


print("\n===== 옷 이미지 삭제 테스트 =====")
delete_result = delete_clothing_image(save_result["image_path"])

print("삭제 성공 여부:", delete_result["success"])
print("메시지:", delete_result["message"])
print("삭제 후 이미지 존재 여부:", os.path.exists(save_result["image_path"]))


print("\n===== 테스트용 원본 이미지 정리 =====")
if os.path.exists(TEST_IMAGE_PATH):
    os.remove(TEST_IMAGE_PATH)

print("원본 테스트 이미지 존재 여부:", os.path.exists(TEST_IMAGE_PATH))
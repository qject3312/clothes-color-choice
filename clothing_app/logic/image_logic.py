import os
import shutil
import uuid


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "images", "clothes")


def ensure_image_dir():
    os.makedirs(IMAGE_DIR, exist_ok=True)


def save_clothing_image(original_path):
    ensure_image_dir()

    if not original_path:
        return {
            "success": False,
            "message": "이미지 경로가 비어 있습니다.",
            "image_path": ""
        }

    if not os.path.exists(original_path):
        return {
            "success": False,
            "message": "이미지 파일을 찾을 수 없습니다.",
            "image_path": ""
        }

    _, ext = os.path.splitext(original_path)

    if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        return {
            "success": False,
            "message": "지원하지 않는 이미지 형식입니다.",
            "image_path": ""
        }

    new_filename = f"{uuid.uuid4()}{ext.lower()}"
    new_path = os.path.join(IMAGE_DIR, new_filename)

    shutil.copy2(original_path, new_path)

    return {
        "success": True,
        "message": "이미지 저장 성공",
        "image_path": new_path
    }


def delete_clothing_image(image_path):
    if not image_path:
        return {
            "success": False,
            "message": "삭제할 이미지 경로가 비어 있습니다."
        }

    if not os.path.exists(image_path):
        return {
            "success": False,
            "message": "이미지 파일이 존재하지 않습니다."
        }

    os.remove(image_path)

    return {
        "success": True,
        "message": "이미지 삭제 성공"
    }


def get_image_dir():
    ensure_image_dir()
    return IMAGE_DIR
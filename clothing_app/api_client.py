import requests

BASE_URL = "http://127.0.0.1:8000"

def add_clothing_to_backend(item):
    data = {
        "category": item.category,
        "detail": item.detail,
        "feature": item.feature,
        "color_name": item.color_name,
        "color_hex": item.hex,
        "image_path": item.image_path
    }

def add_clothing_to_backend(item):
    data = {
        "category": item.category,
        "detail": item.detail,
        "feature": item.feature,
        "color_name": item.color_name,
        "color_hex": item.hex,
        "image_path": item.image_path
    }

    try:
        response = requests.post(
            f"{BASE_URL}/clothes",
            json=data,
            timeout=3
        )

        print("==== 저장 요청 ====")
        print("보낸 데이터:", data)
        print("상태코드:", response.status_code)
        print("응답:", response.text)

        return response.json()

    except Exception as e:
        print("저장 실패:", e)
        return {"error": str(e)}


def get_clothes_from_backend():
    response = requests.get(f"{BASE_URL}/clothes")
    return response.json()


def evaluate_outfit_backend(data):
    response = requests.post(f"{BASE_URL}/evaluate-outfit", json=data)
    return response.json()


def get_history_from_backend():
    response = requests.get(f"{BASE_URL}/history")
    return response.json()

def recommend_from_photo_backend(color_name, category, target_category):
    data = {
        "color_name": color_name,
        "category": category,
        "target_category": target_category
    }

    response = requests.post(
        f"{BASE_URL}/recommend-from-photo",
        json=data
    )

    return response.json()

def recommend_by_cloth_backend(category, color_name, detail):
    data = {
        "category": category,
        "color_name": color_name,
        "detail": detail
    }

    response = requests.post(
        f"{BASE_URL}/recommend-by-cloth",
        json=data,
        timeout=3
    )

    print("추천 요청 상태코드:", response.status_code)
    print("추천 응답 내용:", response.text)

    return response.json()
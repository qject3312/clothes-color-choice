import requests

BASE_URL = "http://127.0.0.1:8765"


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return {"error": response.text}


def signup_user_backend(user):
    try:
        response = requests.post(f"{BASE_URL}/users", json=user, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def login_user_backend(user_id, password):
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"user_id": user_id, "password": password},
            timeout=3,
        )
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def update_user_backend(user):
    try:
        user_id = user.get("user_id", "")
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=user, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def add_clothing_to_backend(item, user_id="guest"):
    data = {
        "user_id": user_id,
        "category": item.category,
        "detail": item.detail,
        "feature": item.feature,
        "color_name": item.color_name,
        "color_hex": item.hex,
        "image_path": item.image_path,
    }

    try:
        response = requests.post(f"{BASE_URL}/clothes", json=data, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def get_clothes_from_backend(user_id="guest"):
    try:
        response = requests.get(f"{BASE_URL}/clothes", params={"user_id": user_id}, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def delete_clothing_backend(clothing_id, user_id="guest"):
    try:
        response = requests.delete(
            f"{BASE_URL}/clothes/{clothing_id}",
            params={"user_id": user_id},
            timeout=3,
        )
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def evaluate_outfit_backend(data):
    response = requests.post(f"{BASE_URL}/evaluate-outfit", json=data)
    return response.json()


def get_history_from_backend(user_id="guest"):
    response = requests.get(f"{BASE_URL}/history", params={"user_id": user_id})
    return response.json()


def recommend_from_photo_backend(color_name, category, target_category):
    data = {
        "color_name": color_name,
        "category": category,
        "target_category": target_category,
    }

    response = requests.post(f"{BASE_URL}/recommend-from-photo", json=data)
    return response.json()


def recommend_by_cloth_backend(category, color_name, detail):
    data = {
        "category": category,
        "color_name": color_name,
        "detail": detail,
    }

    response = requests.post(f"{BASE_URL}/recommend-by-cloth", json=data, timeout=3)
    return response.json()


def update_clothing_backend(clothing_id, item, user_id="guest"):
    data = {
        "user_id": user_id,
        "category": item.category,
        "detail": item.detail,
        "feature": item.feature,
        "color_name": item.color_name,
        "color_hex": item.hex,
    }
    try:
        response = requests.put(f"{BASE_URL}/clothes/{clothing_id}", json=data, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def save_outfit_backend(outfit, user_id="guest"):
    try:
        response = requests.post(
            f"{BASE_URL}/saved-outfits",
            json={"user_id": user_id, "outfit_data": outfit},
            timeout=3,
        )
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def get_saved_outfits_backend(user_id="guest"):
    try:
        response = requests.get(f"{BASE_URL}/saved-outfits", params={"user_id": user_id}, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}


def delete_saved_outfit_backend(outfit_id, user_id="guest"):
    try:
        response = requests.delete(f"{BASE_URL}/saved-outfits/{outfit_id}", params={"user_id": user_id}, timeout=3)
        return _safe_json(response)
    except Exception as e:
        return {"error": str(e)}

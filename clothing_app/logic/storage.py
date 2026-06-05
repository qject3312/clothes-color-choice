import json
import os
import uuid
from model.clothing import Clothing
from logic.image_logic import delete_clothing_image


DATA_FILE = "clothes_data.json"


def clothing_to_dict(clothing):
    if not hasattr(clothing, "clothing_id"):
        clothing.clothing_id = str(uuid.uuid4())

    return {
        "clothing_id": clothing.clothing_id,
        "category": clothing.category,
        "detail": clothing.detail,
        "feature": clothing.feature,
        "rgb": list(clothing.rgb),
        "hex": clothing.hex,
        "color_name": clothing.color_name,
        "image_path": clothing.image_path,
        "colors": [
            {
                "rgb": list(color["rgb"]),
                "hex": color["hex"],
                "name": color["name"]
            }
            for color in clothing.colors
        ]
    }


def dict_to_clothing(data):
    colors = []

    for color in data.get("colors", []):
        colors.append({
            "rgb": tuple(color["rgb"]),
            "hex": color["hex"],
            "name": color["name"]
        })

    clothing = Clothing(
        category=data["category"],
        detail=data["detail"],
        feature=data["feature"],
        rgb=tuple(data["rgb"]),
        hex_code=data["hex"],
        color_name=data["color_name"],
        image_path=data.get("image_path", ""),
        colors=colors
)
    clothing.clothing_id = data.get("clothing_id", str(uuid.uuid4()))

    return clothing


def save_clothes(clothes):
    data = [clothing_to_dict(clothing) for clothing in clothes]

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_clothes():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [dict_to_clothing(item) for item in data]

    except Exception as error:
        print("옷 데이터를 불러오는 중 오류 발생:", error)
        return []
    

def add_clothing(clothing):
    clothes = load_clothes()

    if not hasattr(clothing, "clothing_id"):
        clothing.clothing_id = str(uuid.uuid4())

    clothes.append(clothing)
    save_clothes(clothes)

    return {
        "success": True,
        "message": "옷 추가 완료",
        "clothing": clothing
    }


def delete_clothing_by_id(clothing_id, delete_image=True):
    clothes = load_clothes()

    for clothing in clothes:
        if getattr(clothing, "clothing_id", None) == clothing_id:
            clothes.remove(clothing)

            if delete_image and clothing.image_path:
                delete_clothing_image(clothing.image_path)

            save_clothes(clothes)

            return {
                "success": True,
                "message": "옷 삭제 완료",
                "deleted_clothing": clothing
            }

    return {
        "success": False,
        "message": "해당 ID의 옷을 찾을 수 없습니다.",
        "deleted_clothing": None
    }


def get_clothing_by_id(clothing_id):
    clothes = load_clothes()

    for clothing in clothes:
        if getattr(clothing, "clothing_id", None) == clothing_id:
            return {
                "success": True,
                "message": "옷 조회 성공",
                "clothing": clothing
            }

    return {
        "success": False,
        "message": "해당 ID의 옷을 찾을 수 없습니다.",
        "clothing": None
    }
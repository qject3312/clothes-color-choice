import json
import os
from model.clothing import Clothing


DATA_FILE = "clothes_data.json"


def clothing_to_dict(clothing):
    return {
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

    return Clothing(
        category=data["category"],
        detail=data["detail"],
        feature=data["feature"],
        rgb=tuple(data["rgb"]),
        hex_code=data["hex"],
        color_name=data["color_name"],
        image_path=data.get("image_path", ""),
        colors=colors
    )


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
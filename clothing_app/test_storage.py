from model.clothing import Clothing
from logic.storage import save_clothes, load_clothes


sample_clothes = [
    Clothing(
        category="상의",
        detail="반팔",
        feature="기본",
        rgb=(255, 255, 255),
        hex_code="#FFFFFF",
        color_name="흰색",
        image_path="",
        colors=[
            {
                "rgb": (255, 255, 255),
                "hex": "#FFFFFF",
                "name": "흰색"
            }
        ]
    ),
    Clothing(
        category="하의",
        detail="청바지",
        feature="기본",
        rgb=(0, 0, 255),
        hex_code="#0000FF",
        color_name="파랑",
        image_path="",
        colors=[
            {
                "rgb": (0, 0, 255),
                "hex": "#0000FF",
                "name": "파랑"
            }
        ]
    ),
    Clothing(
        category="아우터",
        detail="자켓",
        feature="기본",
        rgb=(0, 0, 0),
        hex_code="#000000",
        color_name="검정",
        image_path="",
        colors=[
            {
                "rgb": (0, 0, 0),
                "hex": "#000000",
                "name": "검정"
            }
        ]
    )
]

save_clothes(sample_clothes)

loaded_clothes = load_clothes()

print("저장 후 불러온 옷 목록:")
for cloth in loaded_clothes:
    print(cloth.category, cloth.detail, cloth.color_name, cloth.hex)
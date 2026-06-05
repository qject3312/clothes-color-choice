from model.clothing import Clothing
from logic.storage import add_clothing, load_clothes, delete_clothing_by_id


print("===== 삭제 테스트용 옷 추가 =====")

test_clothing = Clothing(
    category="상의",
    detail="맨투맨",
    feature="삭제 테스트용",
    rgb=(120, 120, 120),
    hex_code="#787878",
    color_name="회색",
    image_path="",
    colors=[
        {
            "rgb": (120, 120, 120),
            "hex": "#787878",
            "name": "회색"
        }
    ]
)

add_result = add_clothing(test_clothing)

print("추가 성공 여부:", add_result["success"])
print("메시지:", add_result["message"])

added_clothing = add_result["clothing"]
print("추가된 옷 ID:", added_clothing.clothing_id)
print("추가된 옷:", added_clothing.category, added_clothing.detail, added_clothing.color_name)


print("\n===== 삭제 전 옷 목록 =====")
before_clothes = load_clothes()
print("삭제 전 옷 개수:", len(before_clothes))

for clothing in before_clothes:
    print(
        getattr(clothing, "clothing_id", "ID 없음"),
        clothing.category,
        clothing.detail,
        clothing.color_name
    )


print("\n===== 옷 삭제 테스트 =====")
delete_result = delete_clothing_by_id(added_clothing.clothing_id)

print("삭제 성공 여부:", delete_result["success"])
print("메시지:", delete_result["message"])

if delete_result["deleted_clothing"] is not None:
    deleted = delete_result["deleted_clothing"]
    print("삭제된 옷:", deleted.category, deleted.detail, deleted.color_name)


print("\n===== 삭제 후 옷 목록 =====")
after_clothes = load_clothes()
print("삭제 후 옷 개수:", len(after_clothes))

for clothing in after_clothes:
    print(
        getattr(clothing, "clothing_id", "ID 없음"),
        clothing.category,
        clothing.detail,
        clothing.color_name
    )


print("\n===== 존재하지 않는 ID 삭제 테스트 =====")
fail_result = delete_clothing_by_id("not-existing-id")

print("삭제 성공 여부:", fail_result["success"])
print("메시지:", fail_result["message"])
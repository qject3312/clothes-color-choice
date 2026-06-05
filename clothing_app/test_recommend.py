from logic.storage import load_clothes
from logic.recommend_logic import recommend_outfit, recommend_by_temperature


clothes = load_clothes()

print("===== 등록된 옷 목록 =====")
print("총 옷 개수:", len(clothes))

for clothing in clothes:
    print(
        clothing.category,
        clothing.detail,
        clothing.color_name,
        clothing.hex
    )


print("\n===== 기본 코디 추천 테스트 =====")
result = recommend_outfit(clothes)

print("추천 성공 여부:", result["success"])
print("메시지:", result["message"])

if result["success"]:
    top = result["top"]
    bottom = result["bottom"]
    outer = result["outer"]

    print("상의:", top.detail, top.color_name, top.hex)
    print("하의:", bottom.detail, bottom.color_name, bottom.hex)

    if outer is not None:
        print("아우터:", outer.detail, outer.color_name, outer.hex)
    else:
        print("아우터: 없음")

    print("추천 이유:", result["reason"])
else:
    print("실패 이유:", result["message"])


print("\n===== 온도 기반 추천 테스트 =====")
temperature_result = recommend_by_temperature(clothes, 18)

print("추천 성공 여부:", temperature_result["success"])
print("메시지:", temperature_result["message"])

if temperature_result["success"]:
    top = temperature_result["top"]
    bottom = temperature_result["bottom"]
    outer = temperature_result["outer"]

    print("상의:", top.detail, top.color_name, top.hex)
    print("하의:", bottom.detail, bottom.color_name, bottom.hex)

    if outer is not None:
        print("아우터:", outer.detail, outer.color_name, outer.hex)
    else:
        print("아우터: 없음")

    print("추천 이유:", temperature_result["reason"])
else:
    print("실패 이유:", temperature_result["message"])
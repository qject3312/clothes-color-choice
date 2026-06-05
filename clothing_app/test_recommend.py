from logic.storage import load_clothes
from logic.recommend_logic import recommend_outfits, format_item


test_user = {
    "user_id": "testuser",
    "username": "testuser",
    "nickname": "테스트유저",
    "style": "캐주얼"
}


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


print("\n===== 코디 추천 테스트 =====")
results = recommend_outfits(
    user=test_user,
    clothes=clothes,
    temp=22,
    top_n=3
)

print("추천 결과 개수:", len(results))

if not results:
    print("추천 결과가 없습니다. 최소한 상의와 하의를 등록해야 합니다.")
else:
    for index, result in enumerate(results, start=1):
        outfit = result["outfit"]

        print(f"\n--- 추천 코디 {index} ---")
        print("점수:", result["score"])
        print("상의:", format_item(outfit.get("top")))
        print("하의:", format_item(outfit.get("bottom")))
        print("아우터:", format_item(outfit.get("outer")))
        print("신발:", format_item(outfit.get("shoe")))

        print("추천 이유:")
        for reason in result["summary"]:
            print("-", reason)

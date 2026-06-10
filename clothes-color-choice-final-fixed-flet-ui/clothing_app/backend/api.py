def recommend_by_cloth_backend(category, color_name, detail):
    data = {
        "category": category,
        "color_name": color_name,
        "detail": detail
    }

    response = requests.post(
        f"{BASE_URL}/recommend-by-cloth",
        json=data
    )

    return response.json()
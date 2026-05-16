class Clothing:
    def __init__(
        self,
        category,
        detail,
        feature,
        rgb,
        hex_code,
        color_name,
        image_path="",
        colors=None
    ):
        self.category = category
        self.detail = detail
        self.feature = feature
        self.rgb = rgb
        self.hex = hex_code
        self.color_name = color_name
        self.image_path = image_path

        # 사진에서 스포이드로 여러 색을 뽑았을 때 저장
        # 예: [{"rgb": (255, 255, 255), "hex": "#ffffff", "name": "흰색"}]
        self.colors = colors if colors is not None else [
            {
                "rgb": rgb,
                "hex": hex_code,
                "name": color_name
            }
        ]
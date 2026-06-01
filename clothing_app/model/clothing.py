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
        colors=None,
    ):
        self.category = category
        self.detail = detail
        self.feature = feature
        self.rgb = rgb
        self.hex = hex_code
        self.color_name = color_name
        self.image_path = image_path

        self.colors = colors if colors is not None else [
            {"rgb": rgb, "hex": hex_code, "name": color_name}
        ]


class Outfit:
    """코디 (상의 + 하의 + 아우터 조합)"""
    def __init__(self, top=None, bottom=None, outer=None, note=""):
        self.top = top
        self.bottom = bottom
        self.outer = outer
        self.note = note

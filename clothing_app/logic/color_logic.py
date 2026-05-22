def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def rgb_to_name(r, g, b):
    brightness = (r + g + b) / 3

    if max(r, g, b) - min(r, g, b) < 18:
        if brightness < 50:
            return "검정"
        elif brightness < 110:
            return "회색"
        elif brightness < 210:
            return "연회색"
        else:
            return "흰색"

    if r > 200 and g > 200 and b < 150:
        return "노랑"
    if r > 180 and g > 120 and b < 110:
        return "베이지"
    if r > 120 and g > 90 and b < 80:
        return "브라운"
    if r > 150 and g < 100 and b < 100:
        return "빨강"
    if r > 200 and g < 150 and b > 150:
        return "핑크"
    if r < 110 and g > 120 and b < 110:
        return "카키"
    if r < 100 and g < 120 and b > 120:
        return "네이비"
    if b > 150 and g > 140 and r < 180:
        return "하늘색"
    if b > r and b > g:
        return "파랑"
    if g > r and g > b:
        return "초록"

    return "기타"
"""Lightweight clothing-photo analysis without an external AI model."""
from __future__ import annotations

import re
from collections import deque
from pathlib import Path

from PIL import Image


DETAIL_ALIASES = [
    ("하의", "청바지", ["청바지", "데님바지", "jeans", "denim"]),
    ("상의", "반팔", ["반팔", "티셔츠", "반소매", "tshirt", "t-shirt", "tee"]),
    ("상의", "긴팔", ["긴팔", "긴소매", "longsleeve", "long-sleeve"]),
    ("상의", "셔츠", ["셔츠", "남방", "shirt"]),
    ("상의", "니트", ["니트", "스웨터", "knit", "sweater"]),
    ("상의", "맨투맨", ["맨투맨", "스웨트셔츠", "sweatshirt"]),
    ("상의", "후드티", ["후드티", "후디", "hoodie"]),
    ("상의", "블라우스", ["블라우스", "blouse"]),
    ("상의", "민소매", ["민소매", "나시", "tanktop", "sleeveless"]),
    ("하의", "슬랙스", ["슬랙스", "slacks", "trousers"]),
    ("하의", "반바지", ["반바지", "쇼츠", "shorts"]),
    ("하의", "조거팬츠", ["조거", "jogger"]),
    ("하의", "면바지", ["면바지", "치노", "chino"]),
    ("하의", "치마", ["치마", "스커트", "skirt"]),
    ("아우터", "패딩", ["패딩", "다운", "puffer", "padding"]),
    ("아우터", "후리스", ["후리스", "플리스", "fleece"]),
    ("아우터", "코트", ["코트", "coat"]),
    ("아우터", "가디건", ["가디건", "cardigan"]),
    ("아우터", "자켓", ["자켓", "재킷", "jacket", "blazer"]),
    ("아우터", "점퍼", ["점퍼", "jumper"]),
    ("아우터", "집업", ["집업", "zipup", "zip-up"]),
    ("신발", "운동화", ["운동화", "러닝화", "running"]),
    ("신발", "스니커즈", ["스니커즈", "sneakers", "shoes", "shoe"]),
    ("신발", "구두", ["구두", "dressshoes"]),
    ("신발", "로퍼", ["로퍼", "loafer"]),
    ("신발", "부츠", ["부츠", "boots", "boot"]),
    ("신발", "샌들", ["샌들", "sandals", "sandal"]),
    ("신발", "슬리퍼", ["슬리퍼", "slippers", "slipper"]),
    ("악세서리", "가방", ["가방", "백팩", "핸드백", "숄더백", "bag", "backpack"]),
    ("악세서리", "모자", ["모자", "캡", "hat", "cap"]),
    ("악세서리", "시계", ["시계", "watch"]),
    ("악세서리", "목걸이", ["목걸이", "necklace"]),
    ("악세서리", "팔찌", ["팔찌", "bracelet"]),
    ("악세서리", "반지", ["반지", "ring"]),
    ("악세서리", "벨트", ["벨트", "belt"]),
    ("악세서리", "머플러", ["머플러", "스카프", "scarf"]),
    ("악세서리", "선글라스", ["선글라스", "sunglasses"]),
    ("악세서리", "양말", ["양말", "socks", "sock"]),
]


def _normalized_filename(image_path: str) -> str:
    stem = Path(image_path).stem.lower()
    return re.sub(r"[\s_.()\[\]-]+", "", stem)


def foreground_pixels(image_path: str, max_size: int = 300):
    """Return an RGB image and a conservative edge-connected foreground mask."""
    image = Image.open(image_path).convert("RGBA")
    image.thumbnail((max_size, max_size))
    w, h = image.size
    pixels = image.load()

    border = []
    for x in range(w):
        border.extend([pixels[x, 0][:3], pixels[x, h - 1][:3]])
    for y in range(h):
        border.extend([pixels[0, y][:3], pixels[w - 1, y][:3]])
    bg = tuple(sorted(p[i] for p in border)[len(border) // 2] for i in range(3))

    def close_to_bg(x, y):
        rgba = pixels[x, y]
        if rgba[3] < 32:
            return True
        return sum((rgba[i] - bg[i]) ** 2 for i in range(3)) ** 0.5 < 42

    background = set()
    queue = deque()
    for x in range(w):
        queue.extend([(x, 0), (x, h - 1)])
    for y in range(h):
        queue.extend([(0, y), (w - 1, y)])

    while queue:
        x, y = queue.popleft()
        if (x, y) in background or not close_to_bg(x, y):
            continue
        background.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in background:
                queue.append((nx, ny))

    mask = [[(x, y) not in background and pixels[x, y][3] >= 32 for x in range(w)] for y in range(h)]
    rgb = image.convert("RGB")
    return rgb, mask


def _silhouette_guess(image_path: str):
    try:
        image, mask = foreground_pixels(image_path, max_size=220)
    except Exception:
        return None

    w, h = image.size
    points = [(x, y) for y in range(h) for x in range(w) if mask[y][x]]
    if len(points) < max(30, int(w * h * 0.01)):
        return None

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
    bw, bh = max(1, right - left + 1), max(1, bottom - top + 1)
    aspect = bw / bh

    lower_y = top + int(bh * 0.62)
    center_l = left + int(bw * 0.40)
    center_r = left + int(bw * 0.60)
    lower_center = sum(
        mask[y][x] for y in range(lower_y, bottom + 1) for x in range(center_l, center_r + 1)
    ) / max(1, (bottom - lower_y + 1) * (center_r - center_l + 1))

    if aspect >= 1.65:
        return {"category": "신발", "detail": "운동화", "confidence": 0.35, "reason": "가로로 긴 실루엣"}
    if aspect <= 0.68 or (aspect <= 0.78 and lower_center < 0.35):
        return {"category": "하의", "detail": "청바지", "confidence": 0.45, "reason": "아래가 갈라진 바지형 실루엣"}
    if 0.82 <= aspect <= 1.28 and bw < w * 0.75 and bh < h * 0.75:
        return {"category": "악세서리", "detail": "가방", "confidence": 0.25, "reason": "중앙의 작은 사각형 실루엣"}
    return {"category": "상의", "detail": "반팔", "confidence": 0.2, "reason": "상의에 가까운 실루엣"}


def infer_clothing_type(image_path: str):
    """Infer category/detail, prioritizing descriptive Korean or English filenames."""
    name = _normalized_filename(image_path)
    for category, detail, aliases in DETAIL_ALIASES:
        if any(re.sub(r"[\s_-]+", "", alias.lower()) in name for alias in aliases):
            return {
                "category": category,
                "detail": detail,
                "confidence": 0.95,
                "reason": f"파일명에서 '{detail}' 인식",
            }
    return _silhouette_guess(image_path)

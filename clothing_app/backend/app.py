from fastapi import FastAPI
import json

from backend.database import init_db, get_connection
from backend.schemas import ClothingCreate, OutfitEvaluateRequest
from backend.outfit_logic import evaluate_outfit, make_search_keyword
from pydantic import BaseModel
from logic.recommend_logic import get_color_style_info
from pydantic import BaseModel
from backend.outfit_logic import recommend_by_cloth

app = FastAPI()

init_db()


@app.get("/")
def home():
    return {"message": "Clothing recommendation backend is running"}


@app.get("/clothes")
def get_clothes():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, category, detail, feature, color_name, color_hex, image_path
        FROM clothes
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "category": row[1],
            "detail": row[2],
            "feature": row[3],
            "color_name": row[4],
            "color_hex": row[5],
            "image_path": row[6],
        }
        for row in rows
    ]


@app.post("/clothes")
def add_clothing(clothing: ClothingCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clothes
        (category, detail, feature, color_name, color_hex, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        clothing.category,
        clothing.detail,
        clothing.feature,
        clothing.color_name,
        clothing.color_hex,
        clothing.image_path
    ))

    conn.commit()
    conn.close()

    return {"message": "옷이 등록되었습니다."}


@app.post("/evaluate-outfit")
def evaluate(data: OutfitEvaluateRequest):
    result = evaluate_outfit(data)

    keyword = make_search_keyword(
        data.top_color,
        data.top_type,
        data.bottom_color,
        data.bottom_type
    )

    result["search_keyword"] = keyword

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO recommend_history
        (input_data, result_data, score, reason)
        VALUES (?, ?, ?, ?)
    """, (
        json.dumps(data.dict(), ensure_ascii=False),
        json.dumps(result, ensure_ascii=False),
        result["total_score"],
        result["reason"]
    ))

    conn.commit()
    conn.close()

    return result


@app.get("/history")
def get_history():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, input_data, result_data, score, reason, created_at
        FROM recommend_history
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "input_data": json.loads(row[1]),
            "result_data": json.loads(row[2]),
            "score": row[3],
            "reason": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]


@app.post("/favorite/{history_id}")
def add_favorite(history_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO favorites (history_id)
        VALUES (?)
    """, (history_id,))

    conn.commit()
    conn.close()

    return {"message": "즐겨찾기에 저장되었습니다."}


@app.get("/favorites")
def get_favorites():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT favorites.id, recommend_history.input_data, recommend_history.result_data,
               recommend_history.score, recommend_history.reason, favorites.created_at
        FROM favorites
        JOIN recommend_history ON favorites.history_id = recommend_history.id
        ORDER BY favorites.id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "favorite_id": row[0],
            "input_data": json.loads(row[1]),
            "result_data": json.loads(row[2]),
            "score": row[3],
            "reason": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]

class PhotoRecommendRequest(BaseModel):
    color_name: str
    category: str
    target_category: str


@app.post("/recommend-from-photo")
def recommend_from_photo(data: PhotoRecommendRequest):
    info = get_color_style_info(data.color_name)

    return {
        "base_color": data.color_name,
        "base_category": data.category,
        "target_category": data.target_category,
        "recommended_colors": info["recommended"],
        "avoid_colors": info["avoid"],
        "reason": info["reason"],
        "avoid_reason": info["avoid_reason"]
    }

class ClothRecommendRequest(BaseModel):
    category: str
    color_name: str
    detail: str


@app.post("/recommend-by-cloth")
def recommend_cloth(data: ClothRecommendRequest):
    return recommend_by_cloth(
        data.category,
        data.color_name,
        data.detail
    )
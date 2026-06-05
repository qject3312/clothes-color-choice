from fastapi import FastAPI, HTTPException, Query
import hashlib
import json

from backend.database import init_db, get_connection
from backend.schemas import ClothingCreate, OutfitEvaluateRequest, UserCreate, UserLogin
from backend.outfit_logic import evaluate_outfit, make_search_keyword, recommend_by_cloth
from logic.recommend_logic import get_color_style_info
from pydantic import BaseModel

app = FastAPI()
init_db()


def _hash_password(password: str) -> str:
    return "sha256$" + hashlib.sha256((password or "").encode("utf-8")).hexdigest()

def _verify_password(saved_password: str, input_password: str) -> bool:
    if saved_password.startswith("sha256$"):
        return saved_password == _hash_password(input_password)
    # 기존 평문 저장 계정과의 호환성
    return saved_password == input_password


def _user_row_to_dict(row):
    data = dict(row)
    try:
        data["styles"] = json.loads(data.get("styles") or '["미선택"]')
    except Exception:
        data["styles"] = ["미선택"]
    return data


@app.get("/")
def home():
    return {"message": "Clothing recommendation backend is running"}


@app.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user.user_id,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="이미 존재하는 아이디입니다.")

    cur.execute(
        """
        INSERT INTO users
        (user_id, password, name, gender, height, weight, body_type, skin_tone, personal_color, styles)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user.user_id,
            _hash_password(user.password),
            user.name,
            user.gender,
            user.height,
            user.weight,
            user.body_type,
            user.skin_tone,
            user.personal_color,
            json.dumps(user.styles or ["미선택"], ensure_ascii=False),
        ),
    )

    conn.commit()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user.user_id,))
    row = cur.fetchone()
    conn.close()
    return _user_row_to_dict(row)


@app.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user.user_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 아이디입니다.")

    row_data = _user_row_to_dict(row)
    if not _verify_password(row_data["password"], user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    # 기존 평문 비밀번호 계정은 로그인 성공 시 자동으로 해시 저장으로 전환
    if not str(row_data["password"]).startswith("sha256$"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE user_id = ?", (_hash_password(user.password), user.user_id))
        conn.commit()
        conn.close()
        row_data["password"] = _hash_password(user.password)

    return row_data


@app.put("/users/{user_id}")
def update_user(user_id: str, user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="존재하지 않는 아이디입니다.")

    cur.execute(
        """
        UPDATE users
        SET password = ?, name = ?, gender = ?, height = ?, weight = ?,
            body_type = ?, skin_tone = ?, personal_color = ?, styles = ?
        WHERE user_id = ?
        """,
        (
            _hash_password(user.password),
            user.name,
            user.gender,
            user.height,
            user.weight,
            user.body_type,
            user.skin_tone,
            user.personal_color,
            json.dumps(user.styles or ["미선택"], ensure_ascii=False),
            user_id,
        ),
    )
    conn.commit()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return _user_row_to_dict(row)


@app.get("/clothes")
def get_clothes(user_id: str = Query("guest")):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, user_id, category, detail, feature, color_name, color_hex, image_path
        FROM clothes
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "category": row["category"],
            "detail": row["detail"],
            "feature": row["feature"],
            "color_name": row["color_name"],
            "color_hex": row["color_hex"],
            "image_path": row["image_path"],
        }
        for row in rows
    ]


@app.post("/clothes")
def add_clothing(clothing: ClothingCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO clothes
        (user_id, category, detail, feature, color_name, color_hex, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            clothing.user_id,
            clothing.category,
            clothing.detail,
            clothing.feature,
            clothing.color_name,
            clothing.color_hex,
            clothing.image_path,
        ),
    )

    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"message": "옷이 등록되었습니다.", "id": new_id}


@app.delete("/clothes/{clothing_id}")
def delete_clothing(clothing_id: int, user_id: str = Query("guest")):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clothes WHERE id = ? AND user_id = ?", (clothing_id, user_id))
    deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="삭제할 옷을 찾을 수 없습니다.")

    return {"message": "삭제되었습니다."}


@app.post("/evaluate-outfit")
def evaluate(data: OutfitEvaluateRequest):
    result = evaluate_outfit(data)

    keyword = make_search_keyword(data.top_color, data.top_type, data.bottom_color, data.bottom_type)
    result["search_keyword"] = keyword

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO recommend_history
        (user_id, input_data, result_data, score, reason)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.user_id or "guest",
            json.dumps(data.dict(), ensure_ascii=False),
            json.dumps(result, ensure_ascii=False),
            result["total_score"],
            result["reason"],
        ),
    )

    conn.commit()
    conn.close()
    return result


@app.get("/history")
def get_history(user_id: str = Query("guest")):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, input_data, result_data, score, reason, created_at
        FROM recommend_history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "input_data": json.loads(row["input_data"]),
            "result_data": json.loads(row["result_data"]),
            "score": row["score"],
            "reason": row["reason"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@app.post("/favorite/{history_id}")
def add_favorite(history_id: int, user_id: str = Query("guest")):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO favorites (user_id, history_id) VALUES (?, ?)", (user_id, history_id))
    conn.commit()
    conn.close()
    return {"message": "즐겨찾기에 저장되었습니다."}


@app.get("/favorites")
def get_favorites(user_id: str = Query("guest")):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT favorites.id, recommend_history.input_data, recommend_history.result_data,
               recommend_history.score, recommend_history.reason, favorites.created_at
        FROM favorites
        JOIN recommend_history ON favorites.history_id = recommend_history.id
        WHERE favorites.user_id = ?
        ORDER BY favorites.id DESC
        """,
        (user_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "favorite_id": row["id"],
            "input_data": json.loads(row["input_data"]),
            "result_data": json.loads(row["result_data"]),
            "score": row["score"],
            "reason": row["reason"],
            "created_at": row["created_at"],
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
        "avoid_reason": info["avoid_reason"],
    }


class ClothRecommendRequest(BaseModel):
    category: str
    color_name: str
    detail: str


@app.post("/recommend-by-cloth")
def recommend_cloth(data: ClothRecommendRequest):
    return recommend_by_cloth(data.category, data.color_name, data.detail)

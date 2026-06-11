from django.http import JsonResponse
from django.shortcuts import render

from app_paths import DB_PATH
from backend.database import get_connection, init_db


TABLE_LABELS = {
    "users": "Users",
    "clothes": "Clothes",
    "recommend_history": "Recommendations",
    "favorites": "Favorites",
    "saved_outfits": "Saved outfits",
}


def _dashboard_data() -> tuple[dict[str, int], list[dict]]:
    init_db()
    connection = get_connection()
    try:
        counts = {
            label: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table, label in TABLE_LABELS.items()
        }
        recent_clothes = [
            dict(row)
            for row in connection.execute(
                """
                SELECT id, user_id, category, detail, color_name, color_hex, created_at
                FROM clothes
                ORDER BY id DESC
                LIMIT 8
                """
            ).fetchall()
        ]
        return counts, recent_clothes
    finally:
        connection.close()


def dashboard(request):
    counts, recent_clothes = _dashboard_data()
    return render(
        request,
        "django_dashboard/dashboard.html",
        {
            "counts": counts,
            "recent_clothes": recent_clothes,
            "db_path": DB_PATH,
            "fastapi_docs_url": "http://localhost:8000/docs",
        },
    )


def health(request):
    counts, _ = _dashboard_data()
    return JsonResponse(
        {
            "status": "ok",
            "service": "fitpick-django-dashboard",
            "database": str(DB_PATH),
            "counts": counts,
        }
    )

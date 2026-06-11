import sqlite3
from app_paths import DB_PATH, ensure_app_dirs

ensure_app_dirs()
DB_NAME = str(DB_PATH)


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _add_column_if_missing(cur, table_name, column_name, column_sql):
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    if column_name not in columns:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            gender TEXT DEFAULT '미입력',
            height TEXT DEFAULT '미입력',
            weight TEXT DEFAULT '미입력',
            body_type TEXT DEFAULT '미입력',
            skin_tone TEXT DEFAULT '미입력',
            personal_color TEXT DEFAULT '미입력',
            styles TEXT DEFAULT '["미선택"]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            category TEXT,
            detail TEXT,
            feature TEXT,
            color_name TEXT,
            color_hex TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _add_column_if_missing(cur, "clothes", "user_id", "user_id TEXT DEFAULT 'guest'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recommend_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            input_data TEXT,
            result_data TEXT,
            score INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _add_column_if_missing(cur, "recommend_history", "user_id", "user_id TEXT DEFAULT 'guest'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            history_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _add_column_if_missing(cur, "favorites", "user_id", "user_id TEXT DEFAULT 'guest'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'guest',
            outfit_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _add_column_if_missing(cur, "saved_outfits", "user_id", "user_id TEXT DEFAULT 'guest'")

    conn.commit()
    conn.close()

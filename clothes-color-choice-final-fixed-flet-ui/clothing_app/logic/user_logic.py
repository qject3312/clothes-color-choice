import json
import os
import hashlib
import uuid

from model.user import User


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
    ensure_data_dir()

    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [User.from_dict(item) for item in data]

    except Exception as error:
        print("사용자 데이터를 불러오는 중 오류 발생:", error)
        return []


def save_users(users):
    ensure_data_dir()

    data = [user.to_dict() for user in users]

    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def register_user(username, password, nickname, style="캐주얼"):
    if not username or not password or not nickname:
        return {
            "success": False,
            "message": "아이디, 비밀번호, 닉네임을 모두 입력해야 합니다.",
            "user": None
        }

    users = load_users()

    for user in users:
        if user.username == username:
            return {
                "success": False,
                "message": "이미 존재하는 아이디입니다.",
                "user": None
            }

    new_user = User(
        user_id=str(uuid.uuid4()),
        username=username,
        password_hash=hash_password(password),
        nickname=nickname,
        style=style
    )

    users.append(new_user)
    save_users(users)

    return {
        "success": True,
        "message": "회원가입 성공",
        "user": new_user
    }


def login_user(username, password):
    users = load_users()
    password_hash = hash_password(password)

    for user in users:
        if user.username == username and user.password_hash == password_hash:
            return {
                "success": True,
                "message": "로그인 성공",
                "user": user
            }

    return {
        "success": False,
        "message": "아이디 또는 비밀번호가 올바르지 않습니다.",
        "user": None
    }


def get_user_info(user_id):
    users = load_users()

    for user in users:
        if user.user_id == user_id:
            return {
                "success": True,
                "message": "사용자 정보 조회 성공",
                "user": user
            }

    return {
        "success": False,
        "message": "사용자를 찾을 수 없습니다.",
        "user": None
    }


def update_user_info(user_id, nickname=None, style=None):
    users = load_users()

    for user in users:
        if user.user_id == user_id:
            if nickname is not None:
                user.nickname = nickname

            if style is not None:
                user.style = style

            save_users(users)

            return {
                "success": True,
                "message": "사용자 정보 수정 완료",
                "user": user
            }

    return {
        "success": False,
        "message": "사용자를 찾을 수 없습니다.",
        "user": None
    }
class User:
    def __init__(self, user_id, username, password_hash, nickname, style="캐주얼"):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.nickname = nickname
        self.style = style

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "nickname": self.nickname,
            "style": self.style
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data["user_id"],
            username=data["username"],
            password_hash=data["password_hash"],
            nickname=data["nickname"],
            style=data.get("style", "캐주얼")
        )
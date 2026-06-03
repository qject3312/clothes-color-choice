from logic.user_logic import register_user, login_user, get_user_info, update_user_info


print("===== 회원가입 테스트 =====")
register_result = register_user(
    username="testuser",
    password="1234",
    nickname="테스트유저",
    style="캐주얼"
)

print("회원가입 성공 여부:", register_result["success"])
print("메시지:", register_result["message"])


print("\n===== 중복 회원가입 테스트 =====")
duplicate_result = register_user(
    username="testuser",
    password="1234",
    nickname="중복유저",
    style="미니멀"
)

print("중복 회원가입 성공 여부:", duplicate_result["success"])
print("메시지:", duplicate_result["message"])


print("\n===== 로그인 테스트 =====")
login_result = login_user(
    username="testuser",
    password="1234"
)

print("로그인 성공 여부:", login_result["success"])
print("메시지:", login_result["message"])

if login_result["success"]:
    user = login_result["user"]

    print("\n===== 사용자 정보 조회 테스트 =====")
    info_result = get_user_info(user.user_id)

    print("조회 성공 여부:", info_result["success"])
    print("메시지:", info_result["message"])
    print("아이디:", info_result["user"].username)
    print("닉네임:", info_result["user"].nickname)
    print("스타일:", info_result["user"].style)

    print("\n===== 사용자 정보 수정 테스트 =====")
    update_result = update_user_info(
        user_id=user.user_id,
        nickname="수정된유저",
        style="스트릿"
    )

    print("수정 성공 여부:", update_result["success"])
    print("메시지:", update_result["message"])
    print("수정된 닉네임:", update_result["user"].nickname)
    print("수정된 스타일:", update_result["user"].style)


print("\n===== 잘못된 비밀번호 로그인 테스트 =====")
wrong_login_result = login_user(
    username="testuser",
    password="wrongpassword"
)

print("로그인 성공 여부:", wrong_login_result["success"])
print("메시지:", wrong_login_result["message"])
from models.user_model import find_by_username


def login(username: str, password: str) -> dict:
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return {
            "success": False,
            "message": "Vui lòng nhập đầy đủ tài khoản và mật khẩu.",
            "user": None,
        }

    user = find_by_username(username)

    if not user or user.password != password:
        return {
            "success": False,
            "message": "Sai tên đăng nhập hoặc mật khẩu.",
            "user": None,
        }

    return {
        "success": True,
        "message": f"Xin chào {user.full_name or user.username}!",
        "user": user,
    }
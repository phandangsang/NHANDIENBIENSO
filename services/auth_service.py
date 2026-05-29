from models.user_model import find_by_username


def login(username: str, password: str) -> dict:
    username = (username or "").strip()
    password = (password or "").strip()

    if not username or not password:
        return {"success": False, "message": "Vui long nhap day du tai khoan va mat khau.", "user": None}

    user = find_by_username(username)
    if not user or user.get("password") != password:
        return {"success": False, "message": "Sai ten dang nhap hoac mat khau.", "user": None}

    return {
        "success": True,
        "message": f"Xin chao {user.get('full_name') or user.get('username')}!",
        "user": user,
    }

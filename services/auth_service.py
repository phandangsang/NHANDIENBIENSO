from models.user_model import find_by_username


def login(username: str, password: str):
    user = find_by_username(username)

    if not user or user.get("password") != password:
        return None

    return user

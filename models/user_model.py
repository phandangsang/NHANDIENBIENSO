def find_by_username(username: str):
    from database.db import fetch_one

    user_data = fetch_one(
        "SELECT * FROM `user` WHERE `username` = %s",
        (username,),
    )

    if not user_data:
        return None

    return User(
        id=user_data["id"],
        username=user_data["username"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        notif=user_data["notif"],
        created_at=user_data["created_at"],
        password=user_data.get("password")   # 👈 thêm dòng này
    )
    
class User:
    def __init__(
        self,
        id: int,
        username: str,
        full_name: str,
        role: str,
        notif: int,
        created_at: datetime,
        password: str = None
    ):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.notif = notif
        self.created_at = created_at
        self.password = password
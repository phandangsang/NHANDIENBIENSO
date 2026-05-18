def find_by_username(username: str):
    from database.db import fetch_one

    return fetch_one(
        "SELECT * FROM `user` WHERE `username` = %s",
        (username,),
    )

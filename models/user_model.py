from database.db import fetch_one


def find_by_username(username: str):
    # Return a dict row (mysql-connector dictionary cursor) for simplicity across UI/services.
    return fetch_one(
        "SELECT * FROM `user` WHERE `username` = %s",
        (username,),
    )

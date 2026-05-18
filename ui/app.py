from database.db import init_database


def run_app() -> None:
    init_database()
    print("Ung dung nhan dien bien so xe da san sang.")
    print("Giao dien se duoc xay dung trong cac file ui/*_window.py.")

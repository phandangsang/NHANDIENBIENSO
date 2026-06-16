import sys

from PyQt5.QtWidgets import QApplication

from database.db import init_database
from ui.dashboard_window import DashboardWindow
from ui.login_window import LoginWindow


def load_qss(app: QApplication) -> None:
    try:
        with open("ui/style/loginstyle.css", "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Khong tim thay file ui/style/loginstyle.css")


if __name__ == "__main__":
    init_database()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    load_qss(app)

    login_window = LoginWindow()
    app.dashboard_window = None

    def open_dashboard(user: dict) -> None:
        app.dashboard_window = DashboardWindow(user)
        app.dashboard_window.logout_requested.connect(logout)
        app.dashboard_window.show()
        login_window.hide()

    def logout() -> None:
        login_window.reset_form()
        login_window.show()

        if app.dashboard_window is not None:
            dashboard_window = app.dashboard_window
            app.dashboard_window = None
            dashboard_window.close()

    login_window.login_success.connect(open_dashboard)
    login_window.show()

    sys.exit(app.exec_())

import sys

from PyQt5.QtWidgets import QApplication

from ui.dashboard_window import DashboardWindow
from ui.login_window import LoginWindow


def load_qss(app: QApplication) -> None:
    try:
        with open("ui/style/loginstyle.css", "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Khong tim thay file ui/style/loginstyle.css")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    load_qss(app)

    login_window = LoginWindow()
    app.dashboard_window = None

    def open_dashboard(user: dict) -> None:
        app.dashboard_window = DashboardWindow(user)
        app.dashboard_window.logout_requested.connect(return_to_login)
        app.dashboard_window.show()
        login_window.hide()

    def return_to_login() -> None:
        if app.dashboard_window is not None:
            app.dashboard_window.close()
            app.dashboard_window = None
        login_window.reset_form()
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()

    login_window.login_success.connect(open_dashboard)
    login_window.show()

    sys.exit(app.exec_())

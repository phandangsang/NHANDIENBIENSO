import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow


def load_qss(app):
    try:
        with open("ui/style/loginstyle.css", "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Không tìm thấy file ui/style/loginstyle.css")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    load_qss(app)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())
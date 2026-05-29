from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from services.auth_service import login


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dang nhap he thong bai do xe")
        self.setFixedSize(420, 360)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()

        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("PARKING SYSTEM")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Nhan dien bien so xe ra vao bai do")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)

        self.username_input.setPlaceholderText("Ten dang nhap")

        self.password_input.setPlaceholderText("Mat khau")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Dang nhap")
        login_button.clicked.connect(self.handle_login)

        exit_button = QPushButton("Thoat")
        exit_button.setObjectName("exitButton")
        exit_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(login_button)
        buttons.addWidget(exit_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(18)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def handle_login(self) -> None:
        result = login(
            self.username_input.text(),
            self.password_input.text(),
        )

        if not result["success"]:
            QMessageBox.warning(self, "Dang nhap that bai", result["message"])
            return

        QMessageBox.information(self, "Dang nhap thanh cong", result["message"])
        self.login_success.emit(result["user"])

    def reset_form(self) -> None:
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

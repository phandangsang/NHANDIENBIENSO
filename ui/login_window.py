import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from config import MYSQL_DATABASE
from database.db import get_connection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập hệ thống bãi đỗ xe")
        self.setFixedSize(420, 360)
        self.init_ui()

    def init_ui(self):
        title = QLabel("PARKING SYSTEM")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Nhận diện biển số xe ra vào bãi đỗ")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Đăng nhập")
        self.login_button.clicked.connect(self.handle_login)

        self.exit_button = QPushButton("Thoát")
        self.exit_button.setObjectName("exitButton")
        self.exit_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.exit_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(18)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tài khoản và mật khẩu.")
            return

        try:
            conn = get_connection(MYSQL_DATABASE)
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT id, username, full_name, role
                FROM `user`
                WHERE username = %s AND password = %s
            """
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                QMessageBox.information(
                    self,
                    "Đăng nhập thành công",
                    f"Xin chào {user['full_name']}!"
                )

                # Sau này mở MainWindow ở đây
                # self.main_window = MainWindow(user)
                # self.main_window.show()
                # self.close()

            else:
                QMessageBox.warning(
                    self,
                    "Đăng nhập thất bại",
                    "Sai tên đăng nhập hoặc mật khẩu."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi kết nối",
                f"Không thể kết nối database:\n{e}"
            )

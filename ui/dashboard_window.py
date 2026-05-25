from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class DashboardWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle("Dashboard")
        self.resize(960, 640)
        self._build_ui()

    def _build_ui(self) -> None:
        full_name = self.user.get("full_name") or self.user.get("username") or "User"
        role = self.user.get("role") or "staff"

        layout = QVBoxLayout()

        title = QLabel("DASHBOARD")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitle = QLabel(f"Xin chao {full_name} - vai tro: {role}")

        logout_button = QPushButton("Dang xuat")
        logout_button.clicked.connect(self._handle_logout)

        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        header.addSpacing(12)
        header.addWidget(logout_button)

        layout.addLayout(header)
        layout.addStretch()

        self.setLayout(layout)

    def _handle_logout(self) -> None:
        self.logout_requested.emit()

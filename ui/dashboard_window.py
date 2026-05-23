from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardWindow(QWidget):
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
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitle = QLabel(f"Xin chao {full_name} - vai tro: {role}")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setLayout(layout)

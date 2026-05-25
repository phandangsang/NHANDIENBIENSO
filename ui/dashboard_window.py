from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton,
    QStackedWidget
)

from .sidebar import Sidebar


class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()

        self.user = user

        self.setWindowTitle("LPR Dashboard")
        self.resize(1400, 900)

        self._build_ui()

    def _build_ui(self):
        # ===== Central widget =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # ===== Sidebar =====
        self.sidebar = Sidebar()

        # ===== Stack pages =====
        self.stack = QStackedWidget()

        # Page 0 - Dashboard
        dashboard_page = self._create_dashboard_page()

        # Page 1 - Entry
        entry_page = self._create_simple_page("ENTRY WINDOW")

        # Page 2 - Exit
        exit_page = self._create_simple_page("EXIT WINDOW")

        # Page 3 - History
        history_page = self._create_simple_page("HISTORY WINDOW")

        self.stack.addWidget(dashboard_page)
        self.stack.addWidget(entry_page)
        self.stack.addWidget(exit_page)
        self.stack.addWidget(history_page)

        # ===== connect sidebar =====
        self.sidebar.pageChanged.connect(self.change_page)

        # ===== layout =====
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.stack, 4)

    def _create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        full_name = self.user.get("full_name") or self.user.get("username") or "User"
        role = self.user.get("role") or "staff"

        title = QLabel("DASHBOARD")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        info = QLabel(f"Xin chào {full_name} - Vai trò: {role}")

        logout_btn = QPushButton("Đăng xuất")
        logout_btn.clicked.connect(self.logout_requested.emit)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(logout_btn)
        layout.addStretch()

        return page

    def _create_simple_page(self, name: str):
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel(name)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(label)
        layout.addStretch()

        return page

    def change_page(self, index: int):
        self.stack.setCurrentIndex(index)
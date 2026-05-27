from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton,
    QStackedWidget
)

from .sidebar import Sidebar
from .user_window import UserPage


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

        # Page 2 - History
        history_page = self._create_simple_page("HISTORY WINDOW")

        # Page 3 - User 
        self.user_page = UserPage()

        # Page 4 - Exit
        exit_page = self._create_simple_page("EXIT WINDOW") 




        self.stack.addWidget(dashboard_page)
        self.stack.addWidget(entry_page)
        self.stack.addWidget(self.user_page)
        self.stack.addWidget(history_page)
        self.stack.addWidget(exit_page)
        
        # ===== connect sidebar =====
        self.sidebar.pageChanged.connect(self.change_page)

        # ===== layout =====
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.stack, 4)

    def _create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        user = self.user

        full_name = getattr(user, "full_name", None) or getattr(user, "username", "User")
        role = getattr(user, "role", "staff")

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
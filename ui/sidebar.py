from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    pageChanged = pyqtSignal(int)
    logoutRequested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.nav_buttons = []

        css_path = Path(__file__).resolve().parent / "style" / "sidebar.css"
        try:
            self.setStyleSheet(css_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"Khong tim thay file CSS: {css_path}")

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("PARKING")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)
        layout.addSpacing(10)

        btn_dashboard = self._create_nav_button("Bang dieu khien", 0)
        btn_exit_scan = self._create_nav_button("Quet xe ra", 1)
        btn_vehicles = self._create_nav_button("Danh sach xe", 2)
        btn_revenue = self._create_nav_button("Doanh thu", 3)
        btn_users = self._create_nav_button("Nguoi dung", 4)
        btn_logout = QPushButton("Dang xuat")
        btn_logout.setObjectName("logoutButton")

        btn_logout.clicked.connect(self.logoutRequested.emit)

        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_exit_scan)
        layout.addWidget(btn_vehicles)
        layout.addWidget(btn_revenue)
        layout.addWidget(btn_users)
        layout.addStretch()
        layout.addWidget(btn_logout)

        self._set_active_button(btn_dashboard)

    def _create_nav_button(self, text: str, page_index: int) -> QPushButton:
        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda: self._handle_nav_click(button, page_index))
        self.nav_buttons.append(button)
        return button

    def _handle_nav_click(self, button: QPushButton, page_index: int) -> None:
        self._set_active_button(button)
        self.pageChanged.emit(page_index)

    def _set_active_button(self, active_button: QPushButton) -> None:
        for button in self.nav_buttons:
            button.setChecked(button is active_button)

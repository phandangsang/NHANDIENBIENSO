from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    pageChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")

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

        title = QLabel("LPR Admin")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)
        layout.addSpacing(10)

        btn_dashboard = QPushButton("Bang dieu khien")
        btn_vehicles = QPushButton("Danh sach xe")
        btn_users = QPushButton("Nguoi dung")
        btn_history = QPushButton("Lich su")
        btn_settings = QPushButton("Cai dat")

        btn_dashboard.clicked.connect(lambda: self.pageChanged.emit(0))
        btn_vehicles.clicked.connect(lambda: self.pageChanged.emit(1))
        btn_users.clicked.connect(lambda: self.pageChanged.emit(2))
        btn_history.clicked.connect(lambda: self.pageChanged.emit(3))
        btn_settings.clicked.connect(lambda: self.pageChanged.emit(4))

        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_vehicles)
        layout.addWidget(btn_users)
        layout.addWidget(btn_history)
        layout.addWidget(btn_settings)
        layout.addStretch()

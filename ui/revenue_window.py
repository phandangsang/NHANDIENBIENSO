import csv
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.payment_model import get_revenue_summary, list_payment_history
from services.payment_service import format_duration, format_money


class RevenueWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("RevenueWindow")
        self.current_rows = []
        self._load_style()
        self._build_ui()
        self.load_data()

    def _load_style(self):
        css_path = os.path.join(os.path.dirname(__file__), "style", "vehicles.css")
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel("Bao cao doanh thu")
        title.setObjectName("title")
        refresh_btn = QPushButton("Lam moi")
        refresh_btn.setObjectName("exportBtn")
        refresh_btn.clicked.connect(self.load_data)
        export_btn = QPushButton("⬇ Xuat CSV")
        export_btn.setObjectName("exportBtn")
        export_btn.clicked.connect(self.export_csv)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(export_btn)
        title_row.addWidget(refresh_btn)
        root.addLayout(title_row)

        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        summary_layout = QGridLayout(summary_frame)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(12)

        self.revenue_label = self._create_summary_card("Tong doanh thu", "0 VND")

        summary_layout.addWidget(self.revenue_label, 0, 0)
        root.addWidget(summary_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "#", "BIEN SO", "LOAI XE", "THOI GIAN GUI", "SO TIEN", "THU NGAN", "THANH TOAN", "THOI GIAN THU"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        root.addWidget(self.table)

    def _create_summary_card(self, title, value):
        card = QFrame()
        card.setObjectName("summaryCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        title_label = QLabel(title)
        title_label.setObjectName("totalBadge")
        value_label = QLabel(value)
        value_label.setObjectName("title")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.value_label = value_label
        return card

    def load_data(self):
        summary = get_revenue_summary()
        total_revenue = float(summary.get("total_revenue") or 0)

        self.revenue_label.value_label.setText(format_money(total_revenue))

        rows = list_payment_history()
        self.current_rows = rows
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row.get("id") or ""),
                str(row.get("plate_number") or ""),
                self._format_vehicle_type(row.get("vehicle_type")),
                format_duration(int(row.get("duration_minutes") or 0)),
                format_money(float(row.get("amount") or 0)),
                str(row.get("paid_by_name") or "He thong"),
                "Tien mat",
                str(row.get("paid_at") or ""),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 1:
                    item.setForeground(QColor("#003aaf"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                elif col == 4:
                    item.setForeground(QColor("#06623b"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                self.table.setItem(row_index, col, item)

    def export_csv(self):
        if not self.current_rows:
            QMessageBox.information(self, "Xuat CSV", "Khong co du lieu doanh thu de xuat.")
            return

        default_path = os.path.join(os.getcwd(), "bao_cao_doanh_thu.csv")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Luu file CSV",
            default_path,
            "CSV Files (*.csv)",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        headers = [
            "#",
            "BIEN SO",
            "LOAI XE",
            "THOI GIAN GUI",
            "SO TIEN",
            "THU NGAN",
            "THANH TOAN",
            "THOI GIAN THU",
        ]

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)

                for row in self.current_rows:
                    writer.writerow(
                        [
                            row.get("id") or "",
                            row.get("plate_number") or "",
                            self._format_vehicle_type(row.get("vehicle_type")),
                            format_duration(int(row.get("duration_minutes") or 0)),
                            format_money(float(row.get("amount") or 0)),
                            row.get("paid_by_name") or "He thong",
                            "Tien mat",
                            row.get("paid_at") or "",
                        ]
                    )
        except Exception as exc:
            QMessageBox.warning(self, "Xuat CSV that bai", f"Khong the xuat file CSV.\nLoi: {exc}")
            return

        QMessageBox.information(self, "Xuat CSV", f"Da xuat file CSV thanh cong.\n{file_path}")

    def _format_vehicle_type(self, vehicle_type):
        if vehicle_type == "motorbike":
            return "Xe may"
        if vehicle_type == "car":
            return "O to"
        return str(vehicle_type or "")

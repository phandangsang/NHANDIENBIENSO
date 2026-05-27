import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame
)
from PyQt5.QtGui import QColor, QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database.db import fetch_all


class VehiclesWindow(QWidget):

    def __init__(self):
        super().__init__()

       
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #030a1c;")

        self.load_style()
        self.build_ui()
        
        
        self.load_data()

    def load_style(self):
        css_path = os.path.join(
            os.path.dirname(__file__),
            "style",
            "vehicles.css"
        )
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20) 
        root.setSpacing(16)

    
        title_layout = QHBoxLayout()
        
        title = QLabel("Danh sách xe đã quét")
        title.setObjectName("title")

        self.total_label = QLabel("0 lượt")
        self.total_label.setObjectName("totalBadge")

        export_btn = QPushButton("⬇ Xuất CSV")
        export_btn.setObjectName("exportBtn")

        title_layout.addWidget(title)
        title_layout.addSpacing(12)
        title_layout.addWidget(self.total_label)
        title_layout.addStretch()
        title_layout.addWidget(export_btn)

        root.addLayout(title_layout)

      
        chart = QFrame()
        chart.setObjectName("chartBox")
        chart.setFixedHeight(180)  
        
        chart_layout = QVBoxLayout(chart)
        chart_layout.setContentsMargins(20, 12, 20, 12)
        chart_layout.setSpacing(8)

        chart_title = QLabel("SỐ LƯỢNG XE THEO GIỜ")
        chart_title.setObjectName("chartTitle")
        chart_layout.addWidget(chart_title)

        self.figure = Figure(facecolor='#061735')
        self.figure.patch.set_facecolor('#061735') 
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;") 
        chart_layout.addWidget(self.canvas)

        root.addWidget(chart)

       
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm biển số...")
        self.search_input.textChanged.connect(self.load_data)

      
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "Tất cả trạng thái",
            "Thông qua",
            "Cảnh báo",
            "Từ chối"
        ])
        self.status_filter.currentIndexChanged.connect(self.load_data)

        
        self.camera_filter = QComboBox()
        self.camera_filter.addItems(["Tất cả người dùng"])
        self.camera_filter.currentIndexChanged.connect(self.load_data)

        
        filter_layout.addWidget(self.search_input, 5)
        filter_layout.addWidget(self.status_filter, 3)
        filter_layout.addWidget(self.camera_filter, 3)

        root.addLayout(filter_layout)

        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
       
        self.table.setHorizontalHeaderLabels([
            "#", "BIỂN SỐ", "TỈNH/THÀNH", "LOẠI XE", "THỜI GIAN", "NGƯỜI QUÉT", "TRẠNG THÁI", "CONF."
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        root.addWidget(self.table)

    def get_province_by_plate(self, plate_str):
        """Hàm tự động dịch mã vùng biển số xe ra Tỉnh/Thành phố tương ứng"""
        if not plate_str or len(plate_str) < 2:
            return ""
        
        prefix = plate_str[:2]
        
      
        province_map = {
            "11": "Cao Bằng", "12": "Lạng Sơn", "14": "Quảng Ninh",
            "15": "Hải Phòng", "16": "Hải Phòng", "17": "Thái Bình", "18": "Nam Định",
            "19": "Phú Thọ", "20": "Thái Nguyên", "21": "Yên Bái", "22": "Tuyên Quang",
            "23": "Hà Giang", "24": "Lào Cai", "25": "Lai Châu", "26": "Sơn La",
            "27": "Điện Biên", "28": "Hòa Bình",
            "29": "Hà Nội", "30": "Hà Nội", "31": "Hà Nội", "32": "Hà Nội", "33": "Hà Nội", "40": "Hà Nội",
            "34": "Hải Dương", "35": "Ninh Bình", "36": "Thanh Hóa", "37": "Nghệ An",
            "38": "Hà Tĩnh", "43": "Đà Nẵng", "47": "Đắk Lắk", "48": "Đắk Nông",
            "49": "Lâm Đồng", 
            "50": "TP. HCM", "51": "TP. HCM", "52": "TP. HCM", "53": "TP. HCM", "54": "TP. HCM", 
            "55": "TP. HCM", "56": "TP. HCM", "57": "TP. HCM", "58": "TP. HCM", "59": "TP. HCM",
            "41": "TP. HCM",
            "60": "Đồng Nai", "39": "Đồng Nai", "61": "Bình Dương", "62": "Long An",
            "63": "Tiền Giang", "64": "Vĩnh Long", "65": "Cần Thơ", "66": "Đồng Tháp",
            "67": "An Giang", "68": "Kiên Giang", "69": "Cà Mau", "70": "Tây Ninh",
            "71": "Bến Tre", "72": "Bà Rịa - Vũng Tàu", "73": "Quảng Bình", "74": "Quảng Trị",
            "75": "Thừa Thiên Huế", "76": "Quảng Ngãi", "77": "Bình Định", "78": "Phú Yên",
            "79": "Khánh Hòa", "81": "Gia Lai", "82": "Kon Tum", "83": "Sóc Trăng",
            "84": "Trà Vinh", "85": "Ninh Thuận", "86": "Bình Thuận", "88": "Vĩnh Phúc",
            "89": "Hưng Yên", "90": "Hà Nam", "92": "Quảng Nam", "93": "Bình Phước",
            "94": "Bạc Liêu", "95": "Hậu Giang", "97": "Bắc Kạn", "98": "Bắc Giang",
            "99": "Bắc Ninh"
        }
        return province_map.get(prefix, "")

    def load_data(self):
        keyword = self.search_input.text().strip()
        status = self.status_filter.currentText()
        user_filter_text = self.camera_filter.currentText()

        if self.camera_filter.count() == 1:
            try:
                users = fetch_all("SELECT DISTINCT full_name FROM user WHERE full_name IS NOT NULL AND role != 'admin'")
                for u in users:
                    self.camera_filter.addItem(u["full_name"])
            except Exception as e:
                print(f"Lỗi nạp user filter: {e}")

        sql = """
            SELECT
                p.id,
                v.plate_number,
                v.vehicle_type,
                p.entry_time,
                u.full_name,
                p.status,
                img.confidence
            FROM parking_records p
            LEFT JOIN vehicle v ON p.vehicle_id = v.id
            LEFT JOIN user u ON p.user_id = u.id
            LEFT JOIN images img ON img.parking_record_id = p.id
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += " AND (v.plate_number LIKE %s)"
            params.append(f"%{keyword}%")

        if status == "Thông qua": sql += " AND p.status = 'in'"
        elif status == "Cảnh báo": sql += " AND p.status = 'warning'"
        elif status == "Từ chối": sql += " AND p.status = 'deny'"

        if user_filter_text != "Tất cả người dùng":
            sql += " AND u.full_name = %s"
            params.append(user_filter_text)

        sql += " ORDER BY p.id DESC"

        real_hourly_data = {}
        rows = []
        try:
            rows = fetch_all(sql, tuple(params))
        except Exception as e:
            print(f"Lỗi truy vấn database: {e}")

        self.table.setRowCount(len(rows))
        self.total_label.setText(f"{len(rows)} lượt")

        for row_index, row in enumerate(rows):
            plate = str(row["plate_number"]) if row["plate_number"] else ""
            
           
            province = self.get_province_by_plate(plate)
            
            v_type = str(row["vehicle_type"]) if row["vehicle_type"] else ""
            e_time = str(row["entry_time"]) if row["entry_time"] else ""
            operator = str(row["full_name"]) if row["full_name"] else "Hệ thống"
            
            status_raw = str(row["status"]).strip()
            if status_raw == 'in': status_text = "THÔNG QUA"
            elif status_raw == 'warning': status_text = "CẢNH BÁO"
            elif status_raw == 'deny': status_text = "TỪ CHỐI"
            else: status_text = status_raw.upper()

            conf_raw = row.get("confidence")
            conf_text = f"{float(conf_raw) * 100:.1f}%" if conf_raw is not None else ""

            values = [
                str(row["id"]),
                plate,
                province,
                v_type,
                e_time,
                operator,
                status_text,
                conf_text
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                if col == 1:
                    item.setForeground(QColor("#00e5ff"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                
                elif col == 6:
                    if value == "THÔNG QUA": item.setForeground(QColor("#00e676"))
                    elif value == "CẢNH BÁO": item.setForeground(QColor("#ffb300"))
                    elif value == "TỪ CHỐI": item.setForeground(QColor("#ff1744"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                
                elif col == 7:
                    item.setForeground(QColor("#69f0ae"))

                self.table.setItem(row_index, col, item)

            try:
                hour_int = int(str(row["entry_time"]).split()[1].split(':')[0])
                real_hourly_data[hour_int] = real_hourly_data.get(hour_int, 0) + 1
            except:
                pass

        self.draw_chart(real_hourly_data)

    def draw_chart(self, data_dict):
        self.figure.clear()
        self.figure.patch.set_facecolor('#061735')
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#061735')

        hours_range = list(range(12, 24))
        counts = [data_dict.get(h, 0) for h in hours_range]

        bars = ax.bar(hours_range, counts, color='#bf263c', width=0.45, edgecolor='#e63950', linewidth=1.2)
        ax.set_xticks(hours_range)
        ax.set_xticklabels([f"{h}h" for h in hours_range])

        ax.tick_params(colors='#6185b3', labelsize=9, pad=4)
        ax.spines['bottom'].set_color('#163d70')
        ax.spines['left'].set_color('#163d70')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.grid(axis='y', linestyle='--', alpha=0.15, color='#6185b3')

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', color='#ffffff', fontsize=8, fontweight='bold')
                            
        self.figure.subplots_adjust(left=0.06, right=0.96, top=0.85, bottom=0.20)
        self.canvas.draw()
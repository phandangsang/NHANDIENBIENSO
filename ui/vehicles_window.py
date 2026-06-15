import os

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
    
)
from PyQt5.QtGui import QColor, QFont
 
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
        
        title = QLabel("Danh sách xe")
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
        self.status_filter.clear()
        self.status_filter.addItems([
            "Xe dang trong bai",
            "Canh bao",
            "Tu choi",
            "Tat ca lich su",
        ])
        self.status_filter.currentIndexChanged.connect(self.load_data)

        
        self.camera_filter = QComboBox()
        self.camera_filter.addItems(["Tất cả người dùng"])
        self.camera_filter.currentIndexChanged.connect(self.load_data)

        
        filter_layout.addWidget(self.search_input, 5)
        filter_layout.addWidget(self.camera_filter, 3)

        root.addLayout(filter_layout)

        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
       
        self.table.setHorizontalHeaderLabels([
            "#", "BIỂN SỐ", "TỈNH/THÀNH", "LOẠI XE", "THỜI GIAN", "NGƯỜI QUÉT", "TRẠNG THÁI", "CONF."
        ])
        self.table.setHorizontalHeaderLabels([
            "#", "BIEN SO", "TINH/THANH", "THOI GIAN", "NGUOI QUET", "TRANG THAI", "CONF."
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
        if status == "Tat ca lich su":
            pass
        elif status == "Canh bao":
            sql += " AND p.status = 'warning'"
        elif status == "Tu choi":
            sql += " AND p.status = 'deny'"
        else:
            sql += " AND p.status = 'in' AND p.exit_time IS NULL"

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
                
                elif col == 5:
                    if value == "THÔNG QUA": item.setForeground(QColor("#00e676"))
                    elif value == "CẢNH BÁO": item.setForeground(QColor("#ffb300"))
                    elif value == "TỪ CHỐI": item.setForeground(QColor("#ff1744"))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                
                elif col == 6:
                    item.setForeground(QColor("#69f0ae"))

                self.table.setItem(row_index, col, item)

        

   

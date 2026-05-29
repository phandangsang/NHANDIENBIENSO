from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QBrush, QFont
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QScrollArea,
    QFrame, QMessageBox, QDialog, QComboBox,
    QSpacerItem, QStackedWidget,
)
from PyQt5.QtWidgets import QSizePolicy

# ─── COLORS ──────────────────────────────────────────────
BG_DARK      = "#0a1628"
BG_SIDEBAR   = "#0d1e35"
BG_CARD      = "#0f2340"
BG_CARD_HVR  = "#142a4a"
BG_SELECTED  = "#0f2340"
BG_INPUT     = "#0f2340"
ACCENT       = "#3b82f6"
ACCENT_DARK  = "#2563eb"
GREEN        = "#22c55e"
RED          = "#ef4444"
ORANGE       = "#f59e0b"
TEXT_WHITE   = "#f1f5f9"
TEXT_LIGHT   = "#cbd5e1"
TEXT_MUTED   = "#64748b"
BORDER       = "#1e3a5f"
STAT_BG      = "#0d1e35"

AVATAR_COLORS = [
    "#3b82f6", "#8b5cf6", "#10b981",
    "#f59e0b", "#ef4444", "#06b6d4",
    "#ec4899", "#84cc16",
]

STYLE = f"""
* {{
    font-family: 'Segoe UI';
}}
QWidget#mainWidget {{
    background: {BG_DARK};
}}
QWidget#sidebar {{
    background: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}
QWidget#detailPanel {{
    background: {BG_DARK};
}}
QLabel#sidebarTitle {{
    font-size: 14px;
    font-weight: bold;
    color: {TEXT_WHITE};
}}
QLineEdit#searchBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    color: {TEXT_LIGHT};
}}
QLineEdit#searchBox:focus {{
    border-color: {ACCENT};
}}
QPushButton#btnAdd {{
    background: transparent;
    border: 1px dashed {BORDER};
    border-radius: 6px;
    color: {TEXT_MUTED};
    font-size: 13px;
    padding: 8px;
    text-align: center;
}}
QPushButton#btnAdd:hover {{
    background: {BG_CARD};
    border-color: {ACCENT};
    color: {ACCENT};
}}
QPushButton#btnPrimary {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 6px 14px;
    min-height: 30px;
}}
QPushButton#btnPrimary:hover {{
    background: {ACCENT_DARK};
}}
QPushButton#btnDanger {{
    background: #450a0a;
    color: {RED};
    border: 1px solid #7f1d1d;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 6px 14px;
    min-height: 30px;
}}
QPushButton#btnDanger:hover {{
    background: #7f1d1d;
    color: white;
}}
QPushButton#btnWarning {{
    background: #451a03;
    color: {ORANGE};
    border: 1px solid #92400e;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 6px 14px;
    min-height: 30px;
}}
QPushButton#btnWarning:hover {{
    background: #92400e;
    color: white;
}}
QPushButton#btnSecondary {{
    background: {BG_CARD};
    color: {TEXT_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-size: 13px;
    padding: 6px 14px;
    min-height: 30px;
}}
QPushButton#btnSecondary:hover {{
    background: {BG_CARD_HVR};
}}
QLabel#detailEmpty {{
    font-size: 14px;
    color: {TEXT_MUTED};
}}
QLineEdit, QComboBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    color: {TEXT_LIGHT};
    min-height: 30px;
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox QAbstractItemView {{
    background: {BG_CARD};
    color: {TEXT_LIGHT};
    selection-background-color: {BG_SELECTED};
    border: 1px solid {BORDER};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {BG_SIDEBAR};
    width: 5px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


# ════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════
class AvatarLabel(QLabel):
    def __init__(self, initials: str, color: str, size: int = 40, parent=None):
        super().__init__(parent)
        self.initials = initials.upper()[:2]
        self.color = QColor(color)
        self.setFixedSize(size, size)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.setPen(QColor("white"))
        font = QFont("Segoe UI", int(self.width() * 0.3), QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.initials)


def _get_initials(full_name: str, username: str) -> str:
    if full_name and full_name.strip():
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0][0] + parts[-1][0]
        return parts[0][:2]
    return username[:2].upper()


def _avatar_color(idx: int) -> str:
    return AVATAR_COLORS[idx % len(AVATAR_COLORS)]


def _make_divider() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {BORDER}; border: none;")
    return f


def _vsep() -> QFrame:
    s = QFrame()
    s.setFrameShape(QFrame.VLine)
    s.setStyleSheet(f"background: {BORDER}; border: none;")
    s.setFixedWidth(1)
    return s


def _role_text(role: str) -> str:
    return {"admin": "Quản trị viên", "manager": "Giám sát"}.get(role, "Vận hành")


def _role_color(role: str) -> str:
    return {"admin": "#a78bfa", "manager": "#fb923c"}.get(role, "#34d399")


# ════════════════════════════════════════════════════════
# CustomConfirmDialog — Hộp thoại xác nhận xoá hình vuông nền tối
# ════════════════════════════════════════════════════════
class CustomConfirmDialog(QDialog):
    def __init__(self, parent=None, title_text: str = "Xác nhận", message_text: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title_text)
        self.setFixedSize(360, 160)
        
        self.setStyleSheet(
            STYLE + 
            f"QDialog {{ background: {BG_DARK}; }}"
            f"QLabel {{ color: {TEXT_WHITE}; font-size: 14px; border: none; background: transparent; }}"
            f"QPushButton {{ border-radius: 4px; padding: 6px 16px; font-size: 13px; font-weight: bold; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.lbl_msg = QLabel(message_text)
        self.lbl_msg.setWordWrap(True)
        layout.addWidget(self.lbl_msg)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_no = QPushButton("No")
        self.btn_no.setObjectName("btnSecondary")
        self.btn_no.setFixedSize(70, 32)
        self.btn_no.clicked.connect(self.reject)

        self.btn_yes = QPushButton("Yes")
        self.btn_yes.setObjectName("btnPrimary")
        self.btn_yes.setFixedSize(70, 32)
        self.btn_yes.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_no)
        btn_row.addWidget(self.btn_yes)
        layout.addLayout(btn_row)


# ════════════════════════════════════════════════════════
# UserRowWidget — item trong sidebar
# ════════════════════════════════════════════════════════
class UserRowWidget(QWidget):

    def __init__(self, user: dict, on_click, parent=None):
        super().__init__(parent)
        self.user = user
        self.on_click = on_click
        self.selected = False
        self.setFixedHeight(62)
        self.setCursor(Qt.PointingHandCursor)
        self._build()
        self._apply_style(False)

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        initials = _get_initials(
            self.user.get("full_name", ""),
            self.user.get("username", "?"),
            )
        avatar = AvatarLabel(initials, _avatar_color(self.user.get("id", 0)), 38)
        layout.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)

        top = QHBoxLayout()
        top.setSpacing(6)
        name_lbl = QLabel(self.user.get("full_name") or self.user.get("username", ""))
        name_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {TEXT_WHITE};")
        top.addWidget(name_lbl)
        top.addStretch()

        notif = self.user.get("notif", 0)
        if notif:
            badge = QLabel(str(notif))
            badge.setFixedSize(18, 18)
            badge.setAlignment(Qt.AlignCenter)
            # 🌟 ĐÃ SỬA: Thêm border: none; background-color cụ thể để diệt tận gốc khung vuông trắng của badge
            badge.setStyleSheet(
                f"QLabel {{ background-color: {ACCENT}; color: white; border-radius: 9px;"
                f" font-size: 10px; font-weight: bold; border: none; }}"
            )
            top.addWidget(badge)
        info.addLayout(top)

        bot = QHBoxLayout()
        bot.setSpacing(5)

        role = self.user.get("role", "staff")
        role_lbl = QLabel(_role_text(role))
        role_lbl.setStyleSheet(f"font-size: 11px; color: {_role_color(role)};")

        sep = QLabel("·")
        sep.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")

        bot.addWidget(role_lbl)
        bot.addWidget(sep)
        bot.addStretch()

        info.addLayout(bot)
        layout.addLayout(info)

    def _apply_style(self, selected: bool):
        self.selected = selected
        if selected:
            self.setStyleSheet(
                f"QWidget {{ background-color: {BG_SELECTED}; border-radius: 6px; border-left: 3px solid {ACCENT}; }} "
                f"QLabel {{ border: none; background: transparent; }}"
            )
        else:
            self.setStyleSheet(
                f"QWidget {{ background-color: transparent; border-radius: 6px; border-left: 3px solid transparent; }} "
                f"QWidget:hover {{ background-color: rgba(255, 255, 255, 0.05); }} "
                f"QLabel {{ border: none; background: transparent; }}"
            )

    def set_selected(self, val: bool):
        self._apply_style(val)

    def mousePressEvent(self, event):
        self.on_click(self.user)


# ════════════════════════════════════════════════════════
# UserDialog — thêm / sửa user (chỉ thu thập data)
# ════════════════════════════════════════════════════════
class UserDialog(QDialog):

    def __init__(self, parent=None, user_data: dict = None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None
        self.result_data: dict = {}

        self.setWindowTitle("Sửa thông tin" if self.is_edit else "Thêm người dùng mới")
        # Tăng nhẹ chiều cao (360 và 420) để form thoáng hơn khi có khoảng cách giãn dòng
        self.setFixedSize(420, 360 if self.is_edit else 430)
        self.setStyleSheet(STYLE + f"QDialog {{ background: {BG_DARK}; }}")
        self._build()
        if self.is_edit:
            self._fill()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24) # Đều rìa 24px cho chuẩn UI
        layout.setSpacing(6) # Spacing nhỏ giúp Nhãn chữ dính gần vào Ô Nhập của chính nó

        title = QLabel("Sửa thông tin" if self.is_edit else "Thêm người dùng mới")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_WHITE}; border: none; background: transparent;")
        layout.addWidget(title)
        layout.addWidget(_make_divider())
        layout.addSpacing(8) # Khoảng cách từ tiêu đề xuống ô nhập đầu tiên

        # 🌟 ĐOẠN SỬA CHÍNH: Cập nhật lại hàm tạo field chung
        def field(label_text, widget):
            lbl = QLabel(label_text)
            # Thêm border: none và background: transparent để DIỆT TẬN GỐC khung trắng
            lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {TEXT_MUTED}; border: none; background: transparent;")
            layout.addWidget(lbl)
            layout.addWidget(widget)
            layout.addSpacing(12) # 🌟 Tự động tạo khoảng cách giãn đều với cụm tiếp theo

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Tên đăng nhập...")
        if self.is_edit:
            self.inp_username.setReadOnly(True)
            self.inp_username.setStyleSheet(
                f"background: {BG_CARD}; color: {TEXT_MUTED}; border-radius: 6px;"
                f" padding: 6px 10px; font-size: 13px; border: 1px solid {BORDER};"
            )
        field("Tên đăng nhập", self.inp_username)

        self.inp_fullname = QLineEdit()
        self.inp_fullname.setPlaceholderText("Họ và tên đầy đủ...")
        field("Họ và tên", self.inp_fullname)

        self.inp_role = QComboBox()
        self.inp_role.addItems(["staff", "manager", "admin"])
        field("Vai trò", self.inp_role)

        if not self.is_edit:
            self.inp_password = QLineEdit()
            self.inp_password.setPlaceholderText("Mật khẩu...")
            self.inp_password.setEchoMode(QLineEdit.Password)
            field("Mật khẩu", self.inp_password)

        # Giữ khoảng cách vừa phải trước khi đến hàng nút bấm
        layout.addSpacerItem(QSpacerItem(0, 10))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Lưu" if self.is_edit else "Thêm")
        btn_ok.setObjectName("btnPrimary")
        btn_ok.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _fill(self):
        self.inp_username.setText(self.user_data.get("username", ""))
        self.inp_fullname.setText(self.user_data.get("full_name", "") or "")
        idx = self.inp_role.findText(self.user_data.get("role", "staff"))
        if idx >= 0:
            self.inp_role.setCurrentIndex(idx)

    def _save(self):
        u = self.inp_username.text().strip()
        if not u:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập.")
            return
        self.result_data = {
            "username":  u,
            "full_name": self.inp_fullname.text().strip(),
            "role":      self.inp_role.currentText(),
        }
        if not self.is_edit:
            p = self.inp_password.text().strip()
            if not p:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu.")
                return
            self.result_data["password"] = p
        self.accept()

# ════════════════════════════════════════════════════════
# ChangePasswordDialog
# ════════════════════════════════════════════════════════
class ChangePasswordDialog(QDialog):

    def __init__(self, parent=None, username: str = ""):
        super().__init__(parent)
        self.new_password = ""
        self.setWindowTitle("Đổi mật khẩu")
        # 🌟 Tăng chiều cao từ 250 lên 280 để form thoáng đẹp sau khi giãn dòng
        self.setFixedSize(380, 280)
        self.setStyleSheet(STYLE + f"QDialog {{ background: {BG_DARK}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24) # Căn đều rìa 24px cho đẹp
        layout.setSpacing(6) # Giữ khoảng cách khít giữa chữ và ô nhập tương ứng

        title = QLabel(f"Đổi mật khẩu — {username}")
        # Thêm khử viền trắng cho tiêu đề
        title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {TEXT_WHITE}; border: none; background: transparent;")
        layout.addWidget(title)
        layout.addWidget(_make_divider())
        layout.addSpacing(8) # Khoảng cách từ tiêu đề xuống ô bên dưới

        # 🌟 ĐOẠN SỬA CHÍNH: Cập nhật hàm field xóa viền trắng và giãn cách
        def field(lbl_text, widget):
            lbl = QLabel(lbl_text)
            # Thêm border: none và background: transparent để xóa sạch viền trắng cứng đầu
            lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {TEXT_MUTED}; border: none; background: transparent;")
            layout.addWidget(lbl)
            layout.addWidget(widget)
            layout.addSpacing(12) # 🌟 Tạo khoảng cách 12px đều đặn giữa cụm này với cụm tiếp theo

        self.inp_new = QLineEdit()
        self.inp_new.setPlaceholderText("Mật khẩu mới...")
        self.inp_new.setEchoMode(QLineEdit.Password)
        field("Mật khẩu mới", self.inp_new)

        self.inp_confirm = QLineEdit()
        self.inp_confirm.setPlaceholderText("Xác nhận mật khẩu...")
        self.inp_confirm.setEchoMode(QLineEdit.Password)
        field("Xác nhận", self.inp_confirm)

        layout.addSpacerItem(QSpacerItem(0, 8))
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        bc = QPushButton("Hủy")
        bc.setObjectName("btnSecondary")
        bc.clicked.connect(self.reject)
        bs = QPushButton("Đổi mật khẩu")
        bs.setObjectName("btnPrimary")
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(bs)
        layout.addLayout(btn_row)

    def _save(self):
        n = self.inp_new.text().strip()
        c = self.inp_confirm.text().strip()
        if not n:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu mới.")
            return
        if n != c:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        self.new_password = n
        self.accept()


# ════════════════════════════════════════════════════════
# StatCard — ô số liệu (Tổng quét / Cảnh báo / Từ chối)
# ════════════════════════════════════════════════════════
class _StatCard(QFrame):

    def __init__(self, number, label: str, number_color: str = TEXT_WHITE, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 6px; }}")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        num_lbl = QLabel(str(number))
        num_lbl.setAlignment(Qt.AlignCenter)
        num_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {number_color}; background: transparent; border: none;")
        layout.addWidget(num_lbl)

        lbl = QLabel(label.upper())
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px; background: transparent; border: none;")
        layout.addWidget(lbl)


# ════════════════════════════════════════════════════════
# _InfoField — ô thông tin (điện thoại, email, ca làm việc)
# ════════════════════════════════════════════════════════
class _InfoField(QFrame):

    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 6px; }}")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(70)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(3)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px; background: transparent; border: none;")
        layout.addWidget(lbl)

        val = QLabel(value if value else "—")
        val.setStyleSheet(f"font-size: 13px; color: {TEXT_LIGHT}; background: transparent; border: none;")
        layout.addWidget(val)


# ════════════════════════════════════════════════════════
# _ScanRow — hàng lịch sử quét
# ════════════════════════════════════════════════════════
class _ScanRow(QFrame):

    _STATUS = {
        "THÔNG QUA": ("#22c55e", "#052e16"),
        "CẢNH BÁO":   ("#f59e0b", "#2d1a00"),
        "TỪ CHỐI":   ("#ef4444", "#2d0a0a"),
    }

    def __init__(self, plate: str, info: str, scan_time: str, status: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 6px; }}")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        plate_lbl = QLabel(plate)
        plate_lbl.setFixedWidth(120)
        plate_lbl.setAlignment(Qt.AlignCenter)
        plate_lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a1a1a;"
            " background: #e2e8f0; border-radius: 4px; padding: 3px 10px; border: none;"
        )
        layout.addWidget(plate_lbl)

        info_lbl = QLabel(info)
        info_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; background: transparent; border: none;")
        layout.addWidget(info_lbl, stretch=1)

        time_lbl = QLabel(scan_time)
        time_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; background: transparent; border: none;")
        layout.addWidget(time_lbl)

        fg, bg = self._STATUS.get(status, (TEXT_LIGHT, BG_CARD))
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {fg}; background: {bg};"
            f" border-radius: 4px; padding: 3px 10px; border: none;"
        )
        layout.addWidget(status_lbl)


# ════════════════════════════════════════════════════════
# UserPage — trang quản lý người dùng chính
# ════════════════════════════════════════════════════════
class UserPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._users: list = []
        self._selected: dict = None
        self._rows: list = []

        self.on_add             = None
        self.on_edit            = None
        self.on_delete          = None
        self.on_change_password = None

        self.setObjectName("mainWidget")
        self.setStyleSheet(STYLE)
        self._build_ui()

    def set_callbacks(self, *, on_add=None, on_edit=None, on_delete=None, on_change_password=None):
        self.on_add             = on_add
        self.on_edit            = on_edit
        self.on_delete          = on_delete
        self.on_change_password = on_change_password

    def load_users(self, users: list):
        self._users = list(users)
        self._render_list(self._users)
        if self._users:
            self._select_user(self._users[0])

    def refresh_user(self, updated_user: dict):
        for i, u in enumerate(self._users):
            if u["id"] == updated_user["id"]:
                self._users[i] = updated_user
                break
        self._render_list(self._filter(self.search.text()))
        if self._selected and self._selected["id"] == updated_user["id"]:
            self._selected = updated_user
            self._build_detail(updated_user)

    def remove_user(self, user_id: int):
        self._users = [u for u in self._users if u["id"] != user_id]
        self._render_list(self._filter(self.search.text()))
        if self._selected and self._selected["id"] == user_id:
            self._selected = None
            self.stack.setCurrentIndex(0)

    def _filter(self, text: str) -> list:
        t = text.strip().lower()
        if not t:
            return self._users
        return [u for u in self._users if t in u.get("username", "").lower() or t in u.get("full_name", "").lower()]

    def _on_search(self):
        self._render_list(self._filter(self.search.text()))

    def _select_user(self, user: dict):
        self._selected = user
        for row in self._rows:
            row.set_selected(row.user["id"] == user["id"])
        self._build_detail(user)
        self.stack.setCurrentIndex(1)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(10, 14, 10, 10)
        sb.setSpacing(8)

        title = QLabel("Danh sách người dùng")
        title.setObjectName("sidebarTitle")
        sb.addWidget(title)

        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Tìm người dùng...")
        self.search.textChanged.connect(self._on_search)
        sb.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 2, 0, 2)
        self.list_layout.setSpacing(2)
        scroll.setWidget(self.list_container)
        sb.addWidget(scroll, stretch=1)

        sb.addWidget(_make_divider())

        btn_add = QPushButton("＋   Thêm người dùng mới")
        btn_add.setObjectName("btnAdd")
        btn_add.clicked.connect(self._on_add)
        sb.addWidget(btn_add)

        root.addWidget(sidebar)

        # Detail Panel
        detail_panel = QWidget()
        detail_panel.setObjectName("detailPanel")
        dp = QVBoxLayout(detail_panel)
        dp.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        dp.addWidget(self.stack)

        empty_page = QWidget()
        ev = QVBoxLayout(empty_page)
        empty_lbl = QLabel("Chọn người dùng để xem chi tiết")
        empty_lbl.setObjectName("detailEmpty")
        empty_lbl.setAlignment(Qt.AlignCenter)
        ev.addWidget(empty_lbl)
        self.stack.addWidget(empty_page)

        self.detail_page = QWidget()
        self.stack.addWidget(self.detail_page)

        root.addWidget(detail_panel, stretch=1)

    def _render_list(self, users: list):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._rows.clear()

        for user in users:
            row = UserRowWidget(user, self._select_user)
            self.list_layout.addWidget(row)
            self._rows.append(row)

        self.list_layout.addStretch()

        if self._selected:
            for row in self._rows:
                if row.user["id"] == self._selected["id"]:
                    row.set_selected(True)

    def _build_detail(self, user: dict):
        old = self.detail_page.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
            old.deleteLater()

        layout = QVBoxLayout(self.detail_page)
        self.detail_page.setStyleSheet(f"background: {BG_DARK};")
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Widget
        header = QWidget()
        header.setStyleSheet(f"background: {BG_DARK}; border: none;")
        hdr = QHBoxLayout(header)
        hdr.setContentsMargins(24, 20, 24, 16)
        hdr.setSpacing(16)

        avatar = AvatarLabel(
            _get_initials(user.get("full_name", ""), user.get("username", "")),
            _avatar_color(user.get("id", 0)),
            56,
        )
        hdr.addWidget(avatar, alignment=Qt.AlignTop)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)

        name_lbl = QLabel(user.get("full_name") or user.get("username", ""))
        name_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT_WHITE}; border: none; background: transparent;")
        name_col.addWidget(name_lbl)

        role = user.get("role", "staff")
        role_lbl = QLabel(_role_text(role))
        role_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; border: none; background: transparent;")
        name_col.addWidget(role_lbl)

        status_pill = QLabel("● Hoạt động")
        status_pill.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {GREEN}; border: 1px solid {GREEN}; "
            f"border-radius: 10px; padding: 2px 10px; background: transparent;"
        )
        name_col.addWidget(status_pill)
        name_col.addStretch()
        hdr.addLayout(name_col, stretch=1)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        btn_col.setAlignment(Qt.AlignTop)

        btn_edit = QPushButton("✏   Sửa thông tin")
        btn_edit.setObjectName("btnPrimary")
        btn_edit.setFixedSize(150, 32)
        btn_edit.clicked.connect(lambda: self._on_edit(user))

        btn_pw = QPushButton("🔑   Đổi mật khẩu")
        btn_pw.setObjectName("btnWarning")
        btn_pw.setFixedSize(150, 32)
        btn_pw.clicked.connect(lambda: self._on_change_password(user))

        btn_del = QPushButton("🗑   Xóa tài khoản")
        btn_del.setObjectName("btnDanger")
        btn_del.setFixedSize(150, 32)
        btn_del.clicked.connect(lambda: self._on_delete(user))

        btn_col.addWidget(btn_edit)
        btn_col.addWidget(btn_pw)
        btn_col.addWidget(btn_del)
        hdr.addLayout(btn_col)

        layout.addWidget(header)

        # ── HÀNG 1: Ô số liệu thống kê (Tổng quét / Cảnh báo / Từ chối) ──
        stat_w = QWidget()
        stat_w.setStyleSheet(f"background: {BG_DARK}; border: none;")
        stat_lay = QHBoxLayout(stat_w)
        stat_lay.setContentsMargins(24, 6, 24, 6)
        stat_lay.setSpacing(12)
        
        stats = user.get("stats", {})
        stat_lay.addWidget(_StatCard(stats.get("total", 0), "Tổng quét", TEXT_WHITE), stretch=1)
        stat_lay.addWidget(_StatCard(stats.get("warning", 0), "Cảnh báo", ORANGE), stretch=1)
        stat_lay.addWidget(_StatCard(stats.get("denied", 0), "Từ chối", RED), stretch=1)
        layout.addWidget(stat_w)

        # ── HÀNG 2: Điện thoại | Ca làm việc (2 cột song song) ──
        contact_w = QWidget()
        contact_w.setStyleSheet(f"background: {BG_DARK}; border: none;")
        contact_lay = QHBoxLayout(contact_w)
        contact_lay.setContentsMargins(24, 6, 24, 6)
        contact_lay.setSpacing(12)
        
        contact_lay.addWidget(_InfoField("Điện thoại", user.get("phone", "")), stretch=1)
        contact_lay.addWidget(_InfoField("Ca làm việc", user.get("shift", "")), stretch=1)
        layout.addWidget(contact_w)

        # ── HÀNG 3: Email (1 cột trải dài toàn chiều ngang) ──
        email_w = QWidget()
        email_w.setStyleSheet(f"background: {BG_DARK}; border: none;")
        email_lay = QHBoxLayout(email_w)
        email_lay.setContentsMargins(24, 6, 24, 6)
        email_lay.setSpacing(12)
        
        email_lay.addWidget(_InfoField("Email", user.get("email", "")), stretch=1)
        layout.addWidget(email_w)
        # ── HÀNG 3: Lịch sử quét gần đây ──
        history_title = QLabel("LỊCH SỬ QUÉT GẦN ĐÂY")
        history_title.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {TEXT_MUTED}; "
            f"letter-spacing: 1px; padding: 16px 24px 8px 24px; border: none; background: transparent;"
        )
        layout.addWidget(history_title)

        scroll_history = QScrollArea()
        scroll_history.setWidgetResizable(True)
        scroll_history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        history_container = QWidget()
        history_container.setStyleSheet("background: transparent; border: none;")
        history_layout = QVBoxLayout(history_container)
        history_layout.setContentsMargins(24, 0, 24, 16)
        history_layout.setSpacing(8)

        scans = user.get("recent_scans", [])
        if scans:
            for s in scans:
                row = _ScanRow(s.get("plate", ""), s.get("info", ""), s.get("time", ""), s.get("status", ""))
                history_layout.addWidget(row)
        else:
            no_scan = QLabel("Chưa có dữ liệu lịch sử quét.")
            no_scan.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; border: none; background: transparent;")
            history_layout.addWidget(no_scan)

        history_layout.addStretch()
        scroll_history.setWidget(history_container)
        layout.addWidget(scroll_history, stretch=1)

    # ── Callbacks Processing ─────────────────────────────

    def _on_add(self):
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted and self.on_add:
            self.on_add(dialog.result_data)

    def _on_edit(self, user: dict):
        dialog = UserDialog(self, user)
        if dialog.exec_() == QDialog.Accepted and self.on_edit:
            self.on_edit(user["id"], dialog.result_data)

    def _on_change_password(self, user: dict):
        dialog = ChangePasswordDialog(self, user.get("username", ""))
        if dialog.exec_() == QDialog.Accepted and self.on_change_password:
            self.on_change_password(user["id"], dialog.new_password)

    # 🌟 Đstyle: Đã áp dụng Custom Confirm Dialog hình vuông đồng bộ tuyệt đối
    def _on_delete(self, user: dict):
        dialog = CustomConfirmDialog(
            self, 
            "Xác nhận xóa", 
            f"Xóa người dùng '{user.get('username', '')}'?"
        )
        if dialog.exec_() == QDialog.Accepted:
            if self.on_delete:
                self.on_delete(user["id"])


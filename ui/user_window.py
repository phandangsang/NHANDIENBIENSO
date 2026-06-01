import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def _load_user_style():
    style_path = os.path.join(os.path.dirname(__file__), "style", "user.css")
    try:
        with open(style_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def _text(value, fallback="-"):
    if value in (None, ""):
        return fallback
    return str(value)


class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.is_edit = user_data is not None
        self.result_data = {}

        self.setObjectName("UserDialog")
        self.setWindowTitle("Sua nguoi dung" if self.is_edit else "Them nguoi dung")
        self.setFixedSize(390, 345 if self.is_edit else 410)
        self.setStyleSheet(_load_user_style())

        self.username_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.role_input = QComboBox()
        self.password_input = QLineEdit()

        self._build_ui()
        self._fill_form()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        title = QLabel("Sua nguoi dung" if self.is_edit else "Them nguoi dung")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        self.username_input.setPlaceholderText("Ten dang nhap")
        self.full_name_input.setPlaceholderText("Ho ten")
        self.role_input.addItems(["staff", "admin"])
        self.password_input.setPlaceholderText("Mat khau")
        self.password_input.setEchoMode(QLineEdit.Password)

        if self.is_edit:
            self.username_input.setReadOnly(True)

        layout.addWidget(QLabel("Ten dang nhap"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Ho ten"))
        layout.addWidget(self.full_name_input)
        layout.addWidget(QLabel("Vai tro"))
        layout.addWidget(self.role_input)

        if not self.is_edit:
            layout.addWidget(QLabel("Mat khau"))
            layout.addWidget(self.password_input)

        actions = QHBoxLayout()
        cancel_button = QPushButton("Huy")
        cancel_button.setObjectName("GhostButton")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Luu" if self.is_edit else "Them")
        save_button.clicked.connect(self._save)
        actions.addWidget(cancel_button)
        actions.addWidget(save_button)

        layout.addStretch()
        layout.addLayout(actions)

    def _fill_form(self):
        if not self.is_edit:
            return
        self.username_input.setText(self.user_data.get("username", ""))
        self.full_name_input.setText(self.user_data.get("full_name", "") or "")
        role_index = self.role_input.findText(self.user_data.get("role", "staff"))
        self.role_input.setCurrentIndex(role_index if role_index >= 0 else 0)

    def _save(self):
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        role = self.role_input.currentText()

        if not username:
            QMessageBox.warning(self, "Thieu du lieu", "Vui long nhap ten dang nhap.")
            return

        self.result_data = {
            "username": username,
            "full_name": full_name,
            "role": role,
        }

        if not self.is_edit:
            password = self.password_input.text().strip()
            if not password:
                QMessageBox.warning(self, "Thieu du lieu", "Vui long nhap mat khau.")
                return
            self.result_data["password"] = password

        self.accept()


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None, username=""):
        super().__init__(parent)
        self.new_password = ""

        self.setObjectName("UserDialog")
        self.setWindowTitle("Doi mat khau")
        self.setFixedSize(380, 250)
        self.setStyleSheet(_load_user_style())

        self.password_input = QLineEdit()
        self.confirm_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setEchoMode(QLineEdit.Password)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        title = QLabel(f"Doi mat khau: {username}")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Mat khau moi"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Nhap lai mat khau"))
        layout.addWidget(self.confirm_input)

        actions = QHBoxLayout()
        cancel_button = QPushButton("Huy")
        cancel_button.setObjectName("GhostButton")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Luu")
        save_button.clicked.connect(self._save)
        actions.addWidget(cancel_button)
        actions.addWidget(save_button)

        layout.addStretch()
        layout.addLayout(actions)

    def _save(self):
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not password:
            QMessageBox.warning(self, "Thieu du lieu", "Vui long nhap mat khau moi.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Sai du lieu", "Mat khau nhap lai khong khop.")
            return

        self.new_password = password
        self.accept()


class UserPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UserPage")
        self.setStyleSheet(_load_user_style())

        self._users = []
        self._visible_users = []
        self._selected = None

        self.on_add = None
        self.on_edit = None
        self.on_delete = None
        self.on_change_password = None

        self._build_ui()
        self._clear_detail()

    def set_callbacks(self, *, on_add=None, on_edit=None, on_delete=None, on_change_password=None):
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_change_password = on_change_password

    def load_users(self, users):
        selected_id = self._selected.get("id") if self._selected else None
        self._users = list(users or [])
        self._render_list(selected_id=selected_id)

    def refresh_user(self, updated_user):
        updated_id = updated_user.get("id")
        for index, user in enumerate(self._users):
            if user.get("id") == updated_id:
                self._users[index] = updated_user
                break
        else:
            self._users.append(updated_user)
        self._render_list(selected_id=updated_id)

    def remove_user(self, user_id):
        self._users = [user for user in self._users if user.get("id") != user_id]
        next_id = self._users[0].get("id") if self._users else None
        self._render_list(selected_id=next_id)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        side_panel = QFrame()
        side_panel.setObjectName("SidePanel")
        side_panel.setFixedWidth(340)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(20, 20, 18, 20)
        side_layout.setSpacing(14)

        title = QLabel("Nguoi dung")
        title.setObjectName("PageTitle")
        side_layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tim ten, username...")
        self.search_input.textChanged.connect(self._render_list)
        side_layout.addWidget(self.search_input)

        self.user_list = QListWidget()
        self.user_list.currentRowChanged.connect(self._handle_row_changed)
        side_layout.addWidget(self.user_list, 1)

        add_button = QPushButton("+ Them nguoi dung")
        add_button.setObjectName("PrimaryButton")
        add_button.clicked.connect(self._open_add_dialog)
        side_layout.addWidget(add_button)

        content_panel = QFrame()
        content_panel.setObjectName("ContentPanel")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(28, 24, 28, 24)
        content_layout.setSpacing(16)

        header = QHBoxLayout()
        identity = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setObjectName("Name")
        self.username_label = QLabel()
        self.username_label.setObjectName("Muted")
        identity.addWidget(self.name_label)
        identity.addWidget(self.username_label)
        self.role_label = QLabel()
        self.role_label.setObjectName("RolePill")
        header.addLayout(identity)
        header.addStretch()
        header.addWidget(self.role_label, alignment=Qt.AlignTop)
        content_layout.addLayout(header)



        info_card = QFrame()
        info_card.setObjectName("Card")
        info_layout = QGridLayout(info_card)
        info_layout.setContentsMargins(18, 16, 18, 16)
        info_layout.setHorizontalSpacing(24)
        info_layout.setVerticalSpacing(10)
        self.email_value = self._add_info_row(info_layout, 0, "Email")
        self.phone_value = self._add_info_row(info_layout, 1, "Dien thoai")
        self.shift_value = self._add_info_row(info_layout, 2, "Ca lam viec")
        self.created_value = self._add_info_row(info_layout, 3, "Ngay tao")
        content_layout.addWidget(info_card)

        recent_title = QLabel("Luot quet gan day")
        recent_title.setObjectName("PageTitle")
        content_layout.addWidget(recent_title)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(180)
        content_layout.addWidget(self.recent_list)
        content_layout.addStretch()

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Sua thong tin")
        self.edit_button.setObjectName("PrimaryButton")
        self.edit_button.clicked.connect(self._open_edit_dialog)
        self.password_button = QPushButton("Doi mat khau")
        self.password_button.setObjectName("GhostButton")
        self.password_button.clicked.connect(self._open_password_dialog)
        self.delete_button = QPushButton("Xoa nguoi dung")
        self.delete_button.setObjectName("DangerButton")
        self.delete_button.clicked.connect(self._delete_selected)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.password_button)
        actions.addStretch()
        actions.addWidget(self.delete_button)
        content_layout.addLayout(actions)

        root.addWidget(side_panel)
        root.addWidget(content_panel, 1)



    def _add_info_row(self, layout, row, label_text):
        label = QLabel(label_text.upper())
        label.setObjectName("InfoLabel")
        value = QLabel("-")
        value.setObjectName("Muted")
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(label, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def _render_list(self, *_, selected_id=None):
        keyword = self.search_input.text().strip().lower()
        self._visible_users = [
            user
            for user in self._users
            if not keyword
            or keyword in (user.get("username") or "").lower()
            or keyword in (user.get("full_name") or "").lower()
            or keyword in (user.get("role") or "").lower()
        ]

        if selected_id is None and self._selected:
            selected_id = self._selected.get("id")

        self.user_list.blockSignals(True)
        self.user_list.clear()
        selected_row = -1
        for row, user in enumerate(self._visible_users):
            name = user.get("full_name") or user.get("username") or "Nguoi dung"
            role = user.get("role") or "staff"
            online = "online" if user.get("online") else "offline"
            item = QListWidgetItem(f"{name}\n{user.get('username', '')} | {role} | {online}")
            item.setData(Qt.UserRole, user.get("id"))
            item.setSizeHint(item.sizeHint())
            self.user_list.addItem(item)
            if selected_id is not None and user.get("id") == selected_id:
                selected_row = row
        self.user_list.blockSignals(False)

        if selected_row >= 0:
            self.user_list.setCurrentRow(selected_row)
            self._show_user(self._visible_users[selected_row])
        elif self._visible_users:
            self.user_list.setCurrentRow(0)
            self._show_user(self._visible_users[0])
        else:
            self._clear_detail()

    def _handle_row_changed(self, row):
        if 0 <= row < len(self._visible_users):
            self._show_user(self._visible_users[row])

    def _show_user(self, user):
        self._selected = user
        self.name_label.setText(user.get("full_name") or user.get("username") or "Nguoi dung")
        self.username_label.setText(f"Username: {_text(user.get('username'))}")
        self.role_label.setText((_text(user.get("role"), "staff")).upper())

    

        self.email_value.setText(_text(user.get("email")))
        self.phone_value.setText(_text(user.get("phone")))
        self.shift_value.setText(_text(user.get("shift")))
        self.created_value.setText(_text(user.get("created_at")))

        self.recent_list.clear()
        recent_scans = user.get("recent_scans") or []
        if not recent_scans:
            self.recent_list.addItem("Chua co luot quet gan day")
        else:
            for scan in recent_scans[:6]:
                if isinstance(scan, dict):
                    plate = scan.get("plate_number") or scan.get("plate") or "-"
                    status = scan.get("status") or "-"
                    time = scan.get("time") or scan.get("created_at") or ""
                    self.recent_list.addItem(f"{plate} | {status} | {time}")
                else:
                    self.recent_list.addItem(str(scan))

        self._set_actions_enabled(True)

    def _clear_detail(self):
        self._selected = None
        self.name_label.setText("Chua chon nguoi dung")
        self.username_label.setText("Chon mot nguoi dung o danh sach ben trai")
        self.role_label.setText("-")
        self.email_value.setText("-")
        self.phone_value.setText("-")
        self.shift_value.setText("-")
        self.created_value.setText("-")
        self.recent_list.clear()
        self.recent_list.addItem("Khong co du lieu")
        self._set_actions_enabled(False)

    def _set_actions_enabled(self, enabled):
        self.edit_button.setEnabled(enabled)
        self.password_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def _open_add_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted and self.on_add:
            self.on_add(dialog.result_data)

    def _open_edit_dialog(self):
        if not self._selected:
            return
        dialog = UserDialog(self, self._selected)
        if dialog.exec_() == QDialog.Accepted and self.on_edit:
            self.on_edit(self._selected.get("id"), dialog.result_data)

    def _open_password_dialog(self):
        if not self._selected:
            return
        dialog = ChangePasswordDialog(self, self._selected.get("username", ""))
        if dialog.exec_() == QDialog.Accepted and self.on_change_password:
            self.on_change_password(self._selected.get("id"), dialog.new_password)

    def _delete_selected(self):
        if not self._selected or not self.on_delete:
            return

        username = self._selected.get("username", "")
        answer = QMessageBox.question(
            self,
            "Xac nhan xoa",
            f"Ban co chac muon xoa nguoi dung '{username}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.on_delete(self._selected.get("id"))

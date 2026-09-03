import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from src.crypto_utils import AUTH_FILE, SALT_FILE, get_or_create_salt, hash_password

class HistoryDialog(QDialog):
    def __init__(self, history_list, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(500, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 14px;
            }
            QListWidget {
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ff5f56;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header = QHBoxLayout()
        title = QLabel("History Browsing")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.list_widget = QListWidget()
        for item in reversed(history_list):
            self.list_widget.addItem(QListWidgetItem(f"{item['title']}\n{item['url']}"))
        layout.addWidget(self.list_widget)

class DownloadsDialog(QDialog):
    def __init__(self, downloads_list, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(480, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 14px;
            }
            QListWidget {
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ff5f56;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header = QHBoxLayout()
        title = QLabel("Downloads")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.list_widget = QListWidget()
        if not downloads_list:
            self.list_widget.addItem("Belum ada file yang diunduh.")
        else:
            for d in reversed(downloads_list):
                self.list_widget.addItem(f"{d['filename']} - {d['status']}")
        layout.addWidget(self.list_widget)

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(360, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
            }
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5f56, stop:1 #ffbd2e);
                color: black;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Ubah Password Browser")
        title.setStyleSheet("font-weight: bold; font-size: 15px;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.Password)
        self.old_pwd.setPlaceholderText("Password Lama")
        layout.addWidget(self.old_pwd)

        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setPlaceholderText("Password Baru")
        layout.addWidget(self.new_pwd)

        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setPlaceholderText("Konfirmasi Password Baru")
        layout.addWidget(self.confirm_pwd)

        save_btn = QPushButton("Simpan Password Baru")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.change_password)
        layout.addWidget(save_btn)

    def change_password(self):
        old_p = self.old_pwd.text()
        new_p = self.new_pwd.text()
        conf_p = self.confirm_pwd.text()

        if not old_p or not new_p or not conf_p:
            QMessageBox.warning(self, "Error", "Semua kolom wajib diisi!")
            return

        salt = get_or_create_salt()
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, "r") as f:
                saved_hash = f.read().strip()
            if hash_password(old_p, salt) != saved_hash:
                QMessageBox.warning(self, "Error", "Password lama salah!")
                return

        if new_p != conf_p:
            QMessageBox.warning(self, "Error", "Password baru dan konfirmasi tidak cocok!")
            return

        with open(AUTH_FILE, "w") as f:
            f.write(hash_password(new_p, salt))

        QMessageBox.information(self, "Sukses", "Password berhasil diperbarui!")
        self.accept()

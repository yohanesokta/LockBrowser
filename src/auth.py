import os
import sys
import shutil
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent
from src.crypto_utils import (
    PROFILE_DIR, AUTH_FILE, SALT_FILE, ENC_PROFILE_FILE,
    get_or_create_salt, hash_password, check_auth_integrity,
    decrypt_and_mount_profile, encrypt_and_unmount_profile
)

class AuthDialog(QDialog):
    def __init__(self, mode="LOGIN"):
        super().__init__()
        self.mode = mode
        self.authenticated = False
        self.user_password = None
        self._drag_pos = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 310)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #26242c,
                    stop:0.5 #1e1d24,
                    stop:1 #17161c);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
            }
            QLabel {
                color: #e0e0e0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.45);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                padding: 10px 14px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #ff5f56;
            }
            QPushButton#primary_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5f56, stop:1 #ffbd2e);
                color: #121212;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-radius: 10px;
                padding: 11px;
            }
            QPushButton#primary_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff736b, stop:1 #ffc747);
            }
            QPushButton#secondary_btn {
                background-color: rgba(255, 255, 255, 0.08);
                color: #cccccc;
                font-size: 12px;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton#secondary_btn:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #aaaaaa;
                border-radius: 8px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #ff5f56;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)

        if self.mode == "SETUP":
            title = QLabel("Lock Browser Setup")
            title.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff;")
            layout.addWidget(title)
            
            sub = QLabel("Buat password untuk mengamankan data enkripsi browser:")
            sub.setStyleSheet("font-size: 12px; color: #a0a0ab;")
            sub.setWordWrap(True)
            layout.addWidget(sub)

            self.pwd_input = QLineEdit()
            self.pwd_input.setEchoMode(QLineEdit.Password)
            self.pwd_input.setPlaceholderText("Password")
            layout.addWidget(self.pwd_input)

            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("Konfirmasi Password")
            self.confirm_input.returnPressed.connect(self.submit)
            layout.addWidget(self.confirm_input)

            btn = QPushButton("Set Password & Masuk")
            btn.setObjectName("primary_btn")
            btn.clicked.connect(self.submit)
            layout.addWidget(btn)

        elif self.mode == "LOGIN":
            title = QLabel("Browser Terkunci")
            title.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff;")
            layout.addWidget(title)

            sub = QLabel("Masukkan password untuk membuka enkripsi profil:")
            sub.setStyleSheet("font-size: 12px; color: #a0a0ab;")
            sub.setWordWrap(True)
            layout.addWidget(sub)

            self.pwd_input = QLineEdit()
            self.pwd_input.setEchoMode(QLineEdit.Password)
            self.pwd_input.setPlaceholderText("Password")
            self.pwd_input.returnPressed.connect(self.submit)
            layout.addWidget(self.pwd_input)

            btn = QPushButton("Buka Browser")
            btn.setObjectName("primary_btn")
            btn.clicked.connect(self.submit)
            layout.addWidget(btn)

        elif self.mode == "CORRUPTED":
            title = QLabel("Keamanan Terdeteksi Corrupt")
            title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ff5f56;")
            layout.addWidget(title)

            msg = QLabel("File keamanan atau data terenkripsi tidak cocok.\n\nAnda harus menghapus seluruh sesi lama untuk mereset browser.")
            msg.setStyleSheet("font-size: 12px; color: #a0a0ab;")
            msg.setWordWrap(True)
            layout.addWidget(msg)

            reset_btn = QPushButton("Hapus Sesi & Reset Browser")
            reset_btn.setObjectName("primary_btn")
            reset_btn.setStyleSheet("background: #ff5f56; color: white; border-radius: 10px; padding: 10px;")
            reset_btn.clicked.connect(self.reset_all_data)
            layout.addWidget(reset_btn)

            cancel_btn = QPushButton("Batal / Keluar")
            cancel_btn.setObjectName("secondary_btn")
            cancel_btn.clicked.connect(self.reject)
            layout.addWidget(cancel_btn)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def submit(self):
        if self.mode == "SETUP":
            pwd = self.pwd_input.text()
            conf = self.confirm_input.text()
            if not pwd:
                QMessageBox.warning(self, "Error", "Password tidak boleh kosong!")
                return
            if pwd != conf:
                QMessageBox.warning(self, "Error", "Password dan Konfirmasi tidak cocok!")
                return
            
            salt = get_or_create_salt()
            with open(AUTH_FILE, "w") as f:
                f.write(hash_password(pwd, salt))
            
            self.user_password = pwd
            self.authenticated = True
            decrypt_and_mount_profile(pwd)
            self.accept()

        elif self.mode == "LOGIN":
            pwd = self.pwd_input.text()
            if not os.path.exists(AUTH_FILE) or not os.path.exists(SALT_FILE):
                self.reject()
                return
            
            with open(AUTH_FILE, "r") as f:
                saved_hash = f.read().strip()
            
            salt = get_or_create_salt()
            if hash_password(pwd, salt) == saved_hash:
                try:
                    decrypt_and_mount_profile(pwd)
                    self.user_password = pwd
                    self.authenticated = True
                    self.accept()
                except Exception:
                    QMessageBox.critical(self, "Error", "Gagal mendekripsi profile data!")
                    self.pwd_input.clear()
            else:
                QMessageBox.warning(self, "Error", "Password salah!")
                self.pwd_input.clear()

    def reset_all_data(self):
        if os.path.exists(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        self.mode = "SETUP"
        self.accept()

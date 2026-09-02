from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal

class UrlPopup(QDialog):
    url_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ketik URL atau pencarian (Ctrl+/)...")
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(35, 35, 45, 0.92);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
            }
        """)
        self.input.returnPressed.connect(self.submit)
        layout.addWidget(self.input)

    def show_centered(self, parent_widget):
        geo = parent_widget.geometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 3
        self.move(x, y)
        self.input.clear()
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()

    def submit(self):
        url = self.input.text().strip()
        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                if "." in url and " " not in url:
                    url = "https://" + url
                else:
                    url = "https://www.google.com/search?q=" + url
            self.url_submitted.emit(url)
        self.close()

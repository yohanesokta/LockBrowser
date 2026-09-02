from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QStyleOption, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from src.styles import TITLEBAR_STYLE

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titlebar")
        self.setFixedHeight(30)
        self.setStyleSheet(TITLEBAR_STYLE)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(8)
        
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.setStyleSheet("background-color: #ff5f56; border-radius: 6px;")
        self.close_btn.clicked.connect(self.parent.close)
        
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(12, 12)
        self.min_btn.setStyleSheet("background-color: #ffbd2e; border-radius: 6px;")
        self.min_btn.clicked.connect(self.parent.showMinimized)
        
        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(12, 12)
        self.max_btn.setStyleSheet("background-color: #27c93f; border-radius: 6px;")
        self.max_btn.clicked.connect(self.toggle_max_restore)
        
        self.layout.addWidget(self.close_btn)
        self.layout.addWidget(self.min_btn)
        self.layout.addWidget(self.max_btn)
        
        self.title = QLabel("Zen Browser")
        self.title.setStyleSheet("color: #888; font-size: 12px;")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.title)
        self.layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self._start_pos = None

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._start_pos is not None:
            delta = event.globalPosition().toPoint() - self._start_pos
            self.parent.move(self.parent.pos() + delta)
            self._start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._start_pos = None
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_max_restore()

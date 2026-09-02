from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QListWidget, QLabel, QListWidgetItem, QStyleOption, QStyle
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPainter
from src.styles import SIDEBAR_STYLE

class Sidebar(QWidget):
    url_submitted = Signal(str)
    nav_back = Signal()
    nav_forward = Signal()
    nav_reload = Signal()
    tab_changed = Signal(int)
    new_tab = Signal()
    close_tab = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLE)
        self.setFixedWidth(250)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(10)
        
        self.nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        self.back_btn.clicked.connect(self.nav_back.emit)
        self.forward_btn.clicked.connect(self.nav_forward.emit)
        self.reload_btn.clicked.connect(self.nav_reload.emit)
        self.nav_layout.addWidget(self.back_btn)
        self.nav_layout.addWidget(self.forward_btn)
        self.nav_layout.addWidget(self.reload_btn)
        self.layout.addLayout(self.nav_layout)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.on_url_submitted)
        self.layout.addWidget(self.url_bar)
        
        tab_header_layout = QHBoxLayout()
        tabs_label = QLabel("TABS")
        tabs_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(20, 20)
        self.new_tab_btn.clicked.connect(self.new_tab.emit)
        tab_header_layout.addWidget(tabs_label)
        tab_header_layout.addStretch()
        tab_header_layout.addWidget(self.new_tab_btn)
        self.layout.addLayout(tab_header_layout)
        
        self.tab_list = QListWidget()
        self.tab_list.currentRowChanged.connect(self.tab_changed.emit)
        self.layout.addWidget(self.tab_list)
        
        bookmarks_label = QLabel("BOOKMARKS")
        bookmarks_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
        self.layout.addWidget(bookmarks_label)
        
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setFixedHeight(120)
        self.bookmarks_list.addItem("Google")
        self.bookmarks_list.addItem("YouTube")
        self.bookmarks_list.addItem("WhatsApp Web")
        self.bookmarks_list.itemClicked.connect(self.on_bookmark_clicked)
        self.layout.addWidget(self.bookmarks_list)
        
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setStyleSheet("text-align: left;")
        self.layout.addWidget(self.settings_btn)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        
    def on_url_submitted(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = "https://www.google.com/search?q=" + url
        self.url_submitted.emit(url)
        
    def on_bookmark_clicked(self, item):
        if item.text() == "Google":
            self.url_submitted.emit("https://www.google.com")
        elif item.text() == "YouTube":
            self.url_submitted.emit("https://www.youtube.com")
        elif item.text() == "WhatsApp Web":
            self.url_submitted.emit("https://web.whatsapp.com")

    def update_tabs(self, tabs):
        self.tab_list.blockSignals(True)
        self.tab_list.clear()
        for i, tab in enumerate(tabs):
            item = QListWidgetItem(tab["title"])
            if tab.get("icon"):
                item.setIcon(QIcon(tab["icon"]))
            self.tab_list.addItem(item)
        self.tab_list.blockSignals(False)

    def set_current_tab(self, index):
        self.tab_list.blockSignals(True)
        self.tab_list.setCurrentRow(index)
        self.tab_list.blockSignals(False)

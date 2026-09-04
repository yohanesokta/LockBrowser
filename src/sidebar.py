from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QLabel, QListWidgetItem, QStyleOption, QStyle,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
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
    open_history = Signal()
    open_downloads = Signal()
    open_settings = Signal()

    FULL_WIDTH = 250
    COLLAPSED_WIDTH = 52
    HIDDEN_WIDTH = 6

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLE)

        self.is_pinned = True
        self.is_collapsed = False
        self._hover_active = False
        self.current_tabs_data = []
        self.setFixedWidth(self.FULL_WIDTH)
        self.setMouseTracking(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 8, 6, 8)
        self.layout.setSpacing(6)

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(4)

        self.toggle_btn = QPushButton()
        self.toggle_btn.setText("☰")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setStyleSheet("font-size: 16px;")
        self.toggle_btn.setToolTip("Collapse / Expand")
        self.toggle_btn.clicked.connect(self.toggle_collapse)

        self.pin_btn = QPushButton()
        self.pin_btn.setFixedSize(28, 28)
        self.pin_btn.setToolTip("Pin / Unpin Sidebar")
        self.pin_btn.clicked.connect(self.toggle_pin)
        self._update_pin_icon()

        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        for btn in (self.back_btn, self.forward_btn, self.reload_btn):
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("font-size: 14px;")

        self.back_btn.clicked.connect(self.nav_back.emit)
        self.forward_btn.clicked.connect(self.nav_forward.emit)
        self.reload_btn.clicked.connect(self.nav_reload.emit)

        self.header_layout.addWidget(self.toggle_btn)
        self.header_layout.addWidget(self.pin_btn)
        self.header_layout.addWidget(self.back_btn)
        self.header_layout.addWidget(self.forward_btn)
        self.header_layout.addWidget(self.reload_btn)
        self.header_layout.addStretch()
        self.layout.addLayout(self.header_layout)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.on_url_submitted)
        self.layout.addWidget(self.url_bar)

        self.tab_header_layout = QHBoxLayout()
        self.tab_header_layout.setContentsMargins(4, 0, 4, 0)
        self.tab_header_layout.setSpacing(4)
        self.tabs_label = QLabel("TABS")
        self.tabs_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.new_tab_btn.clicked.connect(self.new_tab.emit)

        self.tab_header_layout.addWidget(self.tabs_label)
        self.tab_header_layout.addStretch()
        self.tab_header_layout.addWidget(self.new_tab_btn)
        self.layout.addLayout(self.tab_header_layout)

        self.tab_list = QListWidget()
        self.tab_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_list.currentRowChanged.connect(self.tab_changed.emit)
        self.layout.addWidget(self.tab_list)

        self.bookmarks_label = QLabel("BOOKMARKS")
        self.bookmarks_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
        self.layout.addWidget(self.bookmarks_label)

        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bookmarks_list.setFixedHeight(90)
        self.bookmarks_list.addItem("Google")
        self.bookmarks_list.addItem("YouTube")
        self.bookmarks_list.addItem("WhatsApp Web")
        self.bookmarks_list.itemClicked.connect(self.on_bookmark_clicked)
        self.layout.addWidget(self.bookmarks_list)

        self.tools_label = QLabel("TOOLS & SETTINGS")
        self.tools_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px;")
        self.layout.addWidget(self.tools_label)

        self.history_btn = QPushButton("History")
        self.history_btn.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.history_btn.clicked.connect(self.open_history.emit)
        self.layout.addWidget(self.history_btn)

        self.downloads_btn = QPushButton("Downloads")
        self.downloads_btn.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.downloads_btn.clicked.connect(self.open_downloads.emit)
        self.layout.addWidget(self.downloads_btn)

        self.settings_btn = QPushButton("Password")
        self.settings_btn.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.settings_btn.clicked.connect(self.open_settings.emit)
        self.layout.addWidget(self.settings_btn)

        self._hide_timer = QTimer()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(400)
        self._hide_timer.timeout.connect(self._do_auto_hide)

    def _update_pin_icon(self):
        if self.is_pinned:
            self.pin_btn.setText("📌")
            self.pin_btn.setStyleSheet("font-size: 14px; border: none;")
        else:
            self.pin_btn.setText("📌")
            self.pin_btn.setStyleSheet("font-size: 14px; border: none; opacity: 0.5; color: #ff5f56;")

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self._update_pin_icon()
        if self.is_pinned:
            self._hide_timer.stop()
            self._hover_active = False
            self._apply_visual_state()
        else:
            if not self.underMouse():
                self._do_auto_hide()

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        self._apply_visual_state()

    def _apply_visual_state(self):
        if self.is_collapsed:
            self._show_collapsed()
        else:
            self._show_expanded()
        self._refresh_tab_list()

    def _show_expanded(self):
        self.setFixedWidth(self.FULL_WIDTH)
        self.layout.setContentsMargins(6, 8, 6, 8)

        for w in (self.toggle_btn, self.pin_btn, self.back_btn, self.forward_btn,
                  self.reload_btn, self.url_bar, self.tabs_label, self.new_tab_btn,
                  self.tab_list, self.bookmarks_label, self.bookmarks_list,
                  self.tools_label, self.history_btn, self.downloads_btn,
                  self.settings_btn):
            w.show()

        self.history_btn.setText("History")
        self.downloads_btn.setText("Downloads")
        self.settings_btn.setText("Password")
        self.history_btn.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.downloads_btn.setStyleSheet("text-align: left; padding: 4px 8px;")
        self.settings_btn.setStyleSheet("text-align: left; padding: 4px 8px;")

    def _show_collapsed(self):
        self.setFixedWidth(self.COLLAPSED_WIDTH)
        self.layout.setContentsMargins(4, 8, 4, 8)

        self.toggle_btn.show()
        self.pin_btn.show()
        self.new_tab_btn.show()
        self.tab_list.show()
        self.history_btn.show()
        self.downloads_btn.show()
        self.settings_btn.show()

        self.url_bar.hide()
        self.tabs_label.hide()
        self.bookmarks_label.hide()
        self.bookmarks_list.hide()
        self.tools_label.hide()
        self.back_btn.hide()
        self.forward_btn.hide()
        self.reload_btn.hide()

        self.history_btn.setText("H")
        self.downloads_btn.setText("D")
        self.settings_btn.setText("P")
        self.history_btn.setStyleSheet("text-align: center; padding: 4px;")
        self.downloads_btn.setStyleSheet("text-align: center; padding: 4px;")
        self.settings_btn.setStyleSheet("text-align: center; padding: 4px;")

    def _show_hidden_strip(self):
        self.setFixedWidth(self.HIDDEN_WIDTH)
        self.layout.setContentsMargins(0, 0, 0, 0)
        for w in (self.toggle_btn, self.pin_btn, self.back_btn, self.forward_btn,
                  self.reload_btn, self.url_bar, self.tabs_label, self.new_tab_btn,
                  self.tab_list, self.bookmarks_label, self.bookmarks_list,
                  self.tools_label, self.history_btn, self.downloads_btn,
                  self.settings_btn):
            w.hide()

    def _do_auto_hide(self):
        if not self.is_pinned and not self.underMouse():
            self._hover_active = False
            self._show_hidden_strip()

    def enterEvent(self, event):
        if not self.is_pinned:
            self._hide_timer.stop()
            self._hover_active = True
            self._apply_visual_state()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_pinned:
            self._hide_timer.start()
        super().leaveEvent(event)

    def _refresh_tab_list(self):
        self.update_tabs(self.current_tabs_data)

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
        self.current_tabs_data = tabs
        self.tab_list.blockSignals(True)
        self.tab_list.clear()
        for i, tab in enumerate(tabs):
            if self.is_collapsed:
                title = tab["title"][:2] if tab["title"] else "T"
            else:
                title = tab["title"]
            item = QListWidgetItem(title)
            if tab.get("icon"):
                item.setIcon(QIcon(tab["icon"]))
            self.tab_list.addItem(item)
        self.tab_list.blockSignals(False)

    def set_current_tab(self, index):
        self.tab_list.blockSignals(True)
        self.tab_list.setCurrentRow(index)
        self.tab_list.blockSignals(False)

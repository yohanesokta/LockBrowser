from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QApplication
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from src.titlebar import TitleBar
from src.sidebar import Sidebar
from src.tab_manager import TabManager
from src.styles import MAIN_STYLE
from src.url_popup import UrlPopup

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.resize(1024, 768)
        self.setStyleSheet(MAIN_STYLE)
        
        self.setMouseTracking(True)

        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setMouseTracking(True)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.titlebar = TitleBar(self)
        self.main_layout.addWidget(self.titlebar)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addLayout(self.content_layout)

        self.sidebar = Sidebar()
        self.content_layout.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        self.tab_manager = TabManager(self.stacked_widget)
        self.url_popup = UrlPopup(self)

        self.sidebar.url_submitted.connect(self.tab_manager.load_url)
        self.sidebar.nav_back.connect(self.tab_manager.back)
        self.sidebar.nav_forward.connect(self.tab_manager.forward)
        self.sidebar.nav_reload.connect(self.tab_manager.reload)
        self.sidebar.tab_changed.connect(self.tab_manager.set_current_tab)
        self.sidebar.new_tab.connect(self.tab_manager.add_tab)
        
        self.url_popup.url_submitted.connect(self.tab_manager.load_url)

        self.tab_manager.tabs_changed.connect(self.sidebar.update_tabs)
        self.tab_manager.current_tab_changed.connect(self.sidebar.set_current_tab)
        self.tab_manager.url_changed.connect(self.sidebar.url_bar.setText)

        self.tab_manager.add_tab()
        
        self.setup_shortcuts()
        
        self._resizing = False
        self._resize_edge = None
        self._margin = 5

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self, self.tab_manager.add_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.tab_manager.close_tab(self.stacked_widget.currentIndex()))
        QShortcut(QKeySequence("Ctrl+L"), self, self.sidebar.url_bar.setFocus)
        QShortcut(QKeySequence("Ctrl+R"), self, self.tab_manager.reload)
        QShortcut(QKeySequence("F5"), self, self.tab_manager.reload)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.prev_tab)
        QShortcut(QKeySequence("Alt+Left"), self, self.tab_manager.back)
        QShortcut(QKeySequence("Alt+Right"), self, self.tab_manager.forward)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        
        QShortcut(QKeySequence("Ctrl+/"), self, self.open_url_popup)
        QShortcut(QKeySequence("Ctrl+("), self, lambda: self.tab_manager.split_current_tab(Qt.Horizontal))
        QShortcut(QKeySequence("Ctrl+)"), self, lambda: self.tab_manager.split_current_tab(Qt.Vertical))

        for i in range(1, 10):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, lambda idx=i-1: self.tab_manager.set_current_tab(idx))

    def open_url_popup(self):
        self.url_popup.show_centered(self)

    def next_tab(self):
        count = self.stacked_widget.count()
        if count > 1:
            idx = (self.stacked_widget.currentIndex() + 1) % count
            self.tab_manager.set_current_tab(idx)

    def prev_tab(self):
        count = self.stacked_widget.count()
        if count > 1:
            idx = (self.stacked_widget.currentIndex() - 1) % count
            self.tab_manager.set_current_tab(idx)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def get_edge(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = self._margin
        edge = 0
        if x < m: edge |= 1 
        elif x > w - m: edge |= 2 
        if y < m: edge |= 4 
        elif y > h - m: edge |= 8 
        return edge

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self.get_edge(event.pos())
            if edge:
                self._resizing = True
                self._resize_edge = edge
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            rect = self.geometry()
            pos = event.globalPosition().toPoint()
            if self._resize_edge & 1: rect.setLeft(pos.x())
            if self._resize_edge & 2: rect.setRight(pos.x())
            if self._resize_edge & 4: rect.setTop(pos.y())
            if self._resize_edge & 8: rect.setBottom(pos.y())
            self.setGeometry(rect)
            event.accept()
            return
            
        edge = self.get_edge(event.pos())
        if edge == 1 or edge == 2: self.setCursor(Qt.SizeHorCursor)
        elif edge == 4 or edge == 8: self.setCursor(Qt.SizeVerCursor)
        elif edge == 5 or edge == 10: self.setCursor(Qt.SizeFDiagCursor)
        elif edge == 9 or edge == 6: self.setCursor(Qt.SizeBDiagCursor)
        else: self.setCursor(Qt.ArrowCursor)
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_edge = None
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

from PySide6.QtWidgets import QStackedWidget, QSplitter
from PySide6.QtCore import QUrl, Signal, QObject, Qt
from src.webview import WebView

class TabManager(QObject):
    tabs_changed = Signal(list)
    current_tab_changed = Signal(int)
    url_changed = Signal(str)

    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked = stacked_widget
        self.tabs = []
        self.stacked.currentChanged.connect(self.on_stacked_changed)

    def add_tab(self, url="https://www.google.com"):
        view = WebView()
        view.setUrl(QUrl(url))
        
        tab_container = QSplitter(Qt.Horizontal)
        tab_container.setChildrenCollapsible(False)
        tab_container.addWidget(view)

        tab_data = {
            "container": tab_container,
            "views": [view],
            "active_view": view
        }
        self.tabs.append(tab_data)

        self.stacked.addWidget(tab_container)
        self.stacked.setCurrentWidget(tab_container)

        self._connect_view_signals(view)

        self.emit_tabs_changed()
        return len(self.tabs) - 1

    def _connect_view_signals(self, view):
        view.urlChanged.connect(self.on_view_url_changed)
        view.titleChanged.connect(self.on_view_title_changed)
        view.iconChanged.connect(self.on_view_icon_changed)

    def close_tab(self, index):
        if 0 <= index < len(self.tabs):
            tab_data = self.tabs.pop(index)
            container = tab_data["container"]
            self.stacked.removeWidget(container)
            container.deleteLater()
            self.emit_tabs_changed()
            if not self.tabs:
                self.add_tab()

    def set_current_tab(self, index):
        if 0 <= index < len(self.tabs):
            self.stacked.setCurrentIndex(index)

    def get_current_tab_data(self):
        index = self.stacked.currentIndex()
        if 0 <= index < len(self.tabs):
            return self.tabs[index]
        return None

    def get_current_view(self):
        tab_data = self.get_current_tab_data()
        if tab_data:
            return tab_data["active_view"]
        return None

    def split_current_tab(self, orientation):
        tab_data = self.get_current_tab_data()
        if not tab_data:
            return
        
        container = tab_data["container"]
        
        if container.count() == 1:
            container.setOrientation(orientation)
            new_view = WebView()
            new_view.setUrl(QUrl("https://www.google.com"))
            container.addWidget(new_view)
            tab_data["views"].append(new_view)
            tab_data["active_view"] = new_view
            self._connect_view_signals(new_view)
            self.url_changed.emit(new_view.url().toString())
        else:
            if container.orientation() == orientation:
                view_to_remove = tab_data["views"].pop()
                view_to_remove.deleteLater()
                tab_data["active_view"] = tab_data["views"][0]
                self.url_changed.emit(tab_data["active_view"].url().toString())
            else:
                container.setOrientation(orientation)

    def on_stacked_changed(self, index):
        self.current_tab_changed.emit(index)
        view = self.get_current_view()
        if view:
            self.url_changed.emit(view.url().toString())

    def on_view_url_changed(self, url):
        view = self.sender()
        if view == self.get_current_view():
            self.url_changed.emit(url.toString())

    def on_view_title_changed(self, title):
        self.emit_tabs_changed()

    def on_view_icon_changed(self, icon):
        self.emit_tabs_changed()

    def emit_tabs_changed(self):
        result = []
        for tab in self.tabs:
            v = tab["views"][0]
            result.append({
                "title": v.title() or "New Tab",
                "icon": v.icon()
            })
        self.tabs_changed.emit(result)

    def load_url(self, url):
        view = self.get_current_view()
        if view:
            view.setUrl(QUrl(url))

    def back(self):
        view = self.get_current_view()
        if view:
            view.back()

    def forward(self):
        view = self.get_current_view()
        if view:
            view.forward()

    def reload(self):
        view = self.get_current_view()
        if view:
            view.reload()

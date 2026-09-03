import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from src.crypto_utils import get_runtime_profile_dir

CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

_persistent_profile = None

def get_persistent_profile():
    global _persistent_profile
    if _persistent_profile is None:
        profile_dir = get_runtime_profile_dir()
        os.makedirs(profile_dir, exist_ok=True)
        _persistent_profile = QWebEngineProfile("MyChromeProfile", None)
        _persistent_profile.setPersistentStoragePath(profile_dir)
        _persistent_profile.setCachePath(os.path.join(profile_dir, "cache"))
        _persistent_profile.setHttpUserAgent(CHROME_UA)
        
        s = _persistent_profile.settings()
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        s.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
        
    return _persistent_profile

class WebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        profile = get_persistent_profile()
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        
        self.setUrl(QUrl("https://www.google.com"))

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #23222a;
                color: #e0e0e0;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        
        menu.addSeparator()
        inspect_action = QAction("Inspect Element", self)
        inspect_action.triggered.connect(self.inspect_element)
        menu.addAction(inspect_action)
        
        menu.exec_(event.globalPos())

    def inspect_element(self):
        self.page().triggerAction(QWebEnginePage.InspectElement)

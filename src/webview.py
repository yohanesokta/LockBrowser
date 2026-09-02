from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtCore import QUrl

CHROME_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

class WebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(CHROME_USER_AGENT)
        
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        
        self.setUrl(QUrl("https://www.google.com"))

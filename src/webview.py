import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings, QWebEngineScript
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from src.crypto_utils import get_runtime_profile_dir

CHROME_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# JavaScript to spoof navigator properties so Google doesn't detect embedded browser
SPOOF_JS = """
(function() {
    // Override userAgentData to mimic real Chrome
    if (navigator.userAgentData === undefined || navigator.userAgentData) {
        Object.defineProperty(navigator, 'userAgentData', {
            get: function() {
                return {
                    brands: [
                        {brand: "Google Chrome", version: "131"},
                        {brand: "Chromium", version: "131"},
                        {brand: "Not_A Brand", version: "24"}
                    ],
                    mobile: false,
                    platform: "Linux",
                    getHighEntropyValues: function(hints) {
                        return Promise.resolve({
                            brands: this.brands,
                            mobile: false,
                            platform: "Linux",
                            platformVersion: "6.8.0",
                            architecture: "x86",
                            bitness: "64",
                            model: "",
                            uaFullVersion: "131.0.0.0",
                            fullVersionList: this.brands
                        });
                    }
                };
            }
        });
    }
    // Remove webdriver flag
    Object.defineProperty(navigator, 'webdriver', {get: () => false});
})();
"""

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

        # Inject spoof script on every page load
        script = QWebEngineScript()
        script.setName("SpoofNavigator")
        script.setSourceCode(SPOOF_JS)
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(True)
        _persistent_profile.scripts().insert(script)
        
    return _persistent_profile

class WebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        profile = get_persistent_profile()
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        
        self.setUrl(QUrl("https://www.google.com"))

    def createWindow(self, window_type):
        """Handle popup windows (needed for Google login flow)."""
        new_view = WebView()
        new_view.setAttribute(5, True)  # WA_DeleteOnClose
        new_view.setWindowTitle("Login")
        new_view.resize(800, 600)
        new_view.show()
        return new_view

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

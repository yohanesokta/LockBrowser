MAIN_STYLE = """
QMainWindow {
    background-color: #1e1e24;
}
QWidget#central_widget {
    background-color: #1e1e24;
}
QWidget {
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.1);
}
QLineEdit {
    background-color: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 6px 10px;
    color: white;
}
QLineEdit:focus {
    border: 1px solid rgba(255, 255, 255, 0.35);
}
QListWidget {
    background-color: transparent;
    border: none;
}
QListWidget::item {
    padding: 6px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.15);
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.08);
}
QScrollBar:horizontal {
    height: 0px;
    background: transparent;
}
QScrollBar:vertical {
    width: 4px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QSplitter::handle {
    background-color: rgba(255, 255, 255, 0.1);
    margin: 2px;
}
QSplitter::handle:hover {
    background-color: rgba(255, 255, 255, 0.3);
}
QProgressBar#loading_bar {
    background-color: transparent;
    border: none;
}
QProgressBar#loading_bar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ff5f56,
        stop:0.5 #ffbd2e,
        stop:1 #27c93f);
    border-radius: 1px;
}
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3c2a21,
        stop:0.4 #251d28,
        stop:1 #141419);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
"""

TITLEBAR_STYLE = """
QWidget#titlebar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3c2a21,
        stop:0.3 #251d28,
        stop:1 #141419);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
"""

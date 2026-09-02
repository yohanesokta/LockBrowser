import sys
from PySide6.QtWidgets import QApplication
from src.browser import Browser

def main():
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

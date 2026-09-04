import sys
import os
from PySide6.QtWidgets import QApplication, QDialog
from src.crypto_utils import check_auth_integrity, encrypt_and_unmount_profile
from src.auth import AuthDialog

def main():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-features=CrossOriginOpenerPolicyReporting"
        ",SameSiteByDefaultCookies"
        ",CookiesWithoutSameSiteMustBeSecure"
        " --disable-site-isolation-trials"
        " --allow-running-insecure-content"
    )
    app = QApplication(sys.argv)
    
    status = check_auth_integrity()
    auth_dialog = AuthDialog(mode=status)
    
    if auth_dialog.exec() == QDialog.Accepted and auth_dialog.authenticated:
        user_password = auth_dialog.user_password
        from src.browser import Browser
        window = Browser()
        window.show()
        
        exit_code = app.exec()
        
        if user_password:
            encrypt_and_unmount_profile(user_password)
            
        sys.exit(exit_code)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

   

import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from client.network_client import NetworkClient
from client.ui.login_window import LoginWindow


def load_stylesheet():
    theme_path = os.path.join(
        os.path.dirname(__file__),
        "ui",
        "assets",
        "styles",
        "theme.qss"
    )

    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as file:
            return file.read()
    return ""


def run_client_app():
    app = QApplication(sys.argv)
    app.setApplicationName("TalkNest")

    # icon load (optional)
    logo_path = os.path.join(
        os.path.dirname(__file__),
        "ui",
        "assets",
        "logo.png"
    )
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    # stylesheet load
    app.setStyleSheet(load_stylesheet())

    # create client + login window
    network_client = NetworkClient()
    login_window = LoginWindow(network_client)

    # 🔥 direct show (NO splash)
    login_window.show()
    login_window.raise_()
    login_window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_client_app()
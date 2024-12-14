import sys,os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,
    QSystemTrayIcon,QMenu,QAction
)
from PyQt5.QtGui import QFont,QIcon
from PyQt5.QtCore import Qt
from workers.server import FileSharingServer
from workers.helper import getSystem_IpAdd


class FileShareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laner")
        self.setGeometry(100, 100, 500, 500)
        self.server_thread = None
        # self.server = None
        self.running = False
        self.hidden_ip = False
        self.ip = None

        # Main Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Title Label
        self.title_label = QLabel("Laner")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: rgb(0, 179, 153);")
        self.layout.addWidget(self.title_label)

        # Subtitle Label
        self.subtitle_label = QLabel("Fast and Secure File Sharing over LAN")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setFont(QFont("Arial", 16))
        self.subtitle_label.setStyleSheet("color: gray;")
        self.layout.addWidget(self.subtitle_label)

        # Hint Message Label
        self.hint_message = QLabel("Connect your PC to your HotSpot\nand Press Start to get the code")
        self.hint_message.setAlignment(Qt.AlignCenter)
        self.hint_message.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.hint_message)

        # Start Button
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setFixedSize(120, 40)
        self.start_button.setStyleSheet("background-color: white; color: rgb(0, 179, 153);")
        self.layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Status Label
        self.status_label = QLabel("Server not running")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        self.layout.addWidget(self.status_label)

        # Hide IP Button
        self.hide_ip_button = QPushButton("Hide Code")
        self.hide_ip_button.clicked.connect(self.hide_ip)
        self.hide_ip_button.setFixedSize(100, 40)
        self.hide_ip_button.setStyleSheet("background-color: white; color: rgb(0, 179, 153);")
        self.hide_ip_button.setVisible(False)
        self.layout.addWidget(self.hide_ip_button, alignment=Qt.AlignRight)
        
        # System Tray
        self.create_system_tray()

    def create_system_tray(self):
        self.tray = QSystemTrayIcon(self)
        
        icon_path = "icon.png"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "assets", "imgs", "icon.png")
        
        self.tray.setIcon(QIcon(icon_path))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def start_server(self):
        if self.running:
            self.status_label.setText("Server is already running! Don't share the code.")
            self.on_stop()
            return

        self.ip = getSystem_IpAdd()
        if self.ip is None:
            self.hint_message.setText("Connect your PC to your Local Network.\nNo need for Internet Capability.")
            self.hint_message.setStyleSheet("color: black;")
            return
        else:
            self.hint_message.setText("Hidden Code" if self.hidden_ip else self.ip)
            self.hint_message.setStyleSheet("color: gray;")

        # Start the server in a separate thread
        port = 8000
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True

        self.hide_ip_button.setVisible(True)
        self.start_button.setText("End Server")
        self.status_label.setText("Server Running. Don't share the code.\nWrite the exact code in the Link Tab on Your Phone.")

    def run_server(self, port):
        # Initialize the server
        self.server = FileSharingServer(port, '/')
        try:
            # Start the server
            self.server.start()
            print("Press Ctrl+C to stop the server.")
        except KeyboardInterrupt:
            # Stop the server on Ctrl+C
            print("\nStopping the server...")
            self.server.stop()

    def on_stop(self):
        self.hint_message.setText("Goodbye!")
        self.running = False
        self.start_button.setText("Start Server")
        self.status_label.setText("Server Ended!")
        self.hide_ip_button.setVisible(False)

        # Stop the server
        if self.server_thread:
            self.server_thread.join()
            self.server.stop()

    def hide_ip(self):
        if not self.running:
            return

        if not self.hidden_ip:
            self.hint_message.setText("Hidden Code")
            self.hide_ip_button.setText("Show Code")
        else:
            self.hint_message.setText(self.ip)
            self.hide_ip_button.setText("Hide Code")

        self.hidden_ip = not self.hidden_ip


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileShareApp()
    window.show()
    # app.exec_()
    sys.exit(app.exec_())

import sys, os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,QHBoxLayout,
    QSystemTrayIcon, QMenu, QAction, QDialog, QFormLayout, QLineEdit, QStackedWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from workers.server import FileSharingServer
from workers.helper import getSystem_IpAdd


class SettingsScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # Back Button at the top left corner
        back_button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setFixedSize(70, 30)
        self.back_button.setStyleSheet("background-color: white; color: rgb(0, 179, 153);")
        # self.back_button.setStyleSheet("background-color: rgb(0, 179, 153); color: white;")
        back_button_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        layout.addLayout(back_button_layout)

        title_label = QLabel("Settings")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: rgb(0, 179, 153);")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 10, 20, 10)

        # Create and style port title label
        port_title = QLabel("Port:")
        port_title.setFont(QFont("Arial", 18))
        port_title.setStyleSheet("color: gray;")
        port_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Create and style port value label
        self.port_label = QLabel(self.parent.port if self.parent.port else "Server not running")
        self.port_label.setFont(QFont("Arial", 18))
        self.port_label.setStyleSheet("color: gray;")
        self.port_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add both to form layout
        form_layout.addRow(port_title, self.port_label)

        layout.addLayout(form_layout)

        self.setLayout(layout)

    def go_back(self):
        self.parent.stacked_widget.setCurrentWidget(self.parent.main_screen)
class MainScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel("Laner")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: rgb(0, 179, 153);")
        self.main_layout.addWidget(self.title_label)

        # Subtitle Label
        self.subtitle_label = QLabel("Fast and Secure File Sharing over LAN")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setFont(QFont("Arial", 16))
        self.subtitle_label.setStyleSheet("color: gray;")
        self.main_layout.addWidget(self.subtitle_label)

        # Hint Message Label
        self.hint_message = QLabel("Connect your PC to your HotSpot\nand Press Start to get the code")
        self.hint_message.setAlignment(Qt.AlignCenter)
        self.hint_message.setFont(QFont("Arial", 20))
        self.main_layout.addWidget(self.hint_message)

        # Start Button
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.parent.start_server)
        self.start_button.setFixedSize(120, 40)
        self.start_button.setStyleSheet("background-color: white; color: rgb(0, 179, 153);")
        self.main_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Status Label
        self.status_label = QLabel("Server not running")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        self.main_layout.addWidget(self.status_label)

        # Hide IP Button
        self.hide_ip_button = QPushButton("Hide Code")
        self.hide_ip_button.clicked.connect(self.parent.hide_ip)
        self.hide_ip_button.setFixedSize(100, 40)
        self.hide_ip_button.setStyleSheet("background-color: white; color: rgb(0, 179, 153);")
        self.hide_ip_button.setVisible(False)
        self.main_layout.addWidget(self.hide_ip_button, alignment=Qt.AlignRight)

        # Settings Button
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("assets/imgs/icon.png"))  # Add settings Icon
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(40, 40)
        # self.settings_button.setStyleSheet("background-color: transparent;")
        self.settings_button.clicked.connect(self.parent.open_settings)
        self.main_layout.addWidget(self.settings_button, alignment=Qt.AlignRight)


class FileShareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laner")
        self.setGeometry(100, 100, 500, 500)
        self.server_thread = None
        self.running = False
        self.hidden_ip = False
        self.ip = None
        self.port = None

        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Main Screen
        self.main_screen = MainScreen(self)
        self.stacked_widget.addWidget(self.main_screen)

        # Settings Screen
        self.settings_screen = SettingsScreen(self)
        self.stacked_widget.addWidget(self.settings_screen)

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
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def start_server(self):
        if self.running:
            self.main_screen.status_label.setText("Server is already running! Don't share the code.")
            self.on_stop()
            return

        self.ip = getSystem_IpAdd()
        if self.ip is None:
            self.main_screen.hint_message.setText("Connect your PC to your Local Network.\nNo need for Internet Capability.")
            self.main_screen.hint_message.setStyleSheet("color: black;")
            self.main_screen.hint_message.setFont(QFont("Arial", 20))

            return
        else:
            self.main_screen.hint_message.setText("Hidden Code" if self.hidden_ip else self.ip)
            self.main_screen.hint_message.setStyleSheet("color: gray;")

        # Start the server in a separate thread
        port = 8000
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        self.main_screen.hint_message.setFont(QFont("Arial", 34))

        self.main_screen.hide_ip_button.setVisible(True)
        self.main_screen.start_button.setText("End Server")
        self.main_screen.status_label.setText("Server Running. Don't share the code.\nWrite the exact code in the Link Tab on Your Phone.")

    def run_server(self, port):
        # Initialize the server
        self.server = FileSharingServer(port, '/')
        try:
            # Start the server
            self.server.start()
            self.port=self.server.getPortNumer()
            self.settings_screen.port_label.setText(str(self.port))
            
            print("Press Ctrl+C to stop the server.")
        except KeyboardInterrupt:
            # Stop the server on Ctrl+C
            print("\nStopping the server...")
            self.server.stop()

    def on_stop(self):
        self.main_screen.hint_message.setText("Goodbye!")

        self.running = False
        self.main_screen.start_button.setText("Start Server")
        self.main_screen.status_label.setText("Server Ended!")
        self.main_screen.hide_ip_button.setVisible(False)

        # Stop the server
        if self.server_thread:
            self.server_thread.join()
            self.server.stop()

    def hide_ip(self):
        if not self.running:
            return

        if not self.hidden_ip:
            self.main_screen.hint_message.setText("Hidden Code")
            self.main_screen.hide_ip_button.setText("Show Code")
        else:
            self.main_screen.hint_message.setText(self.ip)
            self.main_screen.hide_ip_button.setText("Hide Code")

        self.hidden_ip = not self.hidden_ip

    def open_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_screen)

    def closeEvent(self, event):
        print('peek', event)
        self.hide()
        event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileShareApp()
    window.show()
    # app.exec_()
    sys.exit(app.exec_())

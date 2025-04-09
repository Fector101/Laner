from PyQt5.QtWidgets import QWidget,QVBoxLayout,QLabel,QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont,QIcon
from workers.helper import  getAbsPath

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
        # TODO bind to end when server start works
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
        settings_icon=getAbsPath('assets','imgs','icon.png')
        self.settings_button.setIcon(QIcon(settings_icon))  # Add settings Icon
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(40, 40)
        # self.settings_button.setStyleSheet("background-color: transparent;")
        self.settings_button.clicked.connect(self.parent.open_settings)
        self.main_layout.addWidget(self.settings_button, alignment=Qt.AlignRight)

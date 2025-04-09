from PyQt5.QtWidgets import QWidget,QVBoxLayout,QLabel,QPushButton,QHBoxLayout, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from workers.helper import getUserPCName

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
        ip_title = QLabel("Server ip:")
        ip_title.setFont(QFont("Arial", 18))
        ip_title.setStyleSheet("color: gray;")
        ip_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Create and style port value label
        # self.port_label = QSpinBox()
        # self.port_label.setRange(0,30000)
        # self.port_label.setValue(8000)
        self.ip_label = QLabel(self.parent.port if self.parent.port else "Server not running")

        self.ip_label.setFont(QFont("Arial", 18))
        self.ip_label.setStyleSheet("color: gray;")
        self.ip_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Create and style User name
        
        user_title = QLabel("User:")
        user_title.setFont(QFont("Arial", 18))
        user_title.setStyleSheet("color: gray;")
        user_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.username_label = QLabel(getUserPCName())
        self.username_label.setFont(QFont("Arial", 18))
        self.username_label.setStyleSheet("color: gray;")
        self.username_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add both to form layout
        form_layout.addRow(user_title,self.username_label)
        form_layout.addRow(ip_title, self.ip_label)

        layout.addLayout(form_layout)

        self.setLayout(layout)

    def go_back(self):
        self.parent.stacked_widget.setCurrentWidget(self.parent.main_screen)

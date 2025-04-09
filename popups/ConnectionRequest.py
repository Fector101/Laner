import asyncio
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QLabel,QHBoxLayout,QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ConnectionRequest(QWidget):
    def __init__(self, device_name, websocket, event_loop):
        super().__init__()
        self.websocket = websocket
        self.event_loop = event_loop
        
        self.setWindowTitle("Incoming Connection Request")
        self.setFixedSize(350, 450)
        self.setStyleSheet("""
            background-color: #F8FAFC;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Incoming Connection Request")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        # title.setStyleSheet("color: #1E293B;")

        # Subtitle
        subtitle = QLabel("A mobile device is trying to connect to your PC")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; font-size: 12px;")

        # Device Icon
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        icon_label = QLabel()
        icon_label.setFixedSize(80, 80)
        icon_label.setStyleSheet("""
            background-color: #E0F2FE;
            border-radius: 40px;
            border: 2px solid #BAE6FD;
        """)
        icon_layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # Device Name
        device_label = QLabel(device_name)
        device_label.setObjectName("device_name")
        device_label.setFont(QFont("Arial", 12, QFont.Bold))
        device_label.setAlignment(Qt.AlignCenter)
        device_label.setStyleSheet("color: #1E293B; margin-top: 10px;")

        # Connection Message
        connection_msg = QLabel("Wants to connect to this device")
        connection_msg.setAlignment(Qt.AlignCenter)
        connection_msg.setStyleSheet("color: #64748B; font-size: 12px;")

        # Buttons
        button_layout = QHBoxLayout()
        
        reject_btn = QPushButton("✗ Reject")
        reject_btn.setObjectName("reject_btn")
        reject_btn.setFixedSize(120, 40)
        reject_btn.setStyleSheet("""
            QPushButton {
                color: #DC2626;
                border: 2px solid #DC2626;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
            }
        """)

        accept_btn = QPushButton("✔ Accept")
        accept_btn.setObjectName("accept_btn")
        accept_btn.setFixedSize(120, 40)
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        button_layout.addWidget(reject_btn)
        button_layout.addWidget(accept_btn)

        # Footer
        footer = QLabel("Only accept connection requests from devices you trust")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #94A3B8; font-size: 10px; margin-top: 20px;")

        # Assemble layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(icon_container)
        layout.addWidget(device_label)
        layout.addWidget(connection_msg)
        layout.addLayout(button_layout)
        layout.addWidget(footer)

        self.setLayout(layout)

        # Connect buttons
        accept_btn.clicked.connect(self.accept_connection)
        reject_btn.clicked.connect(self.reject_connection)
        
        # Window flags to keep on top
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        # self.setWindowModality(Qt.ApplicationModal)

    def accept_connection(self):
        asyncio.run_coroutine_threadsafe(
            self.websocket.send("ACCESS_GRANTED"),
            self.event_loop
        )
        self.close()

    def reject_connection(self):
        asyncio.run_coroutine_threadsafe(
            self.websocket.send("ACCESS_DENIED"),
            self.event_loop
        )
        self.close()

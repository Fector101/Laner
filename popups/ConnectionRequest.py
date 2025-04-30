import asyncio
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt,QEventLoop
from PyQt5.QtGui import QFont
from workers.web_socket import WebSocketConnectionHandler

# Add Don't show again for this device and then i settings add said device with a checkbox to off/on incoming requests
class ConnectionRequest(QWidget):
    def __init__(self,handler,message_object={'name':'','request':''},parent=None):
        super().__init__(parent)
        self.handler: WebSocketConnectionHandler = handler
        device_name = message_object['name']
        # request = message_object['request'] use in upcoming in-app terminal
        self._made_choice = False
        self.setWindowTitle("Incoming Connection Request")
        self.setFixedSize(350, 450)
        self.setStyleSheet("""
            background-color: #F8FAFC;
        """)
        
        # border-radius: 10px;
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        self.title = QLabel("Incoming Connection Request")
        self.title.setFont(QFont("Arial", 14, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        # Subtitle
        self.subtitle = QLabel("A mobile device is trying to connect to your PC")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: #64748B; font-size: 12px;")

        # Device Icon
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setStyleSheet("""
            background-color: #E0F2FE;
            border-radius: 40px;
            border: 2px solid #BAE6FD;
        """)
        icon_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Device Name
        self.device_label = QLabel(device_name)
        self.device_label.setObjectName("device_name")
        self.device_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.device_label.setAlignment(Qt.AlignCenter)
        self.device_label.setStyleSheet("color: #1E293B; margin-top: 10px;")

        # Connection Message
        self.connection_msg = QLabel("Wants to connect to this device")
        self.connection_msg.setAlignment(Qt.AlignCenter)
        self.connection_msg.setStyleSheet("color: #64748B; font-size: 12px;")

        # Buttons
        button_layout = QHBoxLayout()
        
        self.reject_btn = QPushButton("✗ Reject")
        self.reject_btn.setObjectName("reject_btn")
        self.reject_btn.setFixedSize(120, 40)
        self.reject_btn.setStyleSheet("""
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

        self.accept_btn = QPushButton("✔ Accept")
        self.accept_btn.setObjectName("accept_btn")
        self.accept_btn.setFixedSize(120, 40)
        self.accept_btn.setStyleSheet("""
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

        button_layout.addWidget(self.reject_btn)
        button_layout.addWidget(self.accept_btn)

        # Footer
        self.footer = QLabel("Only accept connection requests from devices you trust")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #94A3B8; font-size: 10px; margin-top: 20px;")

        # Assemble layout
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(icon_container)
        layout.addWidget(self.device_label)
        layout.addWidget(self.connection_msg)
        layout.addLayout(button_layout)
        layout.addWidget(self.footer)

        self.setLayout(layout)

        # Connect buttons
        self.accept_btn.clicked.connect(self.accept_connection)
        self.reject_btn.clicked.connect(self.reject_connection)
        # Window flags to keep on top
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

    # def show_request(self, device_name, websocket, event_loop):
    # def show_request(self, handler: WebSocketConnectionHandler, message_object={'name':'','request':''}):
    #     """Show the widget with new connection details"""
        # self.handler = handler
        # self.websocket = websocket
        # self.event_loop = event_loop
        # device_name = message_object['name']
        # request = message_object['request']
        # self.device_label.setText(device_name)
        # self.show()

    # def hide_request(self):
    #     """Hide the widget"""
    #     self.hide()
    def closeEvent(self, event):
        """
            For When User Closes Popup Without Choosing 'Yes' or 'No'
        """
        if not self._made_choice:
            self._made_choice=True
            # `accept_connection` and `reject_connection` method till call close, this will help
            self.reject_connection()
        self.hide()
        event.ignore()
    def accept_connection(self):
        """Handle accept connection"""
        self._made_choice = True
        if self.handler:
            loop = QEventLoop()
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(self.handler.accept())
            # asyncio.run_coroutine_threadsafe(self._send_response(True), self.event_loop)
        # self.hide_request()
        self.close()

    def reject_connection(self):
        """Handle reject connection"""
        self._made_choice = True
        if self.handler:
            loop = QEventLoop()
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(self.handler.reject())
            # asyncio.run_coroutine_threadsafe(self._send_response(False), self.event_loop)
        # self.hide_request()
        self.close()

    # async def _send_response(self, accepted):
    #     """Send response to websocket"""
    #     if self.websocket:
    #         response = "accept" if accepted else "reject"
    #         await self.websocket.send(response)

# Window flags to keep on top
# self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
# self.setWindowModality(Qt.ApplicationModal)

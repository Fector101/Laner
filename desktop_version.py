# from kivy.lang import Builder
# from kivymd.app import MDApp
# from kivy.core.window import Window
# import kivymd.icon_definitions
# from kivy.config import Config
# import time
# import os
# import sys
# import threading
# # import platform

# from workers.server import FileSharingServer
# from workers.helper import getSystem_IpAdd



# Window.size = (500, 500)


# KV = '''
# #:set THEME_COLOR_TUPLE (0, .7, .6, 1)
# MDBoxLayout:
#     orientation: "vertical"
#     padding: dp(10)
#     md_bg_color: (.95,.95,.95,1)

#     MDLabel:
#         text: "Laner"
#         halign: "center"
#         text_color: THEME_COLOR_TUPLE
#         theme_font_size: "Custom"
#         font_size: '60sp'
        
#     MDLabel:
#         text: "Fast and Secure File Sharing over LAN"
#         halign: "center"
#         text_color: (.5,.5,.5,1)
#         theme_font_size: "Custom"
#         font_size: '20sp'
        
#     MDLabel:
#         id: hint_message
#         text: 'Connect your PC to your HotSpot\\n and Press start to get code'
#         theme_font_size: "Custom"
#         font_size: '20sp'
#         halign: "center"


#     MDButton:
#         pos_hint: {"center_x": .5}
#         on_release: app.start_server()
#         theme_text_color: "Custom"
#         theme_bg_color: "Custom"
#         theme_width:  "Custom"
#         theme_height:  "Custom"
#         size_hint:[None,None]
#         size:[sp(120),dp(40)]
        
#         MDButtonText:
#             id: start_button_id
#             color: THEME_COLOR_TUPLE
#             text: "Start Server"
#             pos_hint: {"center_x": .5,"center_y": .5}
        

#     MDLabel:
#         id: status_label
#         text: "Server not running"
#         halign: "center"
#         theme_text_color: "Hint"

#     MDButton:
#         id: hide_ip_btn_id
#         pos_hint: {"right": 1}
#         on_release: app.hide_ip()
#         theme_text_color: "Custom"
#         theme_bg_color: "Custom"
#         radius: 3
#         opacity:0
#         theme_width:  "Custom"
#         theme_height:  "Custom"
#         size_hint:[None,None]
#         size:[sp(100),dp(40)]
#         MDButtonText:
#             id: hide_ip_label_id
#             color: THEME_COLOR_TUPLE
#             text: "Hide Code"
#             pos_hint: {"center_x": .5,"center_y": .5}

# '''

# class FileShareApp(MDApp):
#     def build(self):
#         icon_path="icon.png"
#         # print(os.getcwd(),'----||||----')
#         # application_folder = os.path.dirname(__file__)
#         #__file__ OR os.path.abspath(__file__) both gives absolute path
#         # os.path.dirname(__file__) OR sys._MEIPASS both give temp folder path
#         # os.path.dirname(__file__) is better since it work in develepoment when app is not packaged
        
#         if hasattr(sys, "_MEIPASS"):
#             icon_path=os.path.join(sys._MEIPASS,"assets","imgs","icon.png") 
#         self.icon=icon_path
#         self.title="Laner"        
#         self.server_thread = None
#         self.running = False
#         self.hidden_ip = False
#         self.ip = None
#         try:
#             return Builder.load_string(KV)
#         except:
#             time.sleep(200)
#     def start_server(self):
        
#         if self.running:
#             self.root.ids.status_label.text = "Server is already running! don't share code"
#             self.on_stop()
#             return
        
#         self.ip=getSystem_IpAdd()
#         if self.ip == None:
#             self.root.ids.hint_message.text = "Connect your PC to your Local Network,\n No need for Internet Capability"
#             self.root.ids.hint_message.font_style="Body"
#             self.root.ids.hint_message.theme_font_size="Custom"
#             self.root.ids.hint_message.font_size='20sp'
#             self.root.ids.hint_message.text_color=(0,0,0,1)
#             return
#         else:
#             self.root.ids.hint_message.text = "Hidden Code" if self.hidden_ip else self.ip
#             self.root.ids.hint_message.font_style="Display"
#             self.root.ids.hint_message.theme_font_size= "Primary"
#             self.root.ids.hint_message.text_color=(.67,.67,.67,1)




#         # TODO Get port from input or use default OR run loop and return use and log found port
#         port = 8000
#         # Start the HTTP server in a separate thread
#         self.server_thread = threading.Thread(target=self.run_server, args=(port,))
#         self.server_thread.daemon = True
#         self.server_thread.start()
#         self.running = True
        
        
#         self.root.ids.hide_ip_btn_id.opacity = 1
#         self.root.ids.start_button_id.text = "End Server"
#         self.root.ids.status_label.text = "Server Running don't share code\n Write Extact Code in Link Tab on Your Phone"
        
        
#     def run_server(self, port):
#         # Initialize the server
#         self.server = FileSharingServer(port, '/')
#         try:
#             # Start the server
#             self.server.start()
#             print("Press Ctrl+C to stop the server.")
            
#         except KeyboardInterrupt:
#             # Stop the server on Ctrl+C
#             print("\nStopping the server...")
#             self.server.stop()
        

#     def on_stop(self):
#         self.root.ids.hint_message.text = "GoodBye!"
#         self.running = False
#         self.root.ids.start_button_id.text = "Start Server"
#         self.root.ids.status_label.text = "Server Ended !!!"
#         self.root.ids.hide_ip_btn_id.opacity = 0
        
#         # Stop the server when the app is closed
#         if self.server_thread:
#             self.server_thread.join()
#             self.server.stop()
    
#     def hide_ip(self):
#         if not self.running:
#             return
#         if not self.hidden_ip:
#             self.root.ids.hint_message.text = "Hidden Code"
#             self.root.ids.hide_ip_label_id.text = "Show Code"
#         else:
#             self.root.ids.hint_message.text = self.ip
#             self.root.ids.hide_ip_label_id.text = "Hide Code"
            
#         self.hidden_ip= not self.hidden_ip
#     def on_stop(self):
#         return super().on_stop()

# if __name__ == "__main__":
#     FileShareApp().run()

# import os
# import sys
# import threading

# from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
#                              QPushButton, QSystemTrayIcon, QMenu, QAction, QWidget)
# from PyQt5.QtCore import Qt, QThread, pyqtSignal

# from workers.server import FileSharingServer
# from workers.helper import getSystem_IpAdd

# class ServerThread(QThread):
#     status_signal = pyqtSignal(str)
    
#     def __init__(self, port):
#         super().__init__()
#         self.port = port
#         self.server = None
#         self.running = False

#     def run(self):
#         try:
#             self.server = FileSharingServer(self.port, '/')
#             self.running = True
#             self.status_signal.emit("Server Running. Don't share code.")
#             self.server.start()
#         except Exception as e:
#             self.status_signal.emit(f"Server Error: {str(e)}")

#     def stop(self):
#         if self.server:
#             self.server.stop()
#             self.running = False

# class FileShareApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
        
#         # Window setup
#         self.setWindowTitle("Laner")
#         self.setGeometry(100, 100, 500, 500)
        
#         # Icon setup
#         icon_path = "icon.png"
#         if hasattr(sys, "_MEIPASS"):
#             icon_path = os.path.join(sys._MEIPASS, "assets", "imgs", "icon.png")
#         self.setWindowIcon(QIcon(icon_path))

#         # Central widget and layout
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)

#         # Title Label
#         title_label = QLabel("Laner")
#         title_label.setStyleSheet("""
#             font-size: 60px; 
#             color: rgb(0, 179, 153); 
#             text-align: center;
#         """)
#         layout.addWidget(title_label)

#         # Subtitle Label
#         subtitle_label = QLabel("Fast and Secure File Sharing over LAN")
#         subtitle_label.setStyleSheet("""
#             font-size: 20px; 
#             color: gray; 
#             text-align: center;
#         """)
#         layout.addWidget(subtitle_label)

#         # Hint Message Label
#         self.hint_message = QLabel("Connect your PC to your HotSpot\nand Press start to get code")
#         self.hint_message.setStyleSheet("""
#             font-size: 20px; 
#             text-align: center;
#         """)
#         layout.addWidget(self.hint_message)

#         # Start Server Button
#         self.start_button = QPushButton("Start Server")
#         self.start_button.setStyleSheet("""
#             background-color: rgba(0, 179, 153, 0.2);
#             color: rgb(0, 179, 153);
#             padding: 10px;
#             border-radius: 5px;
#         """)
#         self.start_button.clicked.connect(self.start_server)
#         layout.addWidget(self.start_button)

#         # Status Label
#         self.status_label = QLabel("Server not running")
#         self.status_label.setStyleSheet("text-align: center;")
#         layout.addWidget(self.status_label)

#         # Hide IP Button
#         self.hide_ip_btn = QPushButton("Hide Code")
#         self.hide_ip_btn.setStyleSheet("""
#             background-color: rgba(0, 179, 153, 0.2);
#             color: rgb(0, 179, 153);
#             padding: 10px;
#             border-radius: 5px;
#         """)
#         self.hide_ip_btn.clicked.connect(self.hide_ip)
#         self.hide_ip_btn.setVisible(False)
#         layout.addWidget(self.hide_ip_btn)

#         # Server and state variables
#         self.server_thread = None
#         self.running = False
#         self.hidden_ip = False
#         self.ip = None

#         # System Tray
#         # self.create_system_tray()

#     def create_system_tray(self):
#         self.tray = QSystemTrayIcon(self)
        
#         icon_path = "icon.png"
#         if hasattr(sys, "_MEIPASS"):
#             icon_path = os.path.join(sys._MEIPASS, "assets", "imgs", "icon.png")
        
#         self.tray.setIcon(QIcon(icon_path))
        
#         # Create tray menu
#         tray_menu = QMenu()
        
#         show_action = QAction("Show", self)
#         show_action.triggered.connect(self.show)
#         tray_menu.addAction(show_action)
        
#         quit_action = QAction("Quit", self)
#         quit_action.triggered.connect(self.close)
#         tray_menu.addAction(quit_action)
        
#         self.tray.setContextMenu(tray_menu)
#         self.tray.show()

#     def start_server(self):
#         if self.running:
#             self.stop_server()
#             return

#         self.ip = getSystem_IpAdd()
#         if not self.ip:
#             self.hint_message.setText("Connect your PC to your Local Network,\nNo need for Internet Capability")
#             return

#         # Update UI
#         self.hint_message.setText(self.ip)
#         self.start_button.setText("End Server")
#         self.hide_ip_btn.setVisible(True)

#         # Start server thread
#         self.server_thread = ServerThread(8000)
#         self.server_thread.status_signal.connect(self.update_status)
#         self.server_thread.start()
        
#         self.running = True

#     def stop_server(self):
#         if self.server_thread and self.server_thread.running:
#             self.server_thread.stop()
        
#         # Reset UI
#         self.hint_message.setText("Goodbye!")
#         self.start_button.setText("Start Server")
#         self.status_label.setText("Server Ended")
#         self.hide_ip_btn.setVisible(False)
#         self.running = False

#     def hide_ip(self):
#         if not self.running:
#             return
        
#         self.hidden_ip = not self.hidden_ip
        
#         if self.hidden_ip:
#             self.hint_message.setText("Hidden Code")
#             self.hide_ip_btn.setText("Show Code")
#         else:
#             self.hint_message.setText(self.ip)
#             self.hide_ip_btn.setText("Hide Code")

#     def update_status(self, message):
#         self.status_label.setText(message)

#     def closeEvent(self, event):
#         # Stop server when closing
#         if self.running:
#             self.stop_server()
#         event.accept()

# def main():
#     app = QApplication(sys.argv)
#     file_share_app = FileShareApp()
#     file_share_app.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()


import sys
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from workers.server import FileSharingServer
from workers.helper import getSystem_IpAdd


class FileShareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laner")
        self.setGeometry(100, 100, 500, 500)
        self.server_thread = None
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
    app.exec_()
    # sys.exit(app.exec_())

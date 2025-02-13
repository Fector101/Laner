import sys, os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,QHBoxLayout,
    QSystemTrayIcon, QMenu, QAction, QDialog, QFormLayout, QLineEdit, QStackedWidget,QSpinBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize,QThread,pyqtSignal
from workers.server import FileSharingServer
from workers.helper import getUserPCName, getAbsPath
from workers.sword import NetworkManager

DEV=0
class WorkerThread(QThread):
    update_signal = pyqtSignal(object)  # Define signal
    def __init__(self,ip,parent=None):
        super().__init__(parent)
        self.ip =ip
    def run(self):
        try:
            server = FileSharingServer(port=8000,ip=self.ip, directory= '/')
            server.start()
            self.update_signal.emit(server)

            try:
                # Using port from started Server
                NetworkManager().broadcast_ip(server.port)
            except Exception as e:
                print('BroadCast Failed: ',e)
                
        except Exception as e:
            print("See uncaught Errors on App main Thread: ",e)

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


class FileShareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.hidden_ip = False
        self.server = None
        self.ip = None
        self.port = None
        self.icon=getAbsPath("assets", "imgs", "img.ico" if os.name == 'nt' else "icon.png")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Laner")
        self.tray_live_icon=getAbsPath("assets", "imgs", "live.ico" if os.name == 'nt' else "live.png")
        self.setWindowIcon(QtGui.QIcon(self.icon))
        self.setGeometry(100, 100, 500, 500)

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
        if DEV:
            self.start_server()
    def restart_server(self):
        QApplication.quit()
        import subprocess,sys
        py=sys.executable
        print('py --> ',py)
        script=sys.argv[0]
        print('script --> ',script)
        os.execv(py, [py, script])
        
    def create_system_tray(self):
        self.tray = QSystemTrayIcon(self)

        self.tray.setIcon(QIcon(self.icon))

        # Create tray menu
        tray_menu = QMenu()
        if DEV:
            self.dev_btn = QAction("Restart Server", self)
            self.dev_btn.triggered.connect(self.restart_server)
            tray_menu.addAction(self.dev_btn)

        self.start_stop_action = QAction("Quick Connect", self)
        self.start_stop_action.triggered.connect(self.start_server)
        tray_menu.addAction(self.start_stop_action)

        show_action = QAction("Show Code", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def start_server(self):
        if self.running:
            self.on_stop()
            return

        network = NetworkManager()
        self.ip = network.get_server_ip()
        if self.ip is None:
            self.main_screen.hint_message.setText("Connect your PC to your Local Network.\nNo need for Internet Capability.")
            self.main_screen.hint_message.setStyleSheet("color: black;")
            self.main_screen.hint_message.setFont(QFont("Arial", 20))

            return
            # self.main_screen.hint_message.setText("Hidden Code" if self.hidden_ip else self.ip)
        # Start the server in a separate thread
        self.run_server(self.success)
        
    def success(self,server):
        self.running = True
        self.server=server
        self.port=server.port
        
        self.main_screen.hint_message.setStyleSheet("color: gray;")
        self.main_screen.hint_message.setText("Hidden Code" if self.hidden_ip else str(self.port)) # displaying port instead of id
        self.main_screen.hint_message.setFont(QFont("Arial", 34))
        self.main_screen.hide_ip_button.setVisible(True)
        self.main_screen.start_button.setText("End Server")
        self.main_screen.status_label.setText("Server Running. Don't share the code.\nWrite the exact code in the Link Tab on Your Phone.")
        
        self.settings_screen.ip_label.setText(str(self.ip))
        
        self.start_stop_action.setText("Disconnect")
        self.tray.setIcon(QIcon(self.tray_live_icon))
        
    def run_server(self,success=None):
        self.worker = WorkerThread(self.ip)
        self.worker.update_signal.connect(success)
        self.worker.start()

    def on_stop(self):
        self.running = False
        
        self.main_screen.hint_message.setText("Goodbye!")
        self.main_screen.hide_ip_button.setVisible(False)
        self.main_screen.start_button.setText("Start Server")
        self.main_screen.status_label.setText("Server Ended!")
        
        self.settings_screen.ip_label.setText(str(self.ip))
        
        self.start_stop_action.setText("Quick Connect")
        self.tray.setIcon(QIcon(self.icon))
        
        self.server.stop()

    def hide_ip(self):
        if not self.running:
            return

        if not self.hidden_ip:
            self.main_screen.hint_message.setText("Hidden Code")
            self.main_screen.hide_ip_button.setText("Show Code")
        else:
            self.main_screen.hint_message.setText(str(self.port))
            self.main_screen.hide_ip_button.setText("Hide Code")

        self.hidden_ip = not self.hidden_ip

    def open_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_screen)

    def closeEvent(self, event):
        print('peek', event)
        self.hide()
        event.ignore()


if __name__ == "__main__":
    print(sys.argv)
    auto_start = "--autostart" in sys.argv

    app = QApplication(sys.argv)
    window = FileShareApp()

    if auto_start:
        window.start_server()
    else:
        window.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        # When running from cmd and User try to close App with CTRL+C, i don't want to log error after closing with tray
        pass

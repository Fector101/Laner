import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QStackedWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt,QThread,pyqtSignal, QObject

from screens import MainScreen,SettingsScreen
from popups import ConnectionRequest

from workers.server import FileSharingServer
from workers.helper import getUserPCName, getAbsPath
from workers.sword import NetworkManager

DEV=1

class WorkerThread(QThread):
    update_signal = pyqtSignal(object)  # Define signal
    def __init__(self, ip, connection_signal, parent=None):
        super().__init__(parent)
        self.ip =ip
        self.connection_signal = connection_signal
    def run(self):
        try:
            print(self.connection_signal)
            server = FileSharingServer(port=8000,ip=self.ip, directory= '/', connection_signal=self.connection_signal)
            server.start()
            self.update_signal.emit(server)

            try:
                # Using port from started Server
                NetworkManager().broadcast_ip(server.port,server.websocket_port)
            except Exception as e:
                print('BroadCast Failed: ',e)
                
        except Exception as e:
            print("See uncaught Errors on App main Thread: ",e)

class ConnectionSignal(QObject):
    connection_request = pyqtSignal(dict, object)  # Emits ({device_name:'',request:''}, websocket)

class FileShareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.hidden_ip = False
        self.server = None
        self.ip = None
        self.port = None
        self.icon=getAbsPath("assets", "imgs", "img.ico" if os.name == 'nt' else "icon.png")
        self.connection_signal = ConnectionSignal()
        self.connection_signal.connection_request.connect(self.show_connection_request)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Laner")
        self.tray_live_icon=getAbsPath("assets", "imgs", "live.ico" if os.name == 'nt' else "live.png")
        self.setWindowIcon(QIcon(self.icon))
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
        
        # Create PopUps
        self.request_connection_popup:ConnectionRequest=None
        
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
    
        # In your Qt main window class
    def show_connection_request(self, device_name, handler):
        """Show connection dialog"""
        print(device_name,handler, ' name nd handler')
        # self.request_connection_popup.show_request(message_object=device_name, websocket=handler.websocket,event_loop=handler.websocket.loop)
        self.request_connection_popup = ConnectionRequest(message_object=device_name, handler=handler)
        # self.request_connection_popup.show_request()
        
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
        self.run_server(success=self.success, connection_signal=self.connection_signal)
        
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
        
    def run_server(self, connection_signal,success=None):
        self.worker = WorkerThread(self.ip, connection_signal)
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
        NetworkManager().keep_broadcasting = True

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
        # print('peek', event)
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
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
import kivymd.icon_definitions
from kivy.config import Config
import time
import os
import sys
import threading
# import platform

from workers.server import FileSharingServer
from workers.helper import getSystem_IpAdd



Window.size = (500, 500)

#:set THEME_COLOR_TUPLE (160/255, 32/255, 240/255,1)
KV = '''
#:set THEME_COLOR_TUPLE (0, .7, .6, 1)
MDBoxLayout:
    orientation: "vertical"
    padding: dp(10)
    md_bg_color: (.95,.95,.95,1)

    MDLabel:
        text: "Laner"
        halign: "center"
        text_color: THEME_COLOR_TUPLE
        theme_font_size: "Custom"
        font_size: '60sp'
        
    MDLabel:
        text: "Fast and Secure File Sharing over LAN"
        halign: "center"
        text_color: (.5,.5,.5,1)
        theme_font_size: "Custom"
        font_size: '20sp'
        
    MDLabel:
        id: hint_message
        text: 'Connect your PC to your HotSpot\\n and Press start to get code'
        theme_font_size: "Custom"
        font_size: '20sp'
        halign: "center"


    MDButton:
        pos_hint: {"center_x": .5}
        on_release: app.start_server()
        theme_text_color: "Custom"
        theme_bg_color: "Custom"
        theme_width:  "Custom"
        theme_height:  "Custom"
        size_hint:[None,None]
        size:[sp(120),dp(40)]
        
        MDButtonText:
            id: start_button_id
            color: THEME_COLOR_TUPLE
            text: "Start Server"
            pos_hint: {"center_x": .5,"center_y": .5}
        

    MDLabel:
        id: status_label
        text: "Server not running"
        halign: "center"
        theme_text_color: "Hint"

    MDButton:
        id: hide_ip_btn_id
        pos_hint: {"right": 1}
        on_release: app.hide_ip()
        theme_text_color: "Custom"
        theme_bg_color: "Custom"
        radius: 3
        opacity:0
        theme_width:  "Custom"
        theme_height:  "Custom"
        size_hint:[None,None]
        size:[sp(100),dp(40)]
        MDButtonText:
            id: hide_ip_label_id
            color: THEME_COLOR_TUPLE
            text: "Hide Code"
            pos_hint: {"center_x": .5,"center_y": .5}

'''

class FileShareApp(MDApp):
    def build(self):
        icon_path="icon.png"
        # print(os.getcwd(),'----||||----')
        # application_folder = os.path.dirname(__file__)
        #__file__ OR os.path.abspath(__file__) both gives absolute path
        # os.path.dirname(__file__) OR sys._MEIPASS both give temp folder path
        # os.path.dirname(__file__) is better since it work in develepoment when app is not packaged
        
        if hasattr(sys, "_MEIPASS"):
            icon_path=os.path.join(sys._MEIPASS,"assets","imgs","icon.png") 
        self.icon=icon_path
        self.title="Laner"        
        self.server_thread = None
        self.running = False
        self.hidden_ip = False
        self.ip = None
        try:
            return Builder.load_string(KV)
        except:
            time.sleep(200)
    def start_server(self):
        
        if self.running:
            self.root.ids.status_label.text = "Server is already running! don't share code"
            self.on_stop()
            return
        
        self.ip=getSystem_IpAdd()
        if self.ip == None:
            self.root.ids.hint_message.text = "Connect your PC to your Local Network,\n No need for Internet Capability"
            self.root.ids.hint_message.font_style="Body"
            self.root.ids.hint_message.theme_font_size="Custom"
            self.root.ids.hint_message.font_size='20sp'
            self.root.ids.hint_message.text_color=(0,0,0,1)
            return
        else:
            self.root.ids.hint_message.text = "Hidden Code" if self.hidden_ip else self.ip
            self.root.ids.hint_message.font_style="Display"
            self.root.ids.hint_message.theme_font_size= "Primary"
            self.root.ids.hint_message.text_color=(.67,.67,.67,1)




        # TODO Get port from input or use default OR run loop and return use and log found port
        port = 8000
        # Start the HTTP server in a separate thread
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        
        
        self.root.ids.hide_ip_btn_id.opacity = 1
        self.root.ids.start_button_id.text = "End Server"
        self.root.ids.status_label.text = "Server Running don't share code\n Write Extact Code in Link Tab on Your Phone"
        
        
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
        self.root.ids.hint_message.text = "GoodBye!"
        self.running = False
        self.root.ids.start_button_id.text = "Start Server"
        self.root.ids.status_label.text = "Server Ended !!!"
        self.root.ids.hide_ip_btn_id.opacity = 0
        
        # Stop the server when the app is closed
        if self.server_thread:
            self.server_thread.join()
            self.server.stop()
    
    def hide_ip(self):
        if not self.running:
            return
        if not self.hidden_ip:
            self.root.ids.hint_message.text = "Hidden Code"
            self.root.ids.hide_ip_label_id.text = "Show Code"
        else:
            self.root.ids.hint_message.text = self.ip
            self.root.ids.hide_ip_label_id.text = "Hide Code"
            
        self.hidden_ip= not self.hidden_ip
    def on_stop(self):
        return super().on_stop()
def startApp():
    from tray import app
    app.exec_()
if __name__ == "__main__":
    FileShareApp().run()
    # try:
    #     FileShareApp().run()
    # except:
    #     time.sleep(200)


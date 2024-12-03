from kivy.lang import Builder
from kivymd.app import MDApp
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler,HTTPServer
from kivy.core.window import Window
import json
import threading
from server import FileSharingServer
from helper import getSystem_IpAdd

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
        # size_hint_x: 0.8
        halign: "center"


    MDButton:
        pos_hint: {"center_x": .5}
        on_release: app.start_server()
        theme_text_color: "Custom"
        theme_bg_color: "Custom"
        MDButtonText:
            id: start_button_id
            color: THEME_COLOR_TUPLE
            text: "Start Server"
        

    MDLabel:
        id: status_label
        text: "Server not running"
        halign: "center"
        theme_text_color: "Hint"
'''

class FileShareApp(MDApp):
    def build(self):
        self.title="Laner"        
        self.server_thread = None
        self.running = False
        return Builder.load_string(KV)

    def start_server(self):
        print(self.running)
        if self.running:
            self.root.ids.status_label.text = "Server is already running! don't share code"
            self.on_stop()
            return
        ip=getSystem_IpAdd()
        if 'Error' in ip:
            self.root.ids.hint_message.text = "Connect your PC to your Local Network, No need for Internet Capability"
            return
        else:
            self.root.ids.hint_message.text = f"{getSystem_IpAdd()}"
            self.root.ids.hint_message.font_style="Display"
            self.root.ids.hint_message.theme_font_size= "Primary"
            self.root.ids.hint_message.text_color=(.67,.67,.67,1)




        # Get port from input or use default
        # port = self.root.ids.port_input.text
        port = 8000
        # Start the HTTP server in a separate thread
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        
        
        self.root.ids.start_button_id.text = "End Server"
        self.root.ids.status_label.text = "Server Running don't share code"
        # print(self.root.ids)
        
        
        
    def run_server(self, port):
        # Initialize the server
        self.server = FileSharingServer(port, '/')
        try:
            # Start the server
            self.server.start()

            # Keep the program running until interrupted
            print("Press Ctrl+C to stop the server.")
            # while True:
            #     pass
        except KeyboardInterrupt:
            # Stop the server on Ctrl+C
            print("\nStopping the server...")
            self.server.stop()
        
        # with HTTPServer(("", port), CustomHandler) as server:
        #     server.serve_forever()

    def on_stop(self):
        self.root.ids.hint_message.text = "GoodBye!"
        self.running = False
        self.root.ids.start_button_id.text = "Start Server"
        self.root.ids.status_label.text = "Server Ended !!!"
        
        # Stop the server when the app is closed
        # print(self.server_thread)
        if self.server_thread:
            self.server_thread.join()
            self.server.stop()

if __name__ == "__main__":
    FileShareApp().run()
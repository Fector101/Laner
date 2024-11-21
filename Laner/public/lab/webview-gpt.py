from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.webview import WebView  # For webview functionality
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
import os

KV = '''
BoxLayout:
    orientation: "vertical"
    padding: dp(10)

    MDLabel:
        text: "File Sharing Server"
        halign: "center"
        theme_text_color: "Primary"

    MDTextField:
        id: port_input
        hint_text: "Enter port (default: 8000)"
        size_hint_x: 0.8
        pos_hint: {"center_x": 0.5}

    MDRaisedButton:
        text: "Start Server"
        pos_hint: {"center_x": 0.5}
        on_release: app.start_server()

    MDRaisedButton:
        text: "View Directory"
        pos_hint: {"center_x": 0.5}
        on_release: app.view_directory()

    MDLabel:
        id: status_label
        text: "Server not running"
        halign: "center"
        theme_text_color: "Hint"
'''

class FileShareApp(MDApp):
    def build(self):
        self.server_thread = None
        self.running = False
        self.webview_modal = None
        return Builder.load_string(KV)

    def start_server(self):
        if self.running:
            self.root.ids.status_label.text = "Server is already running!"
            return

        # Set the directory to serve files
        os.chdir("shared_files")  # Ensure this folder exists in your app's root

        # Get the port from input or use default
        port = self.root.ids.port_input.text
        port = int(port) if port.isdigit() else 8000

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()

        self.running = True
        self.root.ids.status_label.text = f"Server running at http://127.0.0.1:{port}"

    def run_server(self, port):
        handler = SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()

    def view_directory(self):
        if not self.running:
            self.root.ids.status_label.text = "Start the server first!"
            return

        # Open the WebView to show the file directory
        if not self.webview_modal:
            self.webview_modal = ModalView(size_hint=(0.9, 0.9))
            webview = WebView()
            webview.url = f"http://127.0.0.1:{8000}"
            self.webview_modal.add_widget(webview)
        self.webview_modal.open()

    def on_stop(self):
        # Stop the server when the app is closed
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()

if __name__ == "__main__":
    FileShareApp().run()
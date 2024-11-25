from kivy.lang import Builder
from kivymd.app import MDApp
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler,HTTPServer
import threading
import json

KV = '''
MDBoxLayout:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(10)
    md_bg_color: .5,.5,1,1

    MDLabel:
        text: "File Sharing Server with Custom Endpoint"
        halign: "center"
        theme_text_color: "Primary"

    MDTextField:
        id: port_input
        hint_text: "Enter port (default: 8000)"
        size_hint_x: 0.8
        pos_hint: {"center_x": 0.5}

    MDButton:
        pos_hint: {"center_x": .5}
        on_release: app.start_server()
        theme_text_color: "Custom"
        theme_bg_color: "Custom"
        MDButtonText:
            color: 0,0,1,1
            text: "Start Server"
        

    MDLabel:
        id: status_label
        text: "Server not running"
        halign: "center"
        theme_text_color: "Hint"
'''

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/endpoint_name":
            # Respond with JSON
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            # Example data
            response_data = {"message": "Hello from your Kivy app!"}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
           super().do_GET()
            # Handle unknown endpoints
            # self.send_response(404)
            # self.end_headers()
            # self.wfile.write(b"404 Not Found")

class FileShareApp(MDApp):
    def build(self):
        self.server_thread = None
        self.running = False
        return Builder.load_string(KV)

    def start_server(self):
        if self.running:
            self.root.ids.status_label.text = "Server is already running!"
            return

        # Get port from input or use default
        port = self.root.ids.port_input.text
        port = int(port) if port.isdigit() else 8000

        # Start the HTTP server in a separate thread
        self.server_thread = threading.Thread(target=self.run_server, args=(port,))
        self.server_thread.daemon = True
        self.server_thread.start()

        self.running = True
        self.root.ids.status_label.text = f"Server running at http://<phone_ip>:{port}/api/endpoint_name"

    def run_server(self, port):
        with HTTPServer(("", port), CustomHandler) as server:
            server.serve_forever()
    def run_server(self, port):
        with HTTPServer(("", port), CustomHandler) as server:
            server.serve_forever()

    def on_stop(self):
        # Stop the server when the app is closed
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()

if __name__ == "__main__":
    FileShareApp().run()
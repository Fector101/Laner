
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import json

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/endpoint_name":
            # Handle the custom endpoint
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response_data = {"message": "Hello from your standalone Python server!"}
            request = self.rfile.read()
            print(request)
            request_path='./'
            path_list =os.listdir(request_path)
            # print(path_list)
            dir_info=[]
            for each in path_list:
                dir_info.append({'name':each,'path':os.path.join(request_path,each)})
            
            response_data={'data':dir_info}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            # Serve files for other requests (e.g., base URL)
            super().do_GET()

class FileSharingServer:
    def __init__(self, port=8000, directory="public"):
        self.port = port
        self.directory = directory
        self.server = None
        self.server_thread = None

    def start(self):
        # Change the working directory to serve files
        # if not os.path.exists(self.directory):
        #     os.makedirs(self.directory)
        # print(os.getcwd())
        # os.chdir(self.directory)

        # Create the HTTP server
        self.server = HTTPServer(("", self.port), CustomHandler)

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        print(f"Server started at http://<your_ip>:{self.port}")
        print(f"API endpoint available at http://<your_ip>:{self.port}/api/endpoint_name")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
            print("Server stopped.")

if __name__ == "__main__":
    # Specify the port and directory
    port = 8000
    directory = "public"

    # Initialize the server
    server = FileSharingServer(port, directory)

    try:
        # Start the server
        server.start()

        # Keep the program running until interrupted
        print("Press Ctrl+C to stop the server.")
        while True:
            pass
    except KeyboardInterrupt:
        # Stop the server on Ctrl+C
        print("\nStopping the server...")
        server.stop()

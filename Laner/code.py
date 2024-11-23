
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import json

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/getpathinfo":
            content_length = int(self.headers['Content-Length'])    # This will be None when no path requested (i.e no json= in request)
            request_data = self.rfile.read(content_length)
            try:
                request_path=json.loads(request_data)['path']
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                path_list =os.listdir(request_path)
                dir_info=[]
                for each in path_list:
                    dir_info.append({'name':each,'path':os.path.join(request_path,each)})

                response_data={'data':dir_info}
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'error':"Invaild JSON"}).encode("utf-8"))
            
        else:
            # Serve files for other requests (e.g., base URL)
            super().do_GET()
    def do_POST(self):
        """
        Post request
        responses = requests.post(url="http://localhost:8000/api/endpoint_name",json={'path':self.current_dir})
        print('||||',responses.status_code)
        print('||||',responses.json())
        print('||||',responses)
        """
        
        if self.path == "/api/endpoint_name":
            # Handle the custom endpoint
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                requested_path=json.loads(post_data)['path']
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()


                path_list =os.listdir(requested_path)
                # print(path_list)
                dir_info=[]
                for each in path_list:
                    dir_info.append({'name':each,'path':os.path.join(requested_path,each)})

                response_data={'data':dir_info}
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'error':"Invaild JSON"}).encode("utf-8"))
            
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
        print(f"API endpoint available at http://<your_ip>:{self.port}/api/getpathinfo")

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

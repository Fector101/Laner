import sys,os,tempfile
import json,threading,traceback
from websockets import ServerConnection # for type
import websockets,asyncio
from os.path import join as _joinPath
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Worker imports
if __name__=='__main__':
    # For Tests
    from helper import (
    getAppFolder, getFileExtension, getHomePath, getdesktopFolder,
        makeFolder, sortedDir, getUserPCName
    )
    from thumbnails import get_icon_for_file
    from thumbnails.video import VideoThumbnailExtractor #,generateThumbnails
    from sword import NetworkManager, NetworkConfig
    from web_socket import WebSocketConnectionHandler

else:
    from workers.helper import (
         getAppFolder, getFileExtension, getHomePath, getdesktopFolder,
        makeFolder, sortedDir, getUserPCName
    )
    from workers.thumbnails import get_icon_for_file,VideoThumbnailExtractor
    from workers.sword import NetworkManager, NetworkConfig
    from workers.web_socket import WebSocketConnectionHandler

SERVER_IP = None


# Utility Functions
def writeErrorLog(title, value):
    """Logs errors to a file."""
    error_log_path = os.path.join(getAppFolder(), 'errors.txt')
    with open(error_log_path, 'a') as log_file:
        log_file.write(f'====== {title} LOG ====\n{value}\n\n')
        print(f'====== {title} LOG ====\n{value}\n\n')


# Handle stderr when compiled to a single file
if sys.stderr is None:
    sys.stderr = open(os.path.join(getAppFolder(), 'errors.log'), 'at')


# Threaded HTTP Server
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP Server for handling multiple requests simultaneously."""

def do_lag():
    print('Doing Lag.......')
    import time
    time.sleep(90*60)
# Custom HTTP Handler
class CustomHandler(SimpleHTTPRequestHandler):
    video_paths = []
    request_count = 0
    

    def do_POST(self):
        """Handle POST requests for file uploads."""
        print("Doing Post")
        if self.path == "/api/upload":
            try:
                # Get content length and read raw data
                content_length = int(self.headers.get('Content-Length', 0))
                
                # Extract boundary from Content-Type
                content_type = self.headers.get('Content-Type')
                if not content_type or 'boundary=' not in content_type:
                    raise ValueError("Content-Type header is missing or invalid.")
                
                boundary = content_type.split('=')[1].encode()
                if not boundary:
                    self._send_json_response({'error': "Bad Request: Missing boundary 101"}, status=400)
                    return
                
                data = self.rfile.read(content_length)                
                parts = data.split(b'--' + boundary)
                
                folder_path = getdesktopFolder()
                found_folder=False
                save_path = None
                # print("Whole data: ",parts,'\n')
                for part in parts:
                    # print("This is a part: ",part)
                    if b'name="save_path"' in part and not found_folder:
                        found_folder=True
                        folder_path = (
                            part.split(b'\r\n')[3]  # More precise splitting
                            .decode()
                            .strip()
                        )
                        print("Folder to save upload ----- ", folder_path)
                        os.makedirs(folder_path, exist_ok=True)
                    
                    if b'filename=' in part:
                        # Extract filename
                        headers, file_content = part.split(b'\r\n\r\n', 1)
                        filename = (
                            headers.split(b'filename="')[1]
                            .split(b'"')[0]
                            .decode()
                        )
                        print("Uploaded File name: ----- ", filename)
                        
                        save_path = os.path.join(folder_path, filename)
                        
                        # Remove any trailing boundary markers
                        file_content = file_content.rstrip(b'\r\n--')
                        # Write file safely
                        with open(save_path, 'wb') as f:
                            f.write(file_content)
                
                if save_path:
                    print("File Upload Successful:", save_path)
                    self._send_json_response({'message': 'File uploaded successfully'})
                else:
                    self._send_json_response({'error': "No file content found in the uploaded data."}, status=400)
                    # raise ValueError("No file content found in the uploaded data.")
            
            except Exception as e:
                print("File Upload Error:", e)
                writeErrorLog('File Upload Error', traceback.format_exc())
                self._send_json_response({'error': str(e)}, status=400)

    def do_GET(self):
        """Handle GET requests for various API endpoints."""
        try:
            if self.path == "/api/getpathinfo":
                request_path = self._get_request_body('path')
                if request_path == 'Home':
                    request_path = getHomePath()
                elif request_path == None: # Checking for None incase i send '' as path in future and not './'
                    self._send_json_response({'error': "Server didn't recieve any data, i.e no requested_path"}, status=400)
                    return
                dir_info = []
                self.video_paths = []

                for each in os.listdir(request_path):
                    each_path = os.path.join(request_path, each)
                    img_source, thumbnail_url = get_icon_for_file(each_path,video_paths=self.video_paths)
                    cur_obj = {
                        'text': each,
                        'path': each_path,
                        'is_dir': os.path.isdir(each_path),
                        'icon': img_source,
                        'thumbnail_url': thumbnail_url,
                        'validated_path': False
                    }
                    dir_info.append(cur_obj)

                dir_info = sortedDir(dir_info)
                # print('dta ',dir_info)
                self._send_json_response({'data': dir_info})

                if self.video_paths:
                    VideoThumbnailExtractor(self.video_paths, 1, 10).extract()

            elif self.path == "/api/isdir":
                self._send_json_response({'data': os.path.isdir(self.parseMyPath())})
            elif self.path == "/api/isfile":
                request_path = self._get_request_body('path')
                is_file=os.path.isfile(request_path)
                if not is_file:
                    file_abspath=os.path.abspath(request_path)
                    drive=os.path.splitdrive(file_abspath)[0]
                    real_file_path= _joinPath(drive,request_path)
                    is_file=os.path.isfile(real_file_path)
                    print("Windows test 101: ",real_file_path)
                    
                self._send_json_response({'data': is_file})
                
            elif self.path == "/ping":
                NetworkManager().keep_broadcasting=False
                self._send_json_response({'data': getUserPCName()})
            else:
                super().do_GET()
                # self._send_json_response({'error': "Endpoint not found."}, status=404)
        except PermissionError as e:
            writeErrorLog('Permission Error', traceback.format_exc())
            self._send_json_response({'error': "Permission denied. Please check your access rights."}, status=403)
        except Exception as e:
            writeErrorLog('Error Handling for All Requests', traceback.format_exc())
            self._send_json_response({'error': str(e)}, status=400)

        self.request_count += 1

    def parseMyPath(self):
        """ Takes unreal_path from app and format to real path eg Home --> ~ Home :) TODO Remove this"""
        app_requested_path=self._get_request_body('path')
        return getHomePath() if app_requested_path == 'Home' else app_requested_path
        
    def _get_request_body(self, key):
        """Parses JSON from the request body."""
        extracted_length = self.headers['Content-Length']
        if extracted_length == None: # explicty checking None incase maybe it can be 0,test more and remove line
            return extracted_length
        content_length = int(extracted_length)
        request_data = self.rfile.read(content_length)
        print('Why',json.loads(request_data).get(key))
        return json.loads(request_data).get(key)

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_json_response(self, data, status=200):
        """Sends a JSON response."""
        self.send_response(status)
        # self._set_cors_headers() # <--- For testing from javascript|brower (Don't package with this line, maybe package because of offline website docs)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except ConnectionAbortedError as connection_aborted_error:
            writeErrorLog(f'Connection was aborted: {connection_aborted_error}', traceback.format_exc())


# Server Class
class FileSharingServer:
    def __init__(self, ip, connection_signal=None, port=8000, directory="/"):
        self.ip = ip
        self.port = port
        self._server = None
        self.directory = directory
        makeFolder(os.path.join(getAppFolder(), 'thumbnails'))
        if not connection_signal:
            print("No 'connection_signal' Running without UI")
        self.connection_signal = connection_signal
        self.loop = None
        self.websocket_port = None
        self.websocket_server = None
        self.ws_thread=None

    async def websocket_handler(self, websocket):
        """Handle new WebSocket connections"""
        handler = WebSocketConnectionHandler(
            websocket=websocket,
            connection_signal=self.connection_signal,
            ip=self.ip,
            main_server_port=self.port
        )
        await handler.handle_connection()  # Make sure to await the connection handler        

    # Modify the WebSocket server setup in the FileSharingServer class
    async def start_websocket_server(self):
        # Create a wrapper function to properly bind the instance method
        async def handler(websocket):
            await self.websocket_handler(websocket)

        self.websocket_port=self.port + 1
        self.websocket_server = await websockets.serve(
            handler,
            self.ip,
            self.websocket_port
        )
        print(f"WebSocket server started at ws://{self.ip}:{self.port+1}")

    def start(self):
        global SERVER_IP
        NetworkConfig.server_ip = SERVER_IP = self.ip or SERVER_IP

        # print(SERVER_IP,self.ip)
        os.chdir(self.directory)

        # self.server = ThreadingHTTPServer((self.ip, self.port), CustomHandler)
        # threading.Thread(target=self.server.serve_forever, daemon=True).start()
        # print(f"Server started at http://{SERVER_IP}:{self.port}")

        self._server =None
        
        ports =  [
                    8000, 8080, 9090, 10000, 11000, 12000, 13000, 14000, 
                    15000, 16000, 17000, 18000, 19000,
                    20000, 22000, 23000, 24000, 26000,
                    27000, 28000, 29000, 30000
                ]
        # TODO ping Server from PC and Check for Unquie Generated Code from maybe Singleton
        for port in ports:
            print('Trying ',self.ip,port)
            try:
                # self._server = ThreadingHTTPServer(("", port), CustomHandler)
                # self._server = ThreadingHTTPServer(("0.0.0.0", port), CustomHandler)
                self._server = ThreadingHTTPServer((self.ip, port), CustomHandler)
                self.port=port
                threading.Thread(target=self._server.serve_forever, daemon=True).start()
                print(f"Server started at http://{SERVER_IP}:{self.port}")
                break  # Exit the loop if the server starts successfully
            except OSError as e:
                print(f"Port {port} is unavailable, trying the next one...")
                writeErrorLog(f'{e} -- Port :{port}',traceback.format_exc())
                traceback.print_exc()
            except Exception as e:
                print(f"Error: {e}")
                writeErrorLog(f'{e} -- Port :{port}',traceback.format_exc())
        # Start WebSocket server in event loop
        self.ws_thread = threading.Thread(target=self.run_websocket_server)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        print('Ended trying',port)

    def stop(self):
        # Stop HTTP server
        if self._server:
            self._server.shutdown()
            self._server.server_close()

        # Stop WebSocket server
        if self.loop:
            # Schedule the server closure and loop stop
            async def close_server_and_stop_loop():
                if self.websocket_server:
                    self.websocket_server.close()
                    await self.websocket_server.wait_closed()
                    print("WebSocket server stopped")
                self.loop.stop()  # Stop the loop only after server is closed

            # Schedule the entire shutdown sequence
            self.loop.call_soon_threadsafe( lambda: asyncio.create_task(close_server_and_stop_loop()) )
        print("Server stopped.")
    def run_websocket_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_websocket_server())
        self.loop.run_forever()

print(__name__,'==','__main__')
if __name__ == "__main__":
    # Specify the port and directory
    port = 8000
    directory = "/"

    # Initialize the server
    server = FileSharingServer(port=port,directory=directory,ip=NetworkManager().get_server_ip())

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
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import os
import sys
import json
import threading
import traceback
from os.path import join as _joinPath

# Worker imports
from workers.helper import (
    gen_unique_filname, getAppFolder, getFileExtension, getHomePath, getdesktopFolder,
    makeFolder, removeFirstDot, sortedDir, urlSafePath, getUserPCName
)
from workers.thumbmailGen import generateThumbnails

# File Type Definitions
MY_OWNED_ICONS = ['.py', '.js', '.css', '.html', '.json', '.deb', '.md', '.sql', '.java']
ZIP_FORMATS = ['.zip', '.7z', '.tar', '.bzip2', '.gzip', '.xz', '.lz4', '.zstd', '.bz2', '.gz']
VIDEO_FORMATS = ('.mkv', '.mp4', '.avi', '.mov')
AUDIO_FORMATS = ('.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac', '.wma', '.aiff', '.opus')
PICTURE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif')
SPECIAL_FOLDERS = ['home', 'pictures', 'templates', 'videos', 'documents', 'music', 'favorites', 'share', 'downloads']

SERVER_IP = None


# Utility Functions
def writeErrorLog(title, value):
    """Logs errors to a file."""
    error_log_path = os.path.join(getAppFolder(), 'errors.txt')
    with open(error_log_path, 'a') as log_file:
        log_file.write(f'====== {title} LOG ====\n{value}\n\n')


# Handle stderr when compiled to a single file
if sys.stderr is None:
    sys.stderr = open(os.path.join(getAppFolder(), 'errors.log'), 'at')


# Threaded HTTP Server
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP Server for handling multiple requests simultaneously."""
    pass


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
                data = self.rfile.read(content_length)
                
                # Extract boundary from Content-Type
                content_type = self.headers.get('Content-Type')
                if not content_type or 'boundary=' not in content_type:
                    raise ValueError("Content-Type header is missing or invalid.")
                
                boundary = content_type.split('=')[1].encode()
                parts = data.split(b'--' + boundary)
                
                folder_path = getdesktopFolder()
                found_folder=False
                save_path = None
                
                for part in parts:
                    # print("This is a part: ",part)
                    if b'name="save_path"' in part and not found_folder:
                        found_folder=True
                        folder_path = (
                            part.split(b'\r\n')[3]  # More precise splitting
                            .decode()
                            .strip()
                        )
                        print("My folder path variable ----- ", folder_path)
                        os.makedirs(folder_path, exist_ok=True)
                    
                    if b'filename=' in part:
                        # Extract filename
                        headers, file_content = part.split(b'\r\n\r\n', 1)
                        filename = (
                            headers.split(b'filename="')[1]
                            .split(b'"')[0]
                            .decode()
                        )
                        print("Found file name: ----- ", filename)
                        
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

                dir_info = []
                self.video_paths = []

                for each in os.listdir(request_path):
                    each_path = os.path.join(request_path, each)
                    is_dir = os.path.isdir(each_path)
                    format_ = getFileExtension(each).lower()
                    img_source, thumbnail_url = self._get_file_icon(each, each_path, is_dir, format_)

                    cur_obj = {
                        'text': each,
                        'path': each_path,
                        'is_dir': is_dir,
                        'icon': img_source,
                        'thumbnail_url': thumbnail_url,
                        'validated_path': False
                    }
                    dir_info.append(cur_obj)

                dir_info = sortedDir(dir_info)
                self._send_json_response({'data': dir_info})

                if self.video_paths:
                    threading.Thread(
                        target=generateThumbnails,
                        args=(self.video_paths, os.path.join(getAppFolder(), 'thumbnails'), 1, 10),
                        daemon=True
                    ).start()

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
                self._send_json_response({'data': getUserPCName()})
            else:
                super().do_GET()
                
                # self.send_error(404, "Endpoint not found.")
        except Exception as e:
            writeErrorLog('Request Handling Error', traceback.format_exc())
            self._send_json_response({'error': str(e)}, status=400)

        self.request_count += 1
    def parseMyPath(self):
        """ Takes unreal_path from app and format to real path eg Home --> ~ Home :) TODO Remove this"""
        app_requested_path=self._get_request_body('path')
        return getHomePath() if app_requested_path == 'Home' else app_requested_path
        
    def _get_request_body(self, key):
        """Parses JSON from the request body."""
        content_length = int(self.headers['Content-Length'])
        request_data = self.rfile.read(content_length)
        print('Why',json.loads(request_data).get(key))
        return json.loads(request_data).get(key)

    def _send_json_response(self, data, status=200):
        """Sends a JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_file_icon(self, name, path, is_dir, format_):
        """Returns appropriate icon and thumbnail based on file type."""
        if is_dir:
            return f"assets/icons/folders/{name.lower()}.png" if name.lower() in SPECIAL_FOLDERS else "assets/icons/folders/folder.png", ''
        elif format_ in MY_OWNED_ICONS:
            return f"assets/icons/{format_[1:]}.png", ''
        elif format_ in ZIP_FORMATS:
            return "assets/icons/packed.png", ''
        elif format_ in VIDEO_FORMATS:
            self.video_paths.append(path)
            thumbnail_path = os.path.join(getAppFolder(),'thumbnails',gen_unique_filname(path)+'.jpg')
            formatted_path_4_url=urlSafePath(removeFirstDot(thumbnail_path))
            print(f"http://{SERVER_IP}:8000/{formatted_path_4_url}")
            return "assets/icons/video.png", f"http://{SERVER_IP}:8000/{formatted_path_4_url}"
        elif format_ in AUDIO_FORMATS:
            return "assets/icons/audio.png", ''
        elif format_ in PICTURE_FORMATS:
            return f"http://{SERVER_IP}:8000/{urlSafePath(path)}", ''
        return "assets/icons/file.png", ''


# Server Class
class FileSharingServer:
    def __init__(self, ip, port=8000, directory="/"):
        self.ip = ip
        self.port = port
        self.directory = directory
        makeFolder(os.path.join(getAppFolder(), 'thumbnails'))

    def start(self):
        global SERVER_IP
        SERVER_IP = self.ip
        os.chdir(self.directory)

        self.server = ThreadingHTTPServer((self.ip, self.port), CustomHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        print(f"Server started at http://{SERVER_IP}:{self.port}")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        print("Server stopped.")

# if __name__ == "__main__":
#     # Specify the port and directory
#     port = 8000
#     directory = "/"

#     # Initialize the server
#     server = FileSharingServer(port, directory)

#     try:
#         # Start the server
#         server.start()

#         # Keep the program running until interrupted
#         print("Press Ctrl+C to stop the server.")
#         while True:
#             pass
#     except KeyboardInterrupt:
#         # Stop the server on Ctrl+C
#         print("\nStopping the server...")
#         server.stop()
# filename="helper.py"\r\n\r\n
# filename="server.py"\r\n\r\n
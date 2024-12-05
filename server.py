from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import json
from helper import getHomePath,getSystem_IpAdd
import threading


SERVER_IP = getSystem_IpAdd()
no = 1
from socketserver import ThreadingMixIn
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global no
        print(no)
        if self.path == "/api/getpathinfo":
            content_length = int(self.headers['Content-Length'])    # This will be None when no path requested (i.e no json= in request)
            request_data = self.rfile.read(content_length)
            try:
                data=json.loads(request_data)
                request_path=data['path']
                # ip=data['path']
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                path_list:list[str] =os.listdir(request_path)
                dir_info=[]
                for each in path_list:
                    each_path=os.path.join(request_path,each)
                    is_dir=os.path.isdir(each_path)
                    img_source=None
                    format_=each.split(".")[-1].lower()
                    my_owned_icons=['py','js','css','html','json','deb','md','sql','md','java']
                    zip_formats=['zip','7z','tar','bzip2','gzip','xz','lz4','zstd','bz2','gz']
                    video_formats=['mp4','mov','mkv']
                    special_folders=['home','pictures','templates','videos','documents','music','favorites','share','downloads']
                    home_path=getHomePath()
                    if is_dir:
                        # print(os.path.join(home_path,each), '==', os.path.join(request_path[1:],each))
                        if each.lower() in special_folders and (each.lower() in special_folders or os.path.join(home_path,each) == os.path.join(request_path[1:],each)):
                            # os.path.join(request_path[1:],each): this means getting root path will always be './' not '/'
                            img_source=f"assets/icons/folders/{each.lower()}.png"
                        else:                        
                            img_source="assets/icons/folders/folder.png"
                    elif each.lower().endswith(('.png','.jpg','.jpeg','.tif','.bmp','.gif')):
                        img_source=f"http://{SERVER_IP}:8000{each_path[1:].replace(' ','%20')}"
                    elif format_ in my_owned_icons:
                        img_source=f"assets/icons/{format_}.png"
                        # img_source=f"http://{SERVER_IP}:8000/home/fabian/Documents/my-projects-code/mobile-dev/Laner/Laner/assets/imgs/py.png"
                    elif format_ in zip_formats:
                        img_source=f"assets/icons/packed.png"
                    else:
                        img_source="assets/icons/file.png"
                    
                    dir_info.append({
                        'text':each,
                        'path':each_path,
                        'is_dir':is_dir,'icon':img_source
                        })
                
                dir_info=sorted(dir_info,key=lambda path: path['text'])
                
                # Push files with dot at front to the back
                items_with_dot=[]
                items_without_dot=[]
                for each in dir_info:
                    if each['text'][0] == '.':
                        items_with_dot.append(each)
                    else:
                        items_without_dot.append(each)
                
                dir_info=[*items_without_dot, *items_with_dot]
                
                response_data={'data':dir_info}
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
                print('Handled -----')
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'error':"Invaild JSON"}).encode("utf-8"))

        elif self.path == "/api/ispath":
            
            content_length = int(self.headers['Content-Length'])    # This will be None when no path requested (i.e no json= in request)
            request_data = self.rfile.read(content_length)
            try:
                request_path=json.loads(request_data)['path']
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                self.wfile.write(json.dumps({'data':os.path.isdir(request_path)}).encode("utf-8"))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'error':"Invaild JSON"}).encode("utf-8"))
            
        else:
            
           
            super().do_GET()
        no+=1
   
class FileSharingServer:
    def __init__(self, port=8000, directory="/"):
        self.port = port
        self.directory = directory
        self.server = None
        self.server_thread = None

    def start(self):
        os.chdir(self.directory)

        # Create the HTTP server
        self.server = ThreadingHTTPServer(("", self.port), CustomHandler)
        # self.server.serve_forever()
        
        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        print(f"Server started at http://{SERVER_IP}:{self.port}")
        print(f"API endpoint available at http://{SERVER_IP}:{self.port}/api/getpathinfo")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
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

from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import json
import threading

from workers.helper import gen_unique_filname, getAppFolder, getFileExtension, getHomePath,getSystem_IpAdd, getdesktopFolder, makeDownloadFolder, makeFolder, removeFileExtension, getUserPCName,removeFirstDot, sortedDir
from workers.thumbmailGen import generateThumbnails


my_owned_icons=['.py','.js','.css','.html','.json','.deb','.md','.sql','.md','.java']
zip_formats=['.zip','.7z','.tar','.bzip2','.gzip','.xz','.lz4','.zstd','.bz2','.gz']
video_formats=('.mkv','.mp4', '.avi', '.mkv', '.mov')
audio_formats=('.mp3','.wav','.aac','.ogg','.m4a','.flac','.wma','.aiff','.opus')
picture_formats=('.png','.jpg','.jpeg','.tif','.bmp','.gif')
special_folders=['home','pictures','templates','videos','documents','music','favorites','share','downloads']
                

SERVER_IP = getSystem_IpAdd()
no = 1
generated_thumbnails=[]
def inHomePath(request_path,folder):
    print(os.path.join(getHomePath(),folder), "==", os.path.join(request_path,folder))
    return os.path.join(getHomePath(),folder) == os.path.join(request_path,folder)
    
from socketserver import ThreadingMixIn
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class CustomHandler(SimpleHTTPRequestHandler):
    
    # get uploaded data and save it to a file
    def do_POST(self):
        global no
        if self.path == "/api/upload":
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)

            # Get the boundary from Content-Type header
            content_type = self.headers['Content-Type']
            boundary = content_type.split('=')[1].encode()

            # Parse multipart form data
            parts = data.split(boundary)
            save_path = None
            
            for part in parts:
                if b'name="save_path"' in part:
                    save_path = part.split(b'\r\n\r\n')[1].strip(b'\r\n--').decode()
                elif b'filename=' in part:
                    # Extract filename
                    filename_match = part.split(b'filename="')[1].split(b'"')[0]
                    filename = filename_match.decode()
                    
                    # Extract file content
                    file_content = part.split(b'\r\n\r\n')[1].strip(b'\r\n--')
                    if save_path:
                        if (save_path == 'Home'):
                            save_path = getHomePath()
                        save_path = os.path.join(save_path, filename)
                    else:
                        save_path = os.path.join(getdesktopFolder(), filename)
                        
                    print('BLah',save_path)
                    with open(save_path, 'wb') as f:
                        f.write(file_content)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'File uploaded successfully'}).encode())
           
    
    def do_GET(self):
        global no, generated_thumbnails
        # print(no)
        if self.path == "/api/getpathinfo":
            request_path=self.getRequestBody('path')
            if (request_path == None):
                return
            elif (request_path == 'Home'):
              request_path = getHomePath()
            print('dev home path',request_path)
         
            
            try:
                path_list:list[str] =os.listdir(request_path)
                dir_info=[]
                videos_paths=[]
                
                for each in path_list:
                    thumbnail_url=''
                    thumbnail_path=''
                    each_path=os.path.join(request_path,each)
                    is_dir=os.path.isdir(each_path)
                    img_source=None
                    format_=getFileExtension(each).lower()

                    if is_dir:
                        if each.lower() in special_folders:
                            img_source=f"assets/icons/folders/{each.lower()}.png"
                        else:
                            img_source="assets/icons/folders/folder.png"
                            
                    elif each.lower().endswith(picture_formats):
                        img_url=removeFirstDot(each_path).replace(' ','%20').replace('\\','/')
                        img_source=f"http://{SERVER_IP}:8000{img_url}"

                    elif format_ in my_owned_icons:
                        img_source=f"assets/icons/{format_[1:]}.png"

                    elif format_ in zip_formats:
                        img_source=f"assets/icons/packed.png"

                    elif each.lower().endswith(video_formats):
                        image_path = gen_unique_filname(each_path)
                        thumbnail_path = os.path.join(getAppFolder(),'thumbnails',image_path+'_thumbnail.jpg')
                        
                        formatted_path_4_url=removeFirstDot(thumbnail_path).replace('\\','/')
                        thumbnail_url=f"http://{SERVER_IP}:8000{formatted_path_4_url}"
                        
                        img_source="assets/icons/video.png" 
                        if each_path not in generated_thumbnails:
                            generated_thumbnails.append(each_path)
                            videos_paths.append(each_path)
                    elif each.lower().endswith(audio_formats):
                        img_source="assets/icons/audio.png"                    
                    else:
                        img_source="assets/icons/file.png"                    

                    cur_obj={
                        'text':each,
                        'path':each_path,
                        'is_dir':is_dir,'icon':img_source,
                        'thumbnail_url':thumbnail_url,
                        'thumbnail_path':thumbnail_path,
                        'validated_path':False,
                        # 'size':os.path.getsize(each_path),
                        
                        
                        }
                    dir_info.append(cur_obj)
                
                
                dir_info=sortedDir(dir_info)
                response_data={'data':dir_info}
                
                if len(videos_paths):
                    th=threading.Thread(target=generateThumbnails,args=(videos_paths, os.path.join(getAppFolder(),'thumbnails'),1,10))
                    th.daemon = True
                    th.start()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
                print('Handled -----',no,' Requests')
                
                
                
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'error':type(e).__name__}).encode("utf-8"))

        elif self.path == "/api/isdir":
            request_path=self.getRequestBody('path')
            if (request_path != None):
                if (request_path == 'Home'):
                    request_path = getHomePath()
                self.wfile.write(json.dumps({'data':os.path.isdir(request_path)}).encode("utf-8"))
            
        elif self.path == "/api/isfile":
            request_path=self.getRequestBody('path')
            if (request_path != None):
                self.wfile.write(json.dumps({'data':os.path.isfile(request_path)}).encode("utf-8"))
            
            
        elif self.path == "/ping":
            res=self.getRequestBody('passcode')
            if res == '08112321825':
                self.wfile.write(json.dumps({'data':getUserPCName()}).encode("utf-8"))
        else:
            super().do_GET()
        no+=1
    def getRequestBody(self,request_key):
        content_length = int(self.headers['Content-Length'])    # This will be None when no path requested (i.e no json= in request)
        request_data = self.rfile.read(content_length)
        try:
            request_path=json.loads(request_data)[request_key]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            return request_path
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({'error': type(e).__name__ }).encode("utf-8"))

class FileSharingServer:
    def __init__(self, port=8000, directory="/"):
        self.port = port
        self.directory = directory
        self.server = None
        self.server_thread = None
        makeFolder(os.path.join(getAppFolder(),'thumbnails'))
    def getPortNumer(self):
        return self.port
    def start(self):
        global SERVER_IP
        SERVER_IP = getSystem_IpAdd()
        
        os.chdir(self.directory)

        # Create the HTTP server
        self.server =None
        
        ports =  [
                    8000, 8080, 9090, 10000, 11000, 12000, 13000, 14000, 
                    15000, 16000, 17000, 18000, 19000,
                    20000, 22000, 23000, 24000, 26000,
                    27000, 28000, 29000, 30000
                ]

        for port in ports:
            try:
                # Attempt to start the server on the current port
                self.server = ThreadingHTTPServer(("", port), CustomHandler)
                print(f"Server running on port {port}")
                self.port=port
                break  # Exit the loop if the server starts successfully
            except OSError:
                print(f"Port {port} is unavailable, trying the next one...")
            except Exception as e:
                print(f"Error: {e}")
        # else:
        #     print("All specified ports are in use. Please free up a port and try again.")
        
        
        
        
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
# /home/fabian/Documents/my-projects-code/mobile-dev/Laner/thumbnails/2.%20Reading%20from%20Your%20Database%20with%20Mongoose_thumbnail.jpg
# /home/fabian/Documents/my-projects-code/mobile-dev/Laner/thumbnails/2.%20Reading%20from%20Your%20Database%20with%20Mongoose_thumbnail.jpg
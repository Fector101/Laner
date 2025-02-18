import os
import shutil
import requests
import threading
import traceback

from kivy.clock import Clock
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from android_notify import Notification, NotificationStyles

from workers.helper import getAppFolder,get_full_class_name,urlSafePath,getFormat
from workers.sword import Settings,NetworkManager
from widgets.popup import Snackbar
from workers.utils.constants import IMAGE_FORMATS
# Notification.logs = True

class ProgressData:
    # Monitor LookAlike
    def __init__(self,bytes_read,len_):
        self.bytes_read=bytes_read
        self.len=len_
class AsyncRequest:
    
    def __init__(self):
        self.download_notification= None
        self.upload_notification= None
        self.percent=0 # Don't share Instances
    # requests.get(server,data='to be sent',auth=(username,password))
    def get_server_ip(self) -> str:
        """Return the server IP from settings."""
        return Settings().get("server", "ip")
    
    def get_port_number(self) -> str:
        """Return the server port number from settings."""
        return Settings().get("server", "port")
    def get_path_data(self,path,success,failed=None):
        def __make_request():
            try:
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/getpathinfo"
                json_ = {'path':path}
                response = requests.get(url,json=json_,timeout=5)
                if response.status_code == 200:
                    self.on_ui_thread(success,args=[response.json()['data']])
            except requests.exceptions.ReadTimeout:
                Clock.schedule_once(lambda dt:Snackbar(h1="Couldn't Open Folder - TimeoutError"))
            except Exception as e:
                self.do_failed(failed)
                print("Failed opening Folder async ",e)
                traceback.print_exc()
                
        thread = threading.Thread(target=__make_request)
        thread.start()
    def on_ui_thread(self,fun,args=[]):
        if not fun:
            return
        try:
            if args:
                Clock.schedule_once(lambda dt:fun(*args))
            else:
                Clock.schedule_once(lambda dt:fun())
        except Exception as e:
            print('Failed to excute function on ui Thread: ',e)
    
    def do_failed(self,failed):
        if failed:
            self.on_ui_thread(failed)
        
    def is_folder(self, path,success,failed=None):
        url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/isdir"
        def __make_request():
            try:
                response = requests.get(url,json={'path':path},timeout=3)
                if response.status_code == 200 and response.json()['data']:
                    self.on_ui_thread(success)
                elif failed:
                    self.on_ui_thread(failed)
            except Exception as e:
                if failed:
                    self.on_ui_thread(failed)
                print('is_folder',e)
                traceback.print_exc()
                
        thread = threading.Thread(target=__make_request)
        thread.start()
        
    def is_file(self, path,success,failed=None):
        url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/isfile"
        file_url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{urlSafePath(path)}"
        def __make_request():
            try:
                response = requests.get(url,json={'path':path},timeout=2)
                if response.status_code == 200 and response.json()['data']:
                    self.on_ui_thread(success,args=[file_url])
                elif failed:
                    self.on_ui_thread(failed)
            except Exception as e:
                if failed:
                    self.on_ui_thread(failed)
                print('AsyncRequest Sword is_file Error: ',e)
                traceback.print_exc()
                
        thread = threading.Thread(target=__make_request)
        thread.start()
    def successfull_download_notification(self,save_path):
        file_name = os.path.basename(save_path)
        try:
            # If the file is an image, copy it to the app's assets and send a notification.
            if getFormat(file_name) in IMAGE_FORMATS:
                shutil.copy(save_path, os.path.join(getAppFolder(), 'assets', 'imgs', file_name))
                self.download_notification.large_icon_path=save_path
                self.download_notification.addNotificationStyle(NotificationStyles.LARGE_ICON,already_sent=True)
        except Exception as e:
            print(e,"Adding Img to Notification")
    def send_initial_download_notification(self,file_name):
        self.download_notification = Notification(
                title="Downloaded (0%)",
                message=file_name,
                style=NotificationStyles.PROGRESS,
                progress_max_value=100,progress_current_value=0,
                channel_name='Downloads'
                    # TODO use notification groups
                )
        self.download_notification.send()
    def update_progress(self,monitor,notification:Notification,type_):
        new_percent = int((monitor.bytes_read / monitor.len) * 100)
        if new_percent == 100:
            notification.updateTitle(f'Completed {type_}')
            notification.removeProgressBar()
        elif new_percent != self.percent:
            # print(f"{type_}ing ({new_percent}%)")
            self.percent=new_percent
            notification.updateTitle(f"{type_}ing ({self.percent}%)")
            notification.updateProgressBar(self.percent)
        
    def download_file(self, file_path,save_path,success,failed=None):
        file_name = os.path.basename(save_path)
        def _download():
            try:
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path}"
                response = requests.get(url, stream=True,timeout=(2,None))
                print('got file -- Doing progress bar')
                if response.status_code == 200:
                    # Get the total file size from the response headers (if available)
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 8192  # Adjust chunk size as needed
                    self.send_initial_download_notification(file_name)
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:  # Filter out keep-alive chunks
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress_data = ProgressData(bytes_read=downloaded,len_=total_size)
                                self.update_progress(progress_data,self.download_notification,type_='Download')
                            else:
                                # If no content length header, just print downloaded bytes.
                                print(f"Downloaded: {downloaded} bytes")
                                
                    
                    self.successfull_download_notification(save_path)
                    self.on_ui_thread(success,[file_name])
                else:
                    self.on_ui_thread(failed)
                    
            except Exception as e:
                print("Failed Download Error type: ",e)
                self.download_notification.updateTitle('Download Error!')
                self.download_notification.removeProgressBar()
                traceback.print_exc()
                self.on_ui_thread(failed)
        threading.Thread(target=_download).start()
    
        
    def upload_file(self, file_path, save_path,success,failed=None,file_data=None):
        file_basename = os.path.basename(file_path)        
        def update_progress(monitor):
            self.update_progress(monitor,notification=self.upload_notification,type_='Upload')                
            
        self.upload_notification = Notification(
            title="Uploading (0%)",
            message=file_basename,
            style=NotificationStyles.PROGRESS,
            progress_max_value=100,progress_current_value=0,
            channel_name="Uploads"
            )
        self.upload_notification.send()
        
        
        def __upload():
            try:
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/upload"
                # files = {'file': file_data if file_data else open(file_path, 'rb')}
                # Create the multipart encoder; note that we open the file in binary mode.
                encoder = MultipartEncoder(
                    fields={
                        'save_path': save_path,
                        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')
                    }
                )

                # Wrap it in a monitor to get progress updates.
                monitor = MultipartEncoderMonitor(encoder, update_progress)

                response = requests.post(
                                        url, data=monitor,
                                        headers={'Content-Type': monitor.content_type},
                                        timeout=(2,None)
                                         )
                

                if response.status_code == 200:
                    self.on_ui_thread(success)
                else:
                    Clock.schedule_once(lambda dt:Snackbar(h1=f'Upload Failed - Code {response.status_code}'))
                    self.on_ui_thread(failed)

            except Exception as e:
                self.upload_notification.updateTitle('Upload Error!')
                self.upload_notification.removeProgressBar()
                self.on_ui_thread(failed)
                print("Failed Upload ",e)
                traceback.print_exc()
                
        threading.Thread(target=__upload).start()
        
    def auto_connect(self,success,failed=None):
        timeout=0.5
        
        def try_old_ports():
            print("Trying old ports and ip's...")
            pervious_connections=Settings().get_recent_connections()
            port=Settings().get("server", "port")
            for ip_address in pervious_connections:
                try:
                    print('trying... ',ip_address,port)
                    response=requests.get(f"http://{ip_address}:{port}/ping",json={'passcode':'08112321825'},timeout=timeout)
                    if response.status_code == 200:
                        pc_name = response.json()['data']
                        Settings().set('server', 'ip', ip_address)
                        self.on_ui_thread(success,args=[pc_name,ip_address])
                        print("Found Good Old Port 🥳🥳🥳")
                        break
                except Exception as ea:
                    self.do_failed(failed)
                    print("Old Port Failed - Dev Auto Connect Error: ", get_full_class_name(ea))

        def __auto_connect():
            print('theading...')
            port = 8000
            ip_address = NetworkManager().find_server(port,timeout=timeout)
            print(f"Connecting to server at {ip_address}")
            try:
                if ip_address:    
                    response=requests.get(f"http://{ip_address}:{port}/ping",json={'passcode':'08112321825'},timeout=timeout)
                    if response.status_code == 200:
                        pc_name = response.json()['data']
                        Settings().set('server', 'ip', ip_address)
                        Settings().set('server', 'port', port)# TODO use a loop to check list of `ports` and set `port` in settings file with right `port`
                        Settings().add_recent_connection(ip_address) # TODO create another key `ports` in `recent_connections` settings.json
                        self.on_ui_thread(success,args=[pc_name,ip_address])
                        print("Broadcast Worked found Port 🥳🥳🥳")
                else:
                    try_old_ports()
            except Exception as e:
                print("Finding Server - Auto Connect Error: ", get_full_class_name(e))
                try_old_ports()
                    
        threading.Thread(target=__auto_connect).start()

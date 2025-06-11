import os
import shutil
import time

import requests
import threading
import traceback

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from android_notify import Notification, NotificationStyles
from android_notify.config import from_service_file, run_on_ui_thread
from utils.helper import getAppFolder,get_full_class_name,urlSafePath,getFormat
from utils.config import Settings
from .networkmanager import NetworkManager

if not from_service_file():
    from components.popup import Snackbar
    from kivy.clock import Clock
else:
    def Snackbar(**kwargs):
        print('A fall back Snackbar async_requests')

    class Clock:
        def schedule_once(self,callback,secs):
            print('A fall back Clock async_requests',self)

from utils.constants import IMAGE_FORMATS, PORTS
Notification.logs = False


class ProgressData:
    # Monitor LookAlike
    def __init__(self,bytes_read,len_):
        self.bytes_read=bytes_read
        self.len=len_


class AsyncRequest:
    "notification_id is for service file"
    def __init__(self,notifications=True,notification_id=0):
        self.notifications = notifications
        self.download_notification= None
        self.notification_id= notification_id
        self.upload_notification= None
        self.percent=0 # Don't share Instances
        self.cancel_download = False
        self.cancel_upload = False
        self.running=True
        self.file_name=None
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

    @run_on_ui_thread
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
    
    def do_failed(self,failed,args:list=[]):
        print('This is args: ',args)
        if failed:
            self.on_ui_thread(failed,args)
        
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
        if not self.notifications:
            return
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
        if not self.notifications:
            return
        print('Sent file_name', file_name)
        self.download_notification = Notification(
                id=self.notification_id,
                title="Downloaded (0%)",
                message=file_name,
                style=NotificationStyles.PROGRESS,
                progress_max_value=100,progress_current_value=0.5,
                channel_name='Downloads'
                    # TODO use notification groups
                )
        def cancel_download_method():
            self.cancel_download=True
        self.download_notification.addButton('Cancel',on_release=cancel_download_method)
        self.download_notification.send()

    def update_progress(self,monitor,notification:Notification,type_):
        if not self.notifications:
            return
        new_percent = int((monitor.bytes_read / monitor.len) * 100)
        if new_percent >= 100:
            notification.removeButtons()
            notification.removeProgressBar(title=f'Completed {type_}',message=self.file_name)
        elif new_percent != self.percent:
            # print(f"{type_}ing ({new_percent}%)")
            self.percent=new_percent
            # notification.logs=True
            notification.message=f" ({DownloadProgress(monitor.bytes_read,monitor.len).format()})"
            notification.title=f"{self.file_name}"
            notification.updateProgressBar(self.percent)
        
    def download_file(self, file_path,save_path,success,failed=None):
        file_name = os.path.basename(save_path)
        self.file_name=file_name
        print('download_file file_name:',file_name)
        def failed_download_notification(msg='Download Error!'):
            if not self.notifications:
                return
            self.download_notification.removeButtons()
            self.download_notification.removeProgressBar(title=msg)
            
        def _download():
            try:
                start = time.time()
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path}"
                response = requests.get(url, stream=True,timeout=(2,None))
                self.send_initial_download_notification(file_name)
                if response.status_code == 200:
                    # Get the total file size from the response headers (if available)
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 8192  # Adjust chunk size as needed
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:  # Filter out keep-alive chunks
                                if self.cancel_download:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress_data = ProgressData(bytes_read=downloaded,len_=total_size)
                                print(progress_data.bytes_read,'/',progress_data.len)
                                duration = time.time() - start
                                print(f"Duration: {duration:.2f} seconds")

                                self.update_progress(progress_data,self.download_notification,type_='Download')
                            else:
                                # If no content length header, just print downloaded bytes.
                                print(f"Downloaded: {downloaded} bytes")


                    if self.cancel_download:
                        failed_download_notification('Download Cancelled!')
                        Clock.schedule_once(lambda dt: Snackbar(h1="Download Cancelled"))
                    else:
                        self.successfull_download_notification(save_path)
                        self.on_ui_thread(success,[save_path])
                elif response.status_code == 404:
                    failed_download_notification("Server Couldn't find File")
                    print("Server Couldn't find File")
                    # self.on_ui_thread(Snackbar)
                    
                else:
                    failed_download_notification()
                    self.on_ui_thread(failed)
                    
            except Exception as e:
                print("Failed Download Error type: ",e)
                failed_download_notification()
                traceback.print_exc()
                self.on_ui_thread(failed)
            finally:
                self.running=False
        # if from_service_file():
        #     _download()
        #     print('python using straight function')
        # else:
        threading.Thread(target=_download).start()

    def upload_file(self, file_path, save_path,success,failed=None,file_data=None):
        file_basename = os.path.basename(file_path)        
        self.file_name=file_basename

        def send_initial_upload_notification():
            if not self.notifications:
                return
            self.upload_notification = Notification(
                id=self.notification_id,
                title="Uploading (0%)",
                message=file_basename,
                style=NotificationStyles.PROGRESS,
                progress_max_value=100,progress_current_value=0.5,
                channel_name="Uploads"
                )
            def cancel_upload_method():
                self.cancel_upload=True
            self.upload_notification.addButton('Cancel',on_release=cancel_upload_method)
            self.upload_notification.send()
        
        def failed_upload_notification(msg='Upload Error!'):
            if not self.notifications:
                return
            self.upload_notification.removeButtons()
            self.upload_notification.removeProgressBar(title=msg)
            
        def update_progress(monitor):
            if not self.notifications:
                return
            if self.cancel_upload:
                failed_upload_notification("Upload Cancelled!")
                Clock.schedule_once(lambda dt: Snackbar(h1="Upload Cancelled"))
                raise Exception("Upload canceled by user")
            self.update_progress(monitor,notification=self.upload_notification,type_='Upload')
        
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
                send_initial_upload_notification()
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
                    failed_upload_notification()
                    Clock.schedule_once(lambda dt:Snackbar(h1=f'Upload Failed - Code {response.status_code}'))
                    self.on_ui_thread(failed)
                if self.notifications:
                    self.upload_notification.removeButtons()

            except Exception as e:
                if not self.cancel_upload:
                    failed_upload_notification()
                    self.on_ui_thread(failed)
                    print("Failed Upload ",e)
                    traceback.print_exc()

            finally:
                self.running=False
                
        if from_service_file():
            __upload()
        else:
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
            def _failed(e):
                print("Finding Server - Auto Connect Error: ", e)
                try_old_ports()
            self.find_server_with_ports(success=success,failed=_failed)
                    
        threading.Thread(target=__auto_connect).start()

    def find_server_with_ports(self,success,failed=None) -> None:
        def scan():
            try:
                timeout = .3
                for each_port in PORTS:
                    ip_address = NetworkManager().find_server(each_port,timeout=.2)
                    # timeout for scanning port needs to be longer than sleep time when broadcasting in desktop/workers/sword.py 
                    # TODO Remove Sleep for NetworkManager.find_server method and hardcode timeout
                    # print('trying port: ',each_port)
                    if ip_address:
                        # print(f"Connecting to server at {ip_address}")
                        try:
                            response=requests.get(f"http://{ip_address}:{each_port}/ping",json={'passcode':'08112321825'},timeout=timeout)
                            if response.status_code == 200:
                                pc_name = response.json()['data']
                                Settings().set('server', 'ip', ip_address)
                                Settings().set('server', 'port', each_port)# TODO use a loop to check list of `ports` and set `port` in settings file with right `port`
                                Settings().add_recent_connection(ip_address) # TODO create another key `ports` in `recent_connections` settings.json
                                self.on_ui_thread(success,args=[pc_name,ip_address])
                                return # Ending the function and Loop
                        except Exception as e:
                            print('For Loop error Not Suppose to happen Take a Look !!!',get_full_class_name(e))
            except Exception as e:
                
                self.do_failed(failed,[get_full_class_name(e)])
                print("Finding Server - Auto Connect Error: ", get_full_class_name(e))
                return
            # InCase where no Error in function and still couldn't find server
            self.do_failed(failed,['No Error | No Server'])
                
        threading.Thread(target=scan).start()

    def ping(self,input_ip_address,port,success,failed):
        def __ping():
            try:
                response=requests.get(f"http://{input_ip_address}:{port}/ping",json={'passcode':'08112321825'},timeout=.2)
                if response.status_code == 200:
                    self.on_ui_thread(success,[response.json()['data']])
                else:
                    self.on_ui_thread(failed)
            except Exception as e:
                print('Failed Ping',e)
                self.on_ui_thread(failed)
        threading.Thread(target=__ping).start()

def format_progress(downloaded_bytes, total_bytes):
    if total_bytes <= 0:
        return "0/0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    base = 1024
    index = 0

    # Use total_bytes to determine the best display unit
    value = float(total_bytes)
    while value >= base and index < len(units) - 1:
        value /= base
        index += 1

    unit = units[index]

    # Convert both downloaded and total to that unit
    downloaded = downloaded_bytes / (base ** index)
    total = total_bytes / (base ** index)

    # Round or floor to integers
    return f"{int(downloaded)}/{int(round(total))} {unit}"



class DownloadProgress:
    def __init__(self, downloaded_bytes, total_bytes):
        if downloaded_bytes < 0 or total_bytes < 0:
            raise ValueError("Byte values cannot be negative.")
        self.downloaded = downloaded_bytes
        self.total = total_bytes
        self.units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        self.base = 1024

    def _format_value(self, byte_val):
        index = 0
        value = float(byte_val)

        while value >= self.base and index < len(self.units) - 1:
            value /= self.base
            index += 1

        return f"{int(value)} {self.units[index]}"

    def _format_total_fixed_unit(self):
        index = 0
        value = float(self.total)

        while value >= self.base and index < len(self.units) - 1:
            value /= self.base
            index += 1

        return value, index, self.units[index]

    def format(self):
        if self.total == 0:
            return "0 B / 0 B"

        # Get total formatted and its unit index
        _, total_index, total_unit = self._format_total_fixed_unit()

        # Convert downloaded to appropriate unit for itself
        downloaded_str = self._format_value(self.downloaded)

        # Convert total to the fixed unit
        total_val = self.total / (self.base ** total_index)
        total_str = f"{int(total_val)} {total_unit}"

        return f"{downloaded_str} / {total_str}"

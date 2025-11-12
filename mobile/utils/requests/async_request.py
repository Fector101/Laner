import os, time, shutil
import requests, threading, traceback
import math

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from android_notify import Notification, NotificationStyles
from android_notify.config import from_service_file, run_on_ui_thread
from utils.helper import getAppFolder,get_full_class_name,urlSafePath,getFormat
from utils.config import Settings
from .networkmanager import NetworkManager

if not from_service_file():
    from ui.components.popup import Snackbar
    from kivy.clock import Clock
else:
    def Snackbar(**kwargs):
        print('A fall back Snackbar async_requests')

    class Clock:
        def schedule_once(self,callback=None,secs=None):
            print('A fall back Clock async_requests',self)

from utils.constants import IMAGE_FORMATS, PORTS
Notification.logs = True


class ProgressData:
    # Monitor LookAlike
    def __init__(self,bytes_read,len_):
        self.bytes_read=bytes_read
        self.len=len_


class AsyncRequest:
    "notification_id is for service file"
    def __init__(self,notifications=True,notification_id=0):
        self.show_notifications = notifications
        self.download_notification= None
        self.notification_id= notification_id
        self.upload_notification= None
        self.percent=0 # Don't share Instances
        self.cancel_download = False
        self.cancel_upload = False
        self.running=True
        self.file_name=None
        self.monitor= ProgressData(0,0) # type hinting
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
        if not fun or from_service_file():
            if from_service_file():
                print("Didn't run UI thread fun -AsyncRequest.on_ui_thread")
            return
        try:
            if args:
                Clock.schedule_once(lambda dt:fun(*args))
            else:
                Clock.schedule_once(lambda dt:fun())
        except Exception as e:
            print('Failed to execute function on ui Thread: ',e)
            traceback.print_exc()

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
        if not self.show_notifications:
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

    def send_initial_download_notification(self):
        if not self.show_notifications:
            return
        self.download_notification = Notification(
                id=self.notification_id,
                title=self.file_name,
                message='-/-',
                progress_max_value=100,progress_current_value=0,
                channel_name='Downloads'
                    # TODO use notification groups
                )
        try:
            self.download_notification.setColor('green')
        except Exception as e_:
            print("SetColor error:",e_)
        def cancel_download_method():
            self.cancel_download=True
        self.download_notification.addButton('Cancel download',on_release=cancel_download_method)
        self.download_notification.send()

    def update_progress(self,monitor,notification:Notification,type_,callback):
        if not self.show_notifications:
            return
        new_percent = int((monitor.bytes_read / monitor.len) * 100)
        if new_percent >= 100:
            notification.removeButtons()
            notification.removeProgressBar(title=f'Completed {type_}', message=self.file_name, _callback=callback)
        elif new_percent != self.percent:
            # print(f"{type_}ing ({new_percent}%)")
            self.percent=new_percent
            # notification.logs=True
            notification.message=f"{DownloadProgress(monitor.bytes_read,monitor.len).format()}"
            notification.title=f"{self.file_name}"
            notification.updateProgressBar(self.percent, _callback=callback)
        
    def download_file(self, file_path,save_path,success,failed=None):
        file_name = os.path.basename(save_path)
        self.file_name=file_name
        # print('download_file file_name:',file_name)
        def failed_download_notification(msg='Download Error!'):
            if not self.show_notifications:
                return
            self.download_notification.removeButtons()
            self.download_notification.removeProgressBar(title=msg)


        def _download():
            try:
                # start = time.time()
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path}"
                response = requests.get(url, stream=True,timeout=(2,None))
                self.send_initial_download_notification()
                if response.status_code == 200:
                    # Get the total file size from the response headers (if available)
                    total_size = int(response.headers.get('Content-Length', 0))
                    self.monitor.len = total_size
                    if self.show_notifications:
                        self.download_notification.updateMessage(DownloadProgress(0,total_size).format())
                    downloaded_size = 0
                    self.monitor.bytes_read = 0
                    chunk_size = 8192  # Adjust chunk size as needed
                    start_time = time.time()

                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:  # Filter out keep-alive chunks
                                if self.cancel_download:
                                    break
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                self.monitor.bytes_read = downloaded_size
                                time_left=self.__get_download_speed(start_time)
                                # print(time_left)
                                if self.show_notifications:
                                    progress_data = ProgressData(bytes_read=downloaded_size,len_=total_size)
                                    self.update_progress(
                                        progress_data,self.download_notification, type_='Download',
                                        callback=lambda : self.setDownloadSpeed(time_left)
                                    )

                                # duration = time.time() - start
                                # print(f"Duration: {duration:.2f} seconds")
                            else:
                                # If no content length header, just print downloaded bytes.
                                print(f"Downloaded: {downloaded_size} bytes")


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

        def send_initial_upload_notification(file_size):
            if not self.show_notifications:
                return
            self.upload_notification = Notification(
                id=self.notification_id,
                title=self.file_name,
                message=DownloadProgress(0,file_size).format(),
                style=NotificationStyles.PROGRESS,
                progress_max_value=100,progress_current_value=0,
                channel_name="Uploads"
                )
            def cancel_upload_method():
                self.cancel_upload=True
            self.upload_notification.addButton('Cancel upload',on_release=cancel_upload_method)
            self.upload_notification.send()
        
        def failed_upload_notification(msg='Upload Error!'):
            if not self.show_notifications:
                return
            self.upload_notification.removeButtons()
            self.upload_notification.removeProgressBar(title=msg)

        start_time=0
        def update_progress(monitor):
            nonlocal start_time
            if not self.show_notifications:
                return
            if self.cancel_upload:
                failed_upload_notification("Upload Cancelled!")
                Clock.schedule_once(lambda dt: Snackbar(h1="Upload Cancelled"))
                raise Exception("Upload canceled by user")

            time_left = self.__get_download_speed(start_time)  if start_time else ''# need to calculate time
            # before putting in AN progressbar wait timer
            self.update_progress(
                monitor,notification=self.upload_notification,type_='Upload',
                callback=lambda: self.setDownloadSpeed(time_left)
            )
            start_time = time.time()


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
                self.monitor = MultipartEncoderMonitor(encoder, update_progress)
                send_initial_upload_notification(file_size=self.monitor.len)

                response = requests.post(
                                        url, data=self.monitor,
                                        headers={'Content-Type': self.monitor.content_type},
                                        timeout=(2,None)
                                         )
                

                if response.status_code == 200:
                    self.on_ui_thread(success)
                else:
                    failed_upload_notification()
                    Clock.schedule_once(lambda dt:Snackbar(h1=f'Upload Failed - Code {response.status_code}'))
                    self.on_ui_thread(failed)
                if self.show_notifications:
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

    def __get_download_speed(self,start_time):
        elapsed = time.time() - start_time
        speed = self.monitor.bytes_read / elapsed if elapsed > 0 else 0
        remaining = self.monitor.len - self.monitor.bytes_read
        return DownloadProgress.time_left_formatted(remaining, speed)

    def setDownloadSpeed(self,text):
        if not self.show_notifications:
            return
        if self.download_notification:
            self.download_notification.setSubText(text)
        elif self.upload_notification:
            self.upload_notification.setSubText(text)

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
        self.downloaded = downloaded_bytes  # Using property setters
        self.total = total_bytes
        self._units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
        self.base = 1024

    @property
    def downloaded(self):
        return self._downloaded

    @downloaded.setter
    def downloaded(self, value):
        if value < 0:
            raise ValueError("Byte values cannot be negative.")
        self._downloaded = value

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        if value < 0:
            raise ValueError("Byte values cannot be negative.")
        self._total = value

    def _unit_index(self, byte_val):
        if byte_val == 0:
            return 0
        index = int(math.log(byte_val, self.base))
        return min(index, len(self._units) - 1)

    def _format_value(self, byte_val):
        index = self._unit_index(byte_val)
        value = byte_val / (self.base ** index)
        return f"{round(value, 2)} {self._units[index]}"

    def format(self):
        if self.total == 0:
            return "0 B / 0 B"

        total_index = self._unit_index(self.total)
        total_val = self.total / (self.base ** total_index)
        total_str = f"{round(total_val, 2)} {self._units[total_index]}"

        downloaded_str = self._format_value(self.downloaded)

        return f"{downloaded_str} / {total_str}"

    def __str__(self):
        return self.format()

    def percentage(self):
        if self.total == 0:
            return 0.0
        return (self.downloaded / self.total) * 100

    @staticmethod
    def time_left_formatted(remaining, rate):
        if rate <= 0:
            return ''
        seconds = remaining / rate
        if seconds < 60:
            secs=int(seconds)
            return f"{secs} secs left" if secs else ''
        elif seconds < 3600:
            return f"{int(seconds / 60)} mins left"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hrs left"
        else:
            return f"{int(seconds / 86400)} days left"

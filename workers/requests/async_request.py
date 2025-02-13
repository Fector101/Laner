import threading,requests,os,shutil
from kivy.clock import Clock
from workers.helper import getAppFolder,get_full_class_name
from workers.sword import Settings,NetworkManager
from widgets.popup import Snackbar
#  getHiddenFilesDisplay_State, makeDownloadFolder, 
import traceback

class AsyncRequest:
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
        file_path_url_safe=path.replace(' ', '%20').replace('\\', '/')
        file_url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path_url_safe}"
        def __make_request():
            try:
                response = requests.get(url,json={'path':path},timeout=3)
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
        
        
    def download_file(self, file_path,save_path,success,failed=None):
        def _download():
            try:
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path}"
                
                response = requests.get(url)
                file_name = os.path.basename(save_path)
                print("This is file name: ", file_name)
                print("This is save_path: ", save_path)
                with open(save_path, "wb") as file:
                    file.write(response.content)
                self.on_ui_thread(success)
            except Exception as e:
                print("Failed Download Error type: ",e)
                traceback.print_exc()
                self.on_ui_thread(failed)
        threading.Thread(target=_download).start()
    # def log_failed_msg(self,fail_func):
    #     if fail_func:
    #         Clock.schedule_once(lambda dt:fail_func())
    def upload_file(self, file_path, save_path,success,failed=None,file_data=None):
        def __upload():
            try:
                url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/upload"
                files = {'file': file_data if file_data else open(file_path, 'rb')}
                response = requests.post(url, data={'save_path': save_path},files=files)
                if response.status_code == 200:
                    self.on_ui_thread(success)
                else:
                    Clock.schedule_once(lambda dt:Snackbar(h1=f'Upload Failed - Code {response.status_code}'))
                    self.on_ui_thread(failed)
                # Refresh the folder.
            except Exception as e:
                self.on_ui_thread(failed)
                print("Failed Upload ",e)
                traceback.print_exc()
                
        threading.Thread(target=__upload).start()
    def auto_connect(self,success,failed=None):
        def try_old_ports():
            print("Trying old ports and ip's...")
            pervious_connections=Settings().get_recent_connections()
            port=Settings().get("server", "port")
            for ip_address in pervious_connections:
                try:
                    print('trying... ',ip_address,port)
                    response=requests.get(f"http://{ip_address}:{port}/ping",json={'passcode':'08112321825'},timeout=.4)
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
            timeout=0.5
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

# instance = AsyncRequest()
# instance.is_folder('path',function)
# instance.download_file('save_path')
# instance.upload_file('file_path',file_data='ewewe')

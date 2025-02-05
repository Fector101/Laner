from kivymd.app import MDApp
from kivy.properties import ( ListProperty, StringProperty, BooleanProperty,ColorProperty,ObjectProperty,NumericProperty)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFabButton
from kivy.uix.recycleview import RecycleView
from widgets.header import Header
from kivy.clock import Clock
import threading
from kivy.uix.label import Label
import asyncio
import requests
import os
from pathlib import Path
from widgets.popup import PopupDialog,Snackbar
from android_notify import send_notification,Notification,NotificationStyles
from plyer import filechooser
from workers.helper import getHiddenFilesDisplay_State,makeDownloadFolder,getAppFolder
from kivy.lang import Builder
import shutil
from kivy.utils import platform # OS


if platform == 'android':
    from kivymd.toast import toast
    from workers.filechooser import AndroidFileChooser

my_downloads_folder=makeDownloadFolder()

kv_file_path= [getAppFolder(),"widgets","screens","folderscreen.kv"]
with open( os.path.join(*kv_file_path), encoding="utf-8" ) as kv_file:
    Builder.load_string(kv_file.read(), filename="folderscreen.kv")

class RV(RecycleView):
    """Reuse widgets for Speed

    Args:
        RecycleView (RecycleView): kivy's RecycleView
    """

class DetailsLabel(Label):
    """style label"""

class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint={'top': 1}
        self.app=MDApp.get_running_app()
        self.screen_history = []
        self.data_received=False
        self.current_dir_info:list[dict]=[]
        self.could_not_open_path_msg="Couldn't Open Folder Check Laner on PC"
        # self.md_bg_color=[1,1,0,1]
        self.layout=MDBoxLayout(orientation='vertical')

        self.header=Header(screen=self,
                           text=self.current_dir,
                           
                           text_halign='center',
                           theme_text_color='Primary',
                           title_color=self.theme_cls.primaryColor,
                           )
        self.layout.add_widget(self.header)

        self.screen_scroll_box = RV()
        # self.screen_scroll_box.children[0].bind(height=self.spinner.setter('y'))
        
        
        self.screen_scroll_box.data=self.current_dir_info
        # Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())

        self.layout.add_widget(self.screen_scroll_box)
        self.upload_btn=MDFabButton(
                icon="upload",
                style= "standard",
                pos_hint={"center_x": .82, "center_y": .25},
                on_release=lambda x:self.choose_file()
        )
        
        # Adding directory details
        self.details_box=MDRelativeLayout(
            height='35sp',
            adaptive_width=True,
            md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1],
            size_hint=[1,None]
            )
        
        self.details_label=DetailsLabel(text='0 files and 0 folders')
        
        
        self.details_box.add_widget(self.details_label)
        self.layout.add_widget(self.details_box)
        self.layout.add_widget(MDBoxLayout(height='70sp',size_hint=[1,None]))  # Buffer cause of bottom nav bar (will change to padding later)
        self.add_widget(self.layout)
        self.add_widget(self.upload_btn)

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
    def lastFolderScreen(self):
        if self.screen_history:
            last_dir = self.screen_history.pop()
            self.setPath(last_dir, False)
            
    def getSERVER_IP(self):
        return self.app.settings.get('server', 'ip')
    def getPortNumber(self):
        return self.app.settings.get('server', 'port')
    async def uploadFile(self,file_path,file_data=False):
        try:
            response = requests.post(
                f"http://{self.getSERVER_IP()}:{self.getPortNumber()}/api/upload",
                data={'save_path': self.current_dir},
                files={'file': file_data if file_data else open(file_path, 'rb')},timeout=0
                            )
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1='Connection Error Check Laner on PC'))
                return
            Clock.schedule_once(lambda dt:Snackbar(h1="File Uploaded Successfully"))
            try:
                Notification(title='Completed upload',message=os.path.basename(file_path),channel_name="Upload Completed").send()
            except Exception as e:
                print(e,"Failed sending Notification")
            Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1="Failed to Upload File check Laner on PC"))
            print(e,"Failed Upload")
            
    def startUpload_Thread(self,file_path,file_data):
        def queryUploadAsync():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.uploadFile(file_path,file_data=file_data))
            loop.close()
        threading.Thread(target=queryUploadAsync).start()
    def choose_file(self):
        print('choosing file...')
        def parseAnswer(file_name,file_data,file_path):
            print('received file_name ',file_name)
            print("received file_data ",file_data[:10])
            print('received file_path ',file_path)
                # self.startUpload_Thread(file_path='d/',file_data=file_data)
            # if file_path:
            #     self.startUpload_Thread(file_path if isinstance(file_path,str) else file_path[0])
                # self.img.source=file_path[0]
        # filechooser.open_file(on_selection=test1)
        if platform == 'android':
            result = AndroidFileChooser(callback=parseAnswer)
            # print('result ===> ', result)
        # Bind the result callback
        # try:
        #     context =  activity.getApplicationContext()
        #     print(f"Package Name: {context.getPackageName()}")
        # except Exception as e:
        #     print('Failed getting package',e)
        # filechooser.open_file(on_selection=lambda x: print(x))
    
    def startSetPathInfo_Thread(self,frm_btn_bool=False):
        threading.Thread(target=self.querySetPathInfoAsync,args=[frm_btn_bool]).start()
        
    def querySetPathInfoAsync(self,frm_btn_bool):
        # Run the async function in the event loop
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncSetPathInfo(frm_btn_bool))
        loop.close()
                     
    async def asyncSetPathInfo(self,frm_btn_bool):
        print(frm_btn_bool)
        try:
            response = requests.get(f"http://{self.getSERVER_IP()}:{self.getPortNumber()}/api/getpathinfo",json={'path':self.current_dir},timeout=5)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return
            self.current_dir_info=[]
            no_of_files=0
            no_of_folders=0
            def increase_no_of_files():
                nonlocal no_of_files
                no_of_files+=1
            def increase_no_of_folders():
                nonlocal no_of_folders
                no_of_folders+=1
            
            file_data = response.json()['data']
            show_hidden = getHiddenFilesDisplay_State()
            # print(file_data,'|||',show_hidden)
            for item in file_data:
                # Skip hidden files if not showing them
                if not show_hidden and item['text'].startswith('.'):
                # if not show_hidden and item['text'].startswith('.'):
                    continue
                    
                self.current_dir_info.append(item)
                
                # Update counters
                if item['is_dir']:
                    increase_no_of_folders()
                else:
                    increase_no_of_files()
                    
            parse_for_files='files' if no_of_files > 1 else 'file'
            parse_for_folders='folders' if no_of_folders > 1 else 'folder'
            self.details_label.text=f'{no_of_files} {parse_for_files} and {no_of_folders} {parse_for_folders}'
            self.screen_scroll_box.data=self.current_dir_info
            grey_i = .44
            if not self.screen_history:
                self.header.back_btn.color = [grey_i,grey_i,grey_i,1] # no need to change color in App toogle_theme method since this method will get called everytime user enters screen
            else:
                self.header.back_btn.color=self.header.saved_theme_color

            if frm_btn_bool and platform == 'android':
                toast("Refresh Done")
                    
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print("Failed opening Folder async ",e)
            
    def isDir(self,path:str):

        try:
            response=requests.get(f"http://{self.getSERVER_IP()}:{self.getPortNumber()}/api/isdir",json={'path':path},timeout=3)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return False
            return response.json()['data']

        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(f"isDir method: {e}")
            return 404
    def setPath(self,path,add_to_history=True):
        if self.isDir(path) != 404 and not self.isDir(path):
            self.manager.btm_sheet.enable_swiping=True
            self.manager.btm_sheet.set_state("toggle")
            
            return
        if add_to_history:  # Saving Last directory for screen history
            self.screen_history.append(self.current_dir)

        self.current_dir = path
        self.header.changeTitle(path)
        # self.setPathInfo()
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        
    def showDownloadDialog(self,path:str):
        """Shows Dialog box with choosen path and calls async download if ok press"""
        if self.isDir(path) == 404 or self.isDir(path):
            return
        
        file_name = os.path.basename(path.replace('\\', '/'))
        def failedCallBack():...
        def successCallBack():
            needed_file = f"http://{self.getSERVER_IP()}:{self.getPortNumber()}/{path}"
            url = needed_file.replace(' ', '%20').replace('\\', '/')
            
            saving_path = os.path.join(my_downloads_folder, file_name)
            threading.Thread(target=self.b_c,args=(url, saving_path)).start()
            
        PopupDialog(
                failedCallBack=failedCallBack,successCallBack=successCallBack,
                h1="Verify Download",
                caption=f"{file_name} -- Will be saved in \"Laner\" Folder in your device \"Downloads\"",
                cancel_txt="Cancel",confirm_txt="Ok",
        )
    def b_c(self,url, save_path):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download_file(url, save_path))

   
async def async_download_file(url, save_path):
    try:
        response = requests.get(url)
        file_name = os.path.basename(save_path)
        print("This is file name: ", file_name)
        print("This is save_path: ", save_path)
        with open(save_path, "wb") as file:
            file.write(response.content)
        try:
            
            PICTURE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif')
            if os.path.splitext(file_name)[1] in PICTURE_FORMATS:
                shutil.copy(save_path, os.path.join(getAppFolder(), 'assets', 'imgs', file_name))
                Notification(title="Completed download",message=file_name,style=NotificationStyles.LARGE_ICON,big_picture_path=save_path,channel_name="Download Completed").send()
            else:
                send_notification("Completed download", file_name,channel_name="Download Completed")
        except Exception as e:
            print(e,"Failed sending Notification")
            pass
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { file_name }'))
    except Exception as e:
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1="Download Failed try Checking Laner on PC"))
        print(e,"Failed Download")
     
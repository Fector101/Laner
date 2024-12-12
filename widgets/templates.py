from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.recycleview import RecycleView
from kivy.metrics import dp,sp
from kivy.properties import ( ListProperty, StringProperty)
from kivy.clock import Clock
# from app_settings import SHOW_HIDDEN_FILES

import threading
import asyncio
import requests
import os
from pathlib import Path

from widgets.popup import PopupDialog,Snackbar
from workers.helper import getSERVER_IP, getSystem_IpAdd, makeDownloadFolder, truncateStr,getHiddenFilesDisplay_State



my_downloads_folder=makeDownloadFolder()


class Header(MDBoxLayout):
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (.2, .2, .2, .5)
        self.header_label=MDLabel(
            text_color=self.title_color,
            text='~ '+self.text if self.text == 'Home' else self.text,
            halign=self.text_halign,
            valign='center',
            shorten_from='center',
            shorten=True,

            )
        if self.text_halign == 'left':
            self.header_label.padding=[sp(40),0,0,0]
        else:
            self.header_label.padding=[sp(10),0,sp(10),0]

        self.add_widget(self.header_label)
    def changeTitle(self,text):
        self.header_label.text='~ '+ text if text == 'Home' else text
        


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV,self).__init__(**kwargs)


async def async_download_file(url, save_path):
    try:
        response = requests.get(url)
        file_name = save_path
        file_path = os.path.join(my_downloads_folder, file_name)
        with open(file_path, "wb") as file:
            file.write(response.content)
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { truncateStr(Path(file_path).parts[-1],10) }'))
    except Exception as e:
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1="Download Failed try Checking Laner on PC"))
        print(e,"Failed Download")
        
class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_history = []
        self.current_dir_info:list[dict]=[]
        self.could_not_open_path_msg="Couldn't Open Folder Check Laner on PC"
        self.layout=MDBoxLayout(md_bg_color=[.4,.4,.4,1],orientation='vertical')
        self.header=Header(
                           text=self.current_dir,
                           size_hint=[1,.1],
                           text_halign='center',
                           title_color=self.theme_cls.backgroundColor,
                           )
        self.layout.add_widget(self.header)

        self.screen_scroll_box = RV()
        self.screen_scroll_box.data=self.current_dir_info
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        

        self.layout.add_widget(self.screen_scroll_box)
        self.add_widget(self.layout)

    def startSetPathInfo_Thread(self):
        threading.Thread(target=self.querySetPathInfoAsync).start()
        
    def querySetPathInfoAsync(self):
        # Run the async function in the event loop
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncSetPathInfo())
        loop.close()
    async def asyncSetPathInfo(self):
        try:
            response = requests.get(f"http://{getSERVER_IP()}:8000/api/getpathinfo",json={'path':self.current_dir},timeout=5)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return
            self.current_dir_info=[]
            for each_name in response.json()['data']:
                if not getHiddenFilesDisplay_State() and each_name['text'][0] != '.':
                    self.current_dir_info.append(each_name)
                elif getHiddenFilesDisplay_State():
                    self.current_dir_info.append(each_name)
                    
            self.screen_scroll_box.data=self.current_dir_info

        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(e,"Failed opening Folder async")
                   
    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
   
            
    def isDir(self,path:str):

        try:
            response=requests.get(f"http://{getSERVER_IP()}:8000/api/isdir",json={'path':path},timeout=3)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return False
            return response.json()['data']

        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(f"isDir method: {e}")
            return False
    def setPath(self,path,add_to_history=True):
        if not self.isDir(path):
            return
        if add_to_history:  # Saving Last directory for screen history
            self.screen_history.append(self.current_dir)

        self.current_dir = path
        self.header.changeTitle(path)
        # self.setPathInfo()
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        
    def showDownloadDialog(self,path:str):
        """Shows Dialog box with choosen path and calls async download if ok press"""
        if (self.isDir(path)):
            return
        
        file_name = os.path.basename(path.replace('\\', '/'))
        def failedCallBack():...
        def successCallBack():
            needed_file = f"http://{getSERVER_IP()}:8000/{path}"
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

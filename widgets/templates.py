from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.recycleview import RecycleView
from kivy.metrics import dp,sp
from kivy.properties import ( ListProperty, StringProperty, BooleanProperty,ColorProperty,ObjectProperty,NumericProperty)
from kivy.clock import Clock
from kivy.core.window import Window
# from app_settings import SHOW_HIDDEN_FILES

import threading
import asyncio
import requests
import os
from pathlib import Path
from plyer import filechooser

from widgets.popup import PopupDialog,Snackbar
from workers.helper import getAppFolder, getSERVER_IP, getSystem_IpAdd, is_wine, makeDownloadFolder, truncateStr,getHiddenFilesDisplay_State, wine_path_to_unix

from kivy.lang import Builder

# TODO Fix get app folder worker/helper.py returning app folder as /Laner/workers/
import sys
from kivymd.uix.button import MDFabButton,MDExtendedFabButtonIcon,MDExtendedFabButtonText
def getAppFolder1():
    """
    Returns the correct application folder path, whether running on native Windows,
    Wine, or directly in Linux.
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller creates a temp folder (_MEIPASS)
        path__ = os.path.abspath(sys._MEIPASS)
    else:
        # Running from source code
        path__ = os.path.abspath(os.path.dirname(__file__))
        
    if is_wine():
        path__ = wine_path_to_unix(path__)
    return path__
with open(os.path.join(getAppFolder1(),"templates.kv"), encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="MyBtmSheet.kv")


from kivy.utils import get_color_from_hex
my_downloads_folder=makeDownloadFolder()


class Header(MDBoxLayout):
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (.1, .1, .1, .5)
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
     
from kivy.uix.label import Label
from kivymd.uix.relativelayout import MDRelativeLayout

class DetailsLabel(Label):
    pass
        
        
        
class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_history = []
        self.current_dir_info:list[dict]=[]
        self.could_not_open_path_msg="Couldn't Open Folder Check Laner on PC"
        self.size_hint=[1,None]
        self.height=Window.height-sp(47)   # Bottom nav height
        self.pos_hint={'top':1}
        # print(Window.height)
        
        self.md_bg_color=[1,1,0,1]
        self.layout=MDBoxLayout(orientation='vertical')
        self.header=Header(
                           text=self.current_dir,
                           size_hint=[1,.1],
                           text_halign='center',
                           title_color=self.theme_cls.backgroundColor,
                           )
        self.layout.add_widget(self.header)

        self.screen_scroll_box = RV()
        self.screen_scroll_box.data=self.current_dir_info
        # Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        

        self.layout.add_widget(self.screen_scroll_box)
        # icon.theme_text_color="Custom"
        # icon.text_color=[1,0,0,1]
        THEME_COLOR=(.12, .65, .46, 1)
        # THEME_COLOR=(.12, .85, .6, 1)
        self.upload_btn=MDFabButton(
                #FF0000
                icon="upload",
                style= "standard",
                # MDExtendedFabButtonIcon(,theme_text_color="Custom",text_color=THEME_COLOR),
                # MDExtendedFabButtonText(text="Upload",text_color=(.12, .55, .4, 1),theme_text_color="Custom"),
                pos_hint={"center_x": .82, "center_y": .19},
                # on_release=lambda x:self.choose_file()
        )
        # self.upload_btn.md_bg_color=[1,0,0,1]
        
        # Adding directory details
        container_for_group_label=MDRelativeLayout(
            height='35sp',
            adaptive_width=True,
            md_bg_color=[.15,.15,.15,1],size_hint=[1,None])
        group_label_container= MDBoxLayout(height='35sp',pos_hint={'center_x': 0.5},adaptive_width=True,spacing=sp(10),size_hint_y=None)
        group_label_container.add_widget(DetailsLabel(text='11 files, '))
        group_label_container.add_widget(DetailsLabel(text='5 folders, '))
        group_label_container.add_widget(DetailsLabel(text='35 mb, '))
        container_for_group_label.add_widget(group_label_container)
        self.add_widget(self.upload_btn)
        self.add_widget(self.layout)
        self.add_widget(container_for_group_label)
    def choose_file(self):
        print('printing tstex')
        def test1(file_path):
            print(file_path,'img path')
            # if file_path:
                # self.img.source=file_path[0]
        filechooser.open_file(on_selection=test1)

            
                
                
            
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
        # Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        ...
   
            
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

import asynckivy
# from asynckivy
from kivymd.uix.bottomsheet.bottomsheet import MDBottomSheet,MDBottomSheetDragHandle,MDBottomSheetDragHandleTitle,MDBottomSheetDragHandleButton

from kivy.properties import BoundedNumericProperty

class TypeMapElement(MDBoxLayout):
    selected = BooleanProperty(False)
    icon = StringProperty()
    title = StringProperty()
    
    def set_active_element(self, instance, type_map):
        # print(self.parent.children, instance, type_map)
        for element in self.parent.children:
            if instance == element:
                element.selected = True
                self.current_map = type_map
            else:
                element.selected = False

class MyBtmSheet(MDBottomSheet):
    sheet_type="standard"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super(MyBtmSheet,self).__init__(**kwargs)
        self.size_hint_y=None
        self.height='150dp'
        
        self.drag_sheet= MDBottomSheetDragHandle(
                            
                            
                            drag_handle_color= "grey"
                            )
        self.drag_sheet.add_widget(
            MDBottomSheetDragHandleTitle(
                # text= "Select type map",
                pos_hint= {"center_y": .5}
            )
        )
        self.drag_sheet.add_widget(
            MDBottomSheetDragHandleButton(
                               icon= "close",
                               ripple_effect= False,
                               on_release= lambda x: self.set_state("toggle")
                               )
        )

        self.content = MDBoxLayout(padding=[0, 0, 0, "16dp"])
        self.add_widget(self.drag_sheet)
        # self.generate_content()
        self.add_widget(self.content)
        # self.on_open=asynckivy.start(self.generate_content())
        
    async def generate_content(self):        
        
        icons = {
            "Download": "download",
            "Open with": "apps",
            "Share": "share",
        }
        map_sources = {
        "street": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "sputnik": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        }
        # await asynckivy.sleep(0)
        # print("test----|",self,'|||',self.content)
        # print(self.content.children)
        if not self.children:
            for i, title in enumerate(icons.keys()):
                await asynckivy.sleep(0)
                self.content.add_widget(
                    TypeMapElement(
                        title=title.capitalize(),
                        icon=icons[title],
                        selected=not i,
                    )
                )

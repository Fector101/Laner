from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText,MDButtonIcon,MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.metrics import dp,sp
from kivy.properties import ( ListProperty, StringProperty, BooleanProperty,ColorProperty,ObjectProperty,NumericProperty)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
# from app_settings import SHOW_HIDDEN_FILES
from android_notify import send_notification,Notification,NotificationStyles

import threading
import asyncio
import requests
import os
from pathlib import Path
from plyer import filechooser

from widgets.popup import PopupDialog,Snackbar
from workers.helper import THEME_COLOR_TUPLE, is_wine, makeDownloadFolder, truncateStr,getHiddenFilesDisplay_State, wine_path_to_unix,getAppFolder
from workers.sword import Settings

# TODO Fix get app folder worker/helper.py returning app folder as /Laner/workers/
import sys
from kivymd.uix.button import MDFabButton

import time
from kivy.utils import platform # OS
if platform == 'android':
    from kivymd.toast import toast

with open(os.path.join(getAppFolder(),"widgets","templates.kv"), encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="MyBtmSheet.kv")


from kivy.utils import get_color_from_hex
my_downloads_folder=makeDownloadFolder()
class RV(RecycleView):...

class HeaderBtn(MDFabButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
         # self.back_btn.radius=0
        self.theme_bg_color="Custom"
        self.theme_shadow_color="Custom"
        self.shadow_color=[0,0,0,0]
        self.md_bg_color=[0,0,0,0]
        
        self.font_size=sp(20)    
        size__=35
        self.size=[sp(size__),sp(size__)]

from kivymd.uix.menu import MDDropdownMenu
class Header(MDBoxLayout):
    """_summary_

    Args:
        text (str): _description_
        text_halign (str): _description_
        title_color (str): _description_
    """
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    theme_text_color=StringProperty()
    def __init__(self,screen, **kwargs):
        super().__init__(**kwargs)
        self.screen=screen
        self.md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1]
        self.size_hint=[1,None]
        self.height=sp(70)
        self.header_label=MDLabel(
            text_color=self.title_color,
            theme_text_color=self.theme_text_color,
            text='~ '+self.text if self.text == 'Home' else self.text,
            halign=self.text_halign,
            valign='center',
            shorten_from='left',
            shorten=True,
            # md_bg_color=[1,0,0,1]
            )
        if self.text_halign == 'left':
            self.header_label.padding=[sp(40),0,0,0]
        else:
            def fun():
                print(screen.manager.Android_back_click('_',27))
            self.back_btn = HeaderBtn(icon="arrow-left", style= "standard", pos_hint={"center_y": .5},x=sp(10))
            if isinstance(screen,DisplayFolderScreen):
                self.back_btn.on_release=screen.lastFolderScreen
            self.add_widget(self.back_btn)
            # self.header_label.padding=[sp(10),0,sp(10),0]
            self.padding=[sp(10),0,sp(10),0]

        self.add_widget(self.header_label)
        if self.text_halign != 'left':
            self.opts_btn = HeaderBtn(icon="dots-vertical", style= "standard", pos_hint={"center_y": .5},x=sp(10),on_release=lambda this:self.open_menu(this))
            self.add_widget(self.opts_btn)
        def u():
            self.header_label.text='/home/fabian/Documents/my-projects-code/packages'
        # Clock.schedule_once(lambda x:u(),2)
        self.dropDown = None
    def changeTitle(self,text):
        self.header_label.text='~ '+ text if text == 'Home' else text
    def open_menu(self, item):
        icons=['refresh',
        # 'file','folder'
        ]
        titles=['Refresh','New file','New folder']
        functions = [self.refreshBtnClicked,self.screen.startSetPathInfo_Thread,self.screen.startSetPathInfo_Thread]
        menu_items = [
            {
                "text": titles[i],
                'leading_icon': icons[i],
                'height': sp(45),
                
                "on_release": lambda real_index=i:functions[real_index](),
            } for i in range(len(icons))
        ]
        self.dropDown=MDDropdownMenu(caller=item, items=menu_items)
        self.dropDown.open()
    def refreshBtnClicked(self):
        self.screen.startSetPathInfo_Thread(frm_btn_bool='frm_btn')
        self.dropDown.dismiss()
        
import shutil
        
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
                send_notification("Completed download", file_name, style="large_icon", img_path=save_path,channel_name="Download Completed")
            else:
                send_notification("Completed download", file_name,channel_name="Download Completed")
        except Exception as e:
            print(e,"Failed sending Notification")
            pass
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { file_name }'))
    except Exception as e:
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1="Download Failed try Checking Laner on PC"))
        print(e,"Failed Download")
     
from kivy.uix.label import Label
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout

class DetailsLabel(Label):
    pass


from kivymd.app import MDApp

class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint={'top': 1}
        self.app=MDApp.get_running_app()
        self.screen_history = []
        
        # self.spinner = Grid(opacity=0)
        self.data_received=False
        self.current_dir_info:list[dict]=[]
        self.could_not_open_path_msg="Couldn't Open Folder Check Laner on PC"
        # self.md_bg_color=[1,1,0,1]
        self.layout=MDBoxLayout(orientation='vertical')

        absolute_layout = MDFloatLayout(pos_hint={'top':1},size_hint_y=None,height=sp(70))
        # absolute_layout.md_bg_color=[1,0,0,1]
        # absolute_layout.add_widget(self.back_btn)

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
        # self.add_widget(absolute_layout)
        
        # self.add_widget(self.spinner)
        
    def lastFolderScreen(self):
        if self.screen_history:
            last_dir = self.screen_history.pop()
            self.setPath(last_dir, False)
            
    def getSERVER_IP(self):
        return self.app.settings.get('server', 'ip')
    def getPortNumber(self):
        return self.app.settings.get('server', 'port')
    async def uploadFile(self,file_path):
        try:
            response = requests.post(
                f"http://{self.getSERVER_IP()}:{self.getPortNumber()}/api/upload",
                files={'file': open(file_path, 'rb')},
                data={'save_path': self.current_dir}
            )
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1='Connection Error Check Laner on PC'))
                return
            Clock.schedule_once(lambda dt:Snackbar(h1="File Uploaded Successfully"))
            try:
                
                send_notification("Completed upload", os.path.basename(file_path),channel_name="Upload Completed")
            except Exception as e:
                print(e,"Failed sending Notification")
            Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1="Failed to Upload File check Laner on PC"))
            print(e,"Failed Upload")
            
    def startUpload_Thread(self,file_path):
        def queryUploadAsync():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.uploadFile(file_path))
            loop.close()
        threading.Thread(target=queryUploadAsync).start()
    def choose_file(self):
        print('printing tstex')
        def test1(file_path):
            print(file_path,'choosen path')
            if file_path:
                self.startUpload_Thread(file_path if isinstance(file_path,str) else file_path[0])
                # self.img.source=file_path[0]
        filechooser.open_file(on_selection=test1)
        # filechooser.open_file(on_selection=lambda x: print(x))
        
                    
    def startSetPathInfo_Thread(self,frm_btn_bool=False):
        # print(self.data_received)
        threading.Thread(target=self.querySetPathInfoAsync,args=[frm_btn_bool]).start()
        # time.sleep(0.2)
        # if not self.data_received:
        #     self.pop_up = PopupDialog()
        
    def querySetPathInfoAsync(self,frm_btn_bool):
        # Run the async function in the event loop
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncSetPathInfo(frm_btn_bool))
        loop.close()
                     
    async def asyncSetPathInfo(self,frm_btn_bool):
        print(frm_btn_bool)
        try:
            # self.data_received=False
            
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
            # print('-----------------',self.current_dir_info)
            # return
                
            self.screen_scroll_box.data=self.current_dir_info
            if frm_btn_bool and platform == 'android':
                toast("Refresh Done")
            # self.data_received=True
            
            # self.pop_up.update_pop_up_text(self.name)
            
            # Clock.schedule_once(self.pop_up.close)
            
                    
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print("Failed opening Folder async ",e)
                   
    def on_enter(self, *args):
        # print(self.data_received)
        # Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        pass
        
        
            
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

import asynckivy
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
        self.height=sp(170)
        
        self.drag_sheet= MDBottomSheetDragHandle(
                            
                            
                            # drag_handle_color= "grey"
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
        self.add_widget(self.content)
        self.enable_swiping=0
        # self.generate_content()
        # self.set_state('close')
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
    def on_touch_move(self, touch):
        if self.enable_swiping:
            # if self.status == "closed":
            #     pass
            #     if (
            #         self.get_dist_from_side(touch.oy) <= self.swipe_edge_width
            #         and abs(touch.y - touch.oy) > self.swipe_distance
            #     ):
            #         self.status = "opening_with_swipe"
            if self.status == "opened" and abs(touch.y - touch.oy) > self.swipe_distance:
                self.status = "closing_with_swipe"

        if self.status == "closing_with_swipe":
            self.open_progress = max(
                min(
                    self.open_progress
                    + (touch.dy if self.anchor == "left" else -touch.dy)
                    / self.height,
                    1,
                ),
                0,
            )
            return True
        return super().on_touch_move(touch)
    def on_close(self, *args):
        self.enable_swiping=0
        return super().on_close(*args)
        

class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    # text_widget = ObjectProperty() # for on_text if statement to work
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.text = self.text
        self.theme_height = "Custom"
        self.theme_width = "Custom"


    # def on_text(self, instance, value):...
        # print(instance,'|||',value)
        # self.text = value
        # if self.text_widget:
        #     self.text_widget.text = value
        # if 'text_id' in self.ids:
        #     print(self.ids['text_id'],'iddsss')
        #     print(self.ids['text_id'].texture_size,'iddsss')




    
class CustomDropDown(MDBoxLayout):
    title = StringProperty("Advanced Options")
    # icon = StringProperty("arrow-down")
    is_open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.not_keeps_sake=[]      
    def toggle_dropdown(self):
        # print(self.is_open)
        # print(self.ids.dropdown_content.children,'pop')
        if self.is_open:
            self.ids.dropdown_content.clear_widgets()
            # self.ids.dropdown_content.height = 0
        else:
            for each in self.not_keeps_sake:
                self.ids.dropdown_content.add_widget(each)
            # self.ids.dropdown_content.height = self.ids.dropdown_content.minimum_height
        # print(self.ids.dropdown_content.children,'ffff')
            
        self.is_open = not self.is_open

    def add_widget(self, widget, index=0, canvas=None):
        if self.ids and 'dropdown_content' in self.ids:
            self.not_keeps_sake.append(widget)
            if self.is_open:
                self.ids.dropdown_content.add_widget(widget)
            # self.ids.dropdown_content.height = self.ids.dropdown_content.minimum_height
        else:
            super().add_widget(widget, index=index, canvas=canvas)        
            


# use for refresh, this function is from kivymd bottomsheet class
    # def on_touch_move(self, touch):
    #     if self.enable_swiping:
    #         if self.status == "closed":
    #             if (
    #                 self.get_dist_from_side(touch.oy) <= self.swipe_edge_width
    #                 and abs(touch.y - touch.oy) > self.swipe_distance
    #             ):
    #                 self.status = "opening_with_swipe"
    #         elif self.status == "opened":
    #             if abs(touch.y - touch.oy) > self.swipe_distance:
    #                 self.status = "closing_with_swipe"

    #     if self.status in ("opening_with_swipe", "closing_with_swipe"):
    #         self.open_progress = max(
    #             min(
    #                 self.open_progress
    #                 + (touch.dy if self.anchor == "left" else -touch.dy)
    #                 / self.height,
    #                 1,
    #             ),
    #             0,
    #         )
    #         return True
    #     return super().on_touch_move(touch)


# for android stuff
# from android.runnable import run_on_ui_thread

# @run_on_ui_thread
# def toast(text,
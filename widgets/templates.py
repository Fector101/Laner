from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
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
from workers.helper import THEME_COLOR_TUPLE, getAppFolder, getSERVER_IP, getSystem_IpAdd, is_wine, makeDownloadFolder, truncateStr,getHiddenFilesDisplay_State, wine_path_to_unix

from kivy.lang import Builder

# TODO Fix get app folder worker/helper.py returning app folder as /Laner/workers/
import sys
from kivymd.uix.button import MDFabButton
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1]
        
        self.header_label=MDLabel(
            text_color=self.title_color,
            theme_text_color=self.theme_text_color,
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
        

from kivy.uix.image import Image
from kivy.animation import Animation
angle=45
class Grid(GridLayout):
    anime = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_animating = False

    def stopLoadingAnime(self, *args):
        if self.is_animating:
            # Stop animation
            self.anime.unbind(on_complete=self.startLoadingAnime)
            self.is_animating = False

    def startLoadingAnime(self, *args):
        global angle
        print('buzzing.....',self.is_animating)
        # self.anime=Animation(height=40, width=40, spacing=[10, 10], duration=0.5)
        # self.anime += Animation(height=34, width=34, spacing=[5, 5], duration=0.5)
        self.anime = Animation(angle=angle, duration=0.4)
        print(angle, 'rotation')
        self.anime.bind(on_complete=self.startLoadingAnime)
        self.anime.start(self)
        self.is_animating = True
        angle += 45
class RV(RecycleView):
    refreshing = BooleanProperty(False)
    drag_threshold = NumericProperty('50sp')
    i=0
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.content_box_y = 0
        # self.spinner = Image(source='spinner.png', size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        # self.spinner.opacity = 0
        # self.add_widget(self.spinner)
        # self.spinner_anim = Animation(rotation=360, duration=1)
        # self.spinner_anim.repeat = True

    def on_touch_down(self, touch):
        # print("Content box pos relative to screen", self.ids.scroll_content.to_parent(*self.ids.scroll_content.pos))
        # print("Test----|", self.ids.scroll_content.to_parent(*[0,0]))
        # print("Window position",Window._pos)
        # print(f"Content box height {self.ids.scroll_content.height} and pos{self.ids.scroll_content.pos}")
        # print(Window.height,Window)
        # for prop in dir(Window):
        #     if not prop.startswith('_'):
        #         print(f"{prop}: {getattr(Window, prop)}")
        # self.content_box_y = self.ids.scroll_content.to_window(*self.ids.scroll_content.pos)[1]
        # spinner = self.parent.parent.spinner if isinstance(self.parent.parent, DisplayFolderScreen) else None
        # if spinner.opacity == 0:# and not spinner_anim.have_properties_to_animate(spinner):
        if self.i==0:
            # print('calling')
            self.i=1
            # spinner.startLoadingAnime()
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        # print("Content box pos relative to screen", self.ids.scroll_content.to_parent(*self.ids.scroll_content.pos))
        pos=self.ids.scroll_content.pos
        # print("Test----|", self.ids.scroll_content.to_widget(x=pos[0],y=pos[1],relative=True))
        a=self.ids.scroll_content.to_window(*self.ids.scroll_content.pos)[1]
        # b=self.ids.scroll_content.to_window(x=pos[0],y=pos[1],relative=True)[1]
        # c=self.ids.scroll_content.to_widget(x=pos[0],y=pos[1],relative=True)[1]
        # d=self.ids.scroll_content.to_local(x=pos[0],y=pos[1],relative=0)[1]
        current_screen_height=self.parent.parent.height
        # print(int(a),int(b),int(c),int(d),e)
        # print(e-a)
        real_coordinate_y=current_screen_height-a-self.ids.scroll_content.height    # .get_top() just return object height
        
        # real_coordinate_y1=current_screen_height-a-self.ids.scroll_content.get_top()
        # print('pos',real_coordinate_y,real_coordinate_y1,self.ids.scroll_content.get_top())
        # print('parent height',self.parent.height)
        # print("Test----|", self.ids.scroll_content.to_widget(*[0,0]))
        # pixels_moved = self.content_box_y - self.ids.scroll_content.to_window(*self.ids.scroll_content.pos)[1]
        # pixels_moved = 0 if pixels_moved < 0 else pixels_moved
        # spinner = self.parent.parent.spinner if isinstance(self.parent.parent, DisplayFolderScreen) else None
        # spinner_anim = self.parent.parent.spinner_anim if isinstance(self.parent.parent, DisplayFolderScreen) else None
        print(self.i,'Index')
        self.i+=1
        # if spinner:...
            # spinner.opacity = min(pixels_moved / 135, 1)
            # spinner.y = spinner.y - (pixels_moved/5 or 0.1)
            
            # print(spinner.y,(pixels_moved/2 or 0.1),'y pixels_moved')
            
        return super().on_touch_move(touch)
    
        
    def on_touch_up(self, touch):
        # self.i=0
        # spinner = self.parent.parent.spinner if isinstance(self.parent.parent, DisplayFolderScreen) else None

        # if spinner:
        #     spinner.stopLoadingAnime()
        # print('stopped laoding anime')
        # return
    
        # pixels_moved = self.content_box_y - self.ids.scroll_content.to_window(*self.ids.scroll_content.pos)[1]
        # print('pixels_moved', pixels_moved)
        # if pixels_moved > 135:...
            # self.refresh()
            # print('refresh data |||||||||')
        
        # spinner_anim = self.parent.parent.spinner_anim if isinstance(self.parent.parent, DisplayFolderScreen) else None
        
        #     spinner.opacity = 0
            # spinner_anim.stop(spinner)
        # self._start_touch_y = 0
        return super().on_touch_up(touch)

    def refresh(self):
        screen = self.parent.parent if isinstance(self.parent.parent, DisplayFolderScreen) else None
        if screen:
            Clock.schedule_once(lambda dt: screen.startSetPathInfo_Thread())
        
        
        
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
        

from kivy.uix.scrollview import ScrollView

class CustomRefreshLayout(ScrollView):
    refreshing = BooleanProperty(False)
    drag_threshold = NumericProperty('50dp')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_touch_y = None
        self._refresh_triggered = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._start_touch_y = touch.y
            self._refresh_triggered = False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._start_touch_y and not self._refresh_triggered:
            if touch.y - self._start_touch_y > self.drag_threshold:
                self.refreshing = True
                self._refresh_triggered = True
                self.dispatch('on_refresh')
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._start_touch_y = None
        return super().on_touch_up(touch)

    def on_refresh(self):
        print('on fresh method---|')
        pass

    def refresh_done(self):
        print('fresh done method---|')
        self.refreshing = False

class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner = Grid()
        # self.spinner = Image(source='loading.png', size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        # self.spinner.opacity = 0
        
        
        
        
        
        
        self.data_received=False
        self.screen_history = []
        self.current_dir_info:list[dict]=[]
        self.could_not_open_path_msg="Couldn't Open Folder Check Laner on PC"
        # self.md_bg_color=[1,1,0,1]
        self.layout=MDBoxLayout(orientation='vertical')
        self.header=Header(
                           text=self.current_dir,
                           size_hint=[1,.1],
                           text_halign='center',
                        #    theme_text_color='Custom',
                        #    title_color  = THEME_COLOR_TUPLE
                           theme_text_color='Primary',
                           title_color=self.theme_cls.primaryColor,
                           )
        self.layout.add_widget(self.header)

        self.screen_scroll_box = RV()
        self.screen_scroll_box.children[0].bind(height=self.spinner.setter('y'))
        
        
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
                on_release=lambda x:self.choose_file()
        )
        # self.upload_btn.md_bg_color=[1,0,0,1]
        
        # Adding directory details
        self.details_box=MDRelativeLayout(
            height='35sp',
            adaptive_width=True,
            md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1],
            size_hint=[1,None]
            )
        
        self.details_label=DetailsLabel(text='0 files and 0 folders')
        
        self.add_widget(self.layout)
        
        self.details_box.add_widget(self.details_label)
        self.add_widget(self.details_box)
        self.add_widget(self.upload_btn)
        
        self.add_widget(self.spinner)
        
        # self.spinner_anim = Animation(height=80,spacing=[10,10], duration=0.5)
        # self.spinner_anim += Animation(height=60,spacing=[5,5], duration=0.5)
        # self.spinner_anim += Animation(height=self.angle, duration=0.5)
        # # self.angle +=5
        # self.spinner_anim.repeat = True
           
        
    def uploadFile(self,file_path):
        try:
            response = requests.post(
                f"http://{getSERVER_IP()}:8000/api/upload",
                files={'file': open(file_path, 'rb')},
                data={'save_path': self.current_dir}
            )
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return
            Clock.schedule_once(lambda dt:Snackbar(h1="File Uploaded Successfully"))
            Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1="Failed to Upload File check Laner on PC"))
            print(e,"Failed Upload")
            
    def startUpload_Thread(self,file_path):
        threading.Thread(target=self.uploadFile,args=(file_path,)).start()
    def choose_file(self):
        print('printing tstex')
        def test1(file_path):
            print(file_path,'choosen path')
            if file_path:
                self.startUpload_Thread(file_path if isinstance(file_path,str) else file_path[0])
                # self.img.source=file_path[0]
        filechooser.open_file(on_selection=test1)
        # filechooser.open_file(on_selection=lambda x: print(x))
        
                    
    def startSetPathInfo_Thread(self):
        # print(self.data_received)
        threading.Thread(target=self.querySetPathInfoAsync).start()
        # time.sleep(0.2)
        # if not self.data_received:
        #     self.pop_up = PopupDialog()
        
    def querySetPathInfoAsync(self):
        # Run the async function in the event loop
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncSetPathInfo())
        loop.close()
                     
    async def asyncSetPathInfo(self):
        try:
            # self.data_received=False
            
            response = requests.get(f"http://{getSERVER_IP()}:8000/api/getpathinfo",json={'path':self.current_dir},timeout=5)
            
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
            # self.data_received=True
            
            # self.pop_up.update_pop_up_text(self.name)
            
            # Clock.schedule_once(self.pop_up.close)
            
                    
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(e,"Failed opening Folder async")
                   
    def on_enter(self, *args):...
        # print(self.data_received)
        # Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        
        
            
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
            return 404
    def setPath(self,path,add_to_history=True):
        if self.isDir(path) != 404 and not self.isDir(path):
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


from kivymd.uix.button import MDButton, MDButtonText

class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    font_size = StringProperty('')
    
    size = ListProperty([sp(0),sp(0)])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_width = "Custom"
        self.theme_height = "Custom"
        # if self.size == [sp(0),sp(0)]:
        #     self.adaptive_size=True
        # self.height=10#self.size[1]

        text=MDButtonText(
            text=self.text,
            pos_hint= {"center_x": .5, "center_y": .5})
        if self.font_size:
            text.theme_font_size = "Custom"
            # text.font_size=self.font_size
        self.add_widget(text)



class CustomDropDown(MDBoxLayout):
    title = StringProperty("Advanced Options")
    # icon = StringProperty("arrow-down")
    is_open = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.not_keeps_sake=[]      
    def toggle_dropdown(self):
        print(self.is_open)
        print(self.ids.dropdown_content.children,'pop')
        if self.is_open:
            self.ids.dropdown_content.clear_widgets()
            # self.ids.dropdown_content.height = 0
        else:
            for each in self.not_keeps_sake:
                self.ids.dropdown_content.add_widget(each)
            # self.ids.dropdown_content.height = self.ids.dropdown_content.minimum_height
        print(self.ids.dropdown_content.children,'ffff')
            
        self.is_open = not self.is_open

    def add_widget(self, widget, index=0, canvas=None):
        if self.ids and 'dropdown_content' in self.ids:
            self.not_keeps_sake.append(widget)
            if self.is_open:
                self.ids.dropdown_content.add_widget(widget)
            # self.ids.dropdown_content.height = self.ids.dropdown_content.minimum_height
        else:
            super().add_widget(widget, index=index, canvas=canvas)        
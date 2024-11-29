# from kivymd.uix.button import MDButton
from kivy.uix.screenmanager import NoTransition
# from kivymd.uix.button import BaseButton, MDIconButton, MDRectangleFlatButton,MDRectangleFlatIconButton,ButtonContentsIconText
# from kivy.uix.boxlayout import BoxLayout
# from kivymd.uix.button import MDRaisedButton
# from kivymd.uix.relativelayout import MDRelativeLayout
# from kivymd.uix.behaviors import CircularRippleBehavior
# from kivy.uix.image import Image
# from kivymd.uix.button import MDIconButton
# from kivymd.uix.card import MDCard
# from kivy.uix.slider import Slider
# from kivymd.uix.slider import MDSlider
# from kivy.uix.switch import Switch
# from kivymd.uix.fitimage import FitImage
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
# import socket
# from multiprocessing.dummy import Pool as ThreadPool

from kivy.clock import Clock
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import ( BooleanProperty, ListProperty, BoundedNumericProperty, ColorProperty, DictProperty, NumericProperty, ObjectProperty, OptionProperty, StringProperty, VariableListProperty)
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import StringProperty,ListProperty
from kivymd.uix.label import MDIcon, MDLabel
from kivy.metrics import dp,sp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView,RecycleLayoutManagerBehavior
from kivy.core.window import Window
from kivy.app import runTouchApp
from kivymd.uix.stacklayout import MDStackLayout
from kivy.uix.label import Label
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField

from widgets.popup import PopupDialog,Snackbar

import requests
import os, sys, json
from kivymd.material_resources import DEVICE_TYPE
if DEVICE_TYPE != "mobile":
    Window.size = (400, 1000)
THEME_COLOR_TUPLE=(.6, .9, .8, 1)
__DIR__ = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
MY_DATABASE_PATH = os.path.join(__DIR__, 'data', 'store.json') 


try:
    from jnius import autoclass
    from android import mActivity
    # context =  mActivity.getApplicationContext()
    # SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Worker'
    # service = autoclass(SERVICE_NAME)
    # print(SERVICE_NAME)
    # service.start(mActivity,'')
    # print('returned service')

    context =  mActivity.getApplicationContext()
    SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Sendshit'
    service = autoclass(SERVICE_NAME)
    service.start(mActivity,'')
    print('returned service')
except Exception as e:
    print(f'Foreground service failed {e}')


# import ipaddress
import threading
import os
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
import json
import asyncio
from kivy.utils import platform
import requests
# import aiohttp
# from threading import Thread

SERVER_IP = '192.168.2.4'

my_folder=os.getcwd()
if platform == 'android':
    from android.permissions import request_permissions, Permission,check_permission
    from android.storage import app_storage_path, primary_external_storage_path
    my_folder=os.path.join(primary_external_storage_path(),'Download','Laner')
    print('Asking permission...')
    def check_permissions(permissions):
        for permission in permissions:
            if check_permission(permission) != True:
                return False
        return True
    
    permissions=[Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE]
    if check_permissions(permissions):
        request_permissions(permissions)
            

def makeAppDownloadsFolder():
    if not os.path.exists(my_folder):
        os.makedirs(my_folder)
        
makeAppDownloadsFolder()


from pathlib import Path
async def async_download_file(url, save_path):
    try:
        response = requests.get(url)
        file_name = save_path
        file_path = os.path.join(my_folder, file_name)
        print("Done")
        with open(file_path, "wb") as file:
            file.write(response.content)
            # 
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { truncateStr(Path(file_path).parts[-1],10) }'))
        # Clock.schedule_once(lambda dt: print(f"File saved at {file_path}"))
    except Exception as e:
        print(e,"Failed to Write to My Downloads Folder")      

def download_file(url, save_path):
    
    # Run the async function in the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_download_file(url, save_path))
    loop.close()

def myDownloadTest():
    needed_file = f"http://{SERVER_IP}:8000/home/fabian/Downloads/code_1.95.2-1730981514_amd64.deb"
    url = needed_file.replace(' ', '%20')
    file_name = needed_file.split('/')[-1]
    file_path = os.path.join(my_folder, file_name)
    
    # Start the download in a new thread
    # thread = Thread(target=download_file, args=(url, file_path))
    # thread.start()
    threading.Thread(target=download_file,args=(url, file_path)).start()


# size_hint: (.5, None)
Builder.load_string('''
<MyCard>:
    radius: dp(5)
    size_hint:(1,1)
    theme_bg_color: "Custom"
    on_release: app.download_screen.setPath(self.path)
    
    AsyncImage:
        id: test_stuff
        source: root.icon
        size_hint: [.9,.7]
        fit_mode: 'contain'
        mipmap: True
        pos_hint: {"top":1}
        radius: (dp(5),dp(5),0,0)
    MDButton:
        theme_bg_color:  "Custom"
        theme_height:  "Custom"
        theme_width:  "Custom"
        radius: '15sp'
        size_hint:  [None, None]
        width:  '35sp'
        height: '35sp'
        md_bg_color: [.7,.6,.9,1]
        pos_hint: {"top": .979, "right": .97}
        on_release: app.download_screen.showDownloadDialog(root.path)
        
        MDButtonIcon:
            icon: "download"
            pos_hint: {'x':.23,'y':.2}
            theme_icon_color: "Custom"
            icon_color: [1,1,1,1]
        
    Label:
        text: root.myFormat(root.text)
        font_size: '11sp'
        size_hint: [None, None]
        size: (root.width, 40)
        text_size: (root.width, None)
        # max_lines: 2

<RV>:
    viewclass: 'MyCard'
    size_hint: (1, .9)
    My_RecycleGridLayout:
        default_size: 1, '140sp'
        default_size_hint: 1, None
        spacing:18
        padding:"10dp"
        size_hint: (1, None)
        height: self.minimum_height
''')


class My_RecycleGridLayout(RecycleGridLayout):
    screen_history = []  # Stack to manage visited screens
    def __init__(self, **kwargs): 
        # print(Window.width)
        super().__init__(**kwargs)
        if Window.width > 800:
            self.cols=5
        else:
            try:
                self.cols= int(str(Window.width)[0]) -2
            except:
                self.cols=2
    def on_size(self, *args):
        if Window.width > 800:
            self.cols=5
        elif Window.width < 300:            
            self.cols=3
        elif Window.width < 200:
            self.cols=2
        else:
            self.cols=4
            
# rechable_ips=[]
# lock=threading.Lock()
# def ping(ip):
#     """
#     Ping an IP address to check if it is reachable.
#     Returns the IP address if reachable, otherwise None.
#     """
#     # Execute a ping command
#     response = os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1")
#     if response == 0:
#         with lock:
#             rechable_ips.append(ip)
            
# def scan_network(network):
#     """
#     Scan the provided network to find active devices.
#     Returns a list of IP addresses of devices that respond to ping.
#     """
#     print(f"Scanning network: {network}")
#     # Create a pool of threads for faster execution
#     threads=[]
    
#     for ip in ipaddress.IPv4Network(network, strict=False):
#         t=threading.Thread(target=ping, args=(str(ip),))
#         threads.append(t)
#         t.start()
        
#     for t in threads:
#         t.join()

class WindowManager(ScreenManager):
    screen_history = []  # Stack to manage visited screens
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.Android_back_click)
        
    def changeScreenAnimation(self, screen_name):
        if self.screen_names.index(screen_name) > self.screen_names.index(self.current):
            self.transition=SlideTransition(direction='left')
        else:
            self.transition=SlideTransition(direction='right')
    def change_screen(self, screen_name):
        """Navigate to a specific screen and record history."""        
        self.changeScreenAnimation(screen_name)
        
        if self.current != screen_name:
            self.screen_history.append(self.current)
            self.current = screen_name
    
    def findTabButtonsAndChangeDesign(self):
        # TODO Google a way to select children by id prop
        # print([type(widget) for widget in self.walk(loopback=True)][0].ids)
        # test = [type(widget) for widget in self.walk(loopback=True)][0].ids
        # print(test)
        # print(test.att())
        tabs_buttons_list=self.parent.children[0].children
        for each_btn in tabs_buttons_list:
            each_btn.checkWidgetDesign(self.current)
    def Android_back_click(self, window, key, *largs):
        """Handle the Android back button."""
        if key == 27:  # Back button key code
            if self.current == 'download' and len(self.current_screen.download_screen_history):
                # might switch to "if []:" since it works on python but "if len([]):" is more understandable
                # print(self.current_screen.download_screen_history)
                last_dir = self.current_screen.download_screen_history.pop()
                self.current_screen.setPath(last_dir, False)
                return True            
            
            if len(self.screen_history): # Navigate back to the previous screen
                last_screen = self.screen_history.pop()
                self.changeScreenAnimation(last_screen)
                self.current = last_screen
                self.findTabButtonsAndChangeDesign()
                return True
            else:
                # Exit the app if no history
                return False


class MY_MDIcon(MDIcon):
    "MDIcon Font size doesn't work unless creating my own class and passing MDIcon in it."
    font_size__ = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.font_size = self.font_size__


class TabButton(RectangularRippleBehavior,ButtonBehavior,MDBoxLayout):
    text=StringProperty()
    icon=StringProperty()
    screen=StringProperty() # screen name
    screen_manager_current=StringProperty() # current screen name
    # color=ListProperty()
    tabs_buttons_list=[]
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        # self.ripple
        self.orientation='vertical'
        self.padding=[dp(0),dp(8),dp(0),dp(5)]        
        self.line_color=(.2, .2, .2, 0)
        self._radius=1
        self.id=self.text
        self.spacing='-5sp'

        self.label= Label(
            text=self.text, halign='center',
            font_name='assets/fonts/Helvetica.ttf',
            font_size=sp(13),
            )
        self.btn_icon = MDIcon(
                icon=self.icon,
                # font_size__='40sp',
                # size_hint=[.5,.5],
                pos_hint={'center_x': 0.5,'center_y': 0},
                theme_text_color="Custom",
            )
        
        self.add_widget(self.btn_icon)
        self.add_widget(self.label)
        self.tabs_buttons_list.append(self)
        self.checkWidgetDesign(self.screen_manager_current)
    def on_release(self):
        self.designWidgets(self.screen)
        return super().on_release()
    def designWidgets(self,cur_screen):
        for each_btn in self.tabs_buttons_list:
            each_btn.checkWidgetDesign(cur_screen)

    def checkWidgetDesign(self,cur_screen):
        with open(MY_DATABASE_PATH) as change_mode1:
            Bool_theme = json.load(change_mode1)
            if Bool_theme['Dark Mode']:
                self.btn_icon.text_color=self.label.color = [1, 1, 1, 1]
                self.md_bg_color = (.2, .2, .2, .5)

            else:
                self.btn_icon.text_color=self.label.color = [0, 0, 0, 1]
                self.md_bg_color = (.2, .2, .2, .5)
        
            if self.screen == cur_screen:
                # print(self.screen,cur_screen)
                # MDIcon.text_color=Label.color = THEME_COLOR_TUPLE
                self.btn_icon.text_color=self.label.color = self.theme_cls.backgroundColor


class BottomNavigationBar(MDBoxLayout):
    screen = StringProperty()
    def __init__(self, screen_manager:WindowManager,**kwargs):
        super(BottomNavigationBar, self).__init__(**kwargs)

        self.screen_manager=screen_manager
        icons = ['inbox', 'download', 'connection']
        for_label_text = ['Upload','Download','Link']
        screens=screen_manager.screen_names
        self.size_hint =[ 1, .1]
        self.padding=0
        self.spacing=0
        
        for index in range(len(icons)):
            self.btn = TabButton(
                # id=str(index),
                # size_hint=(1, 1),
                # color=colors[index],
                icon=icons[index],
                text=for_label_text[index],
                screen=screens[index],
                screen_manager_current=screen_manager.current,
                on_release=lambda x,cur_index=index: self.setScreen(x,screens[cur_index])
            )
            self.add_widget(self.btn)    
    
    
    def setScreen(self,btn:TabButton,screen_name):
        self.screen_manager.change_screen(screen_name)
        # btn.designWidgets(self.screen_manager.current)


class MySwitch(MDBoxLayout):
    text=StringProperty()
    switch_state=BooleanProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=[1,None]
        self.height='40sp'
        self.padding=[sp(20),0]
        # self.md_bg_color=[1,1,0,1]
        
        self.add_widget(MDLabel(
            halign='left',valign='center',
                                text_color=[1,1,1,1],
                                text=self.text))
        self.add_widget(MDSwitch(
            pos_hint={'right':.9,'top':.9},
                                #  theme_bg_color='Custom',md_bg_color=[1,0,.5,1]
                                 ))

def truncateStr(text:str,limit=20):
    if len(text) > limit:
        return text[0:limit] + '...'
    return text

class MyCard(RecycleDataViewBehavior,RectangularRippleBehavior,ButtonBehavior,MDRelativeLayout):
    path=StringProperty()
    icon=StringProperty()
    text=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_effect=False
           
    def myFormat(self, text:str):
        if len(text) > 20:
            return text[0:18] + '...'
        return text
    
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV,self).__init__(**kwargs)

class UploadScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='upload'
        label=MDLabel(text="Upload Screen",halign='center')
        self.add_widget(label)
        self.theme_bg_color="Custom"
        self.md_bg_color=self.theme_cls.backgroundColor
        img=AsyncImage(source=f"http://{SERVER_IP}:8000/home/fabian/Screenshot from 2024-11-23 19-57-50.png".replace(' ','%20'))
        self.add_widget(img)

class Header(MDBoxLayout):
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (.2, .2, .2, .5)
        self.header_label=MDLabel(
            text_color=self.title_color,
            text=self.text,
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
    def chandeTitle(self,text):
        self.header_label.text=text
        
from kivy.uix.widget import Widget

from kivymd.uix.widget import MDWidget
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer,MDDialogSupportingText
        
class DownloadScreen(MDScreen):
    download_screen_history = []  # Stack to directory screens
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='download'
        # self.size_hint=[1,1]
        self.current_dir = './'
        # """ Only set with setPath function"""
        self.current_dir_info:list[dict]=[]
        # """ Only set with setPathInfo function"""

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
        self.setPathInfo()
        
        self.layout.add_widget(self.screen_scroll_box)
        self.add_widget(self.layout)
        
    
    def on_pre_enter(self, *args):
        self.setPathInfo()
        pass
    def setPathInfo(self):
        try:
            response = requests.get(f"http://{SERVER_IP}:8000/api/getpathinfo",json={'path':self.current_dir})   #os.listdir(self.current_dir)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                return
            self.screen_scroll_box.data=self.current_dir_info=response.json()['data']
        except Exception as e:
            print(e)
    def isDir(self,path:str):
        
        try:
            response=requests.get(f"http://{SERVER_IP}:8000/api/ispath",json={'path':path})
            if response.status_code != 200:
                return False
            return response.json()['data']
            
        except Exception as e:
            print(f"isDir method: {e}")
            return False
    def setPath(self,path,add_to_history=True):
        if not self.isDir(path):
            return
        if add_to_history:  # Saving Last directory for screen history
            self.download_screen_history.append(self.current_dir) 
            
        self.current_dir = path
        self.header.chandeTitle(path)
        self.setPathInfo()              
    def showDownloadDialog(self,path):
        """Shows Dialog box with choosen path and calls async download if ok press"""
        if (self.isDir(path)):
            return
        def failedCallBack():...
        def successCallBack():
            needed_file = f"http://{SERVER_IP}:8000/{path}"
            url = needed_file.replace(' ', '%20')
            file_name = needed_file.split('/')[-1]
            saving_path = os.path.join(my_folder, file_name)
            threading.Thread(target=self.b_c,args=(url, saving_path)).start()
        PopupDialog(
            failedCallBack=failedCallBack,successCallBack=successCallBack,
            h1="Verify Download",
            caption=f"{truncateStr(path.split('/')[-1])} Will be saved in \"Laner\" Folder in your device \"Downloads\"",
            cancel_txt="Cancel",confirm_txt="Ok",
            )
    def b_c(self,url, save_path):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download_file(url, save_path))

        
class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='settings'
        self.layout=MDBoxLayout(
            # md_bg_color=[1,0,0,1],
            # adaptive_height=True,
            size_hint=[1,.1],
            
            pos_hint={'top':1}
            )
        self.layout.orientation='vertical'
        # self.layout.orientation='vertical'
        self.layout.spacing=sp(10)
        self.header=Header(
            # size_hint=[1,None],height=sp(50),
                           size_hint=[1,1],
            
            text="Settings",text_halign='left')
        
        self.content=MDBoxLayout(orientation='vertical',
                                 size_hint=[1,.8],
                                #  md_bg_color=[1,0,0,1],
                                adaptive_height=True,
                                spacing=sp(20),
                                padding=[sp(10),0],
            pos_hint={'top':.86}
                                 )
        
        portInput=MDTextField(input_filter='float',theme_text_color= "Custom",text_color_focus=[.9,.9,1,1],text_color_normal=[1,1,1,1],pos_hint={'center_x':.5},size_hint=[.8,None],height=dp(80))
        verifyBtn=MDButton(    
                           theme_height= "Custom", theme_width= "Custom",
                           on_release=lambda x: Snackbar(confirm_txt='Ok'),
                           pos_hint={'center_x':.5},size_hint=[None,None],size=[sp(120),dp(50)],radius=0)
        verifyBtn.add_widget(MDButtonText(text='Verify',pos_hint= {"center_x": .5, "center_y": .5}
))
        self.layout.add_widget(self.header)
        
        
        self.content.add_widget(MySwitch(text='Show hidden files'))
        self.content.add_widget(portInput)
        self.content.add_widget(verifyBtn)
        
        self.add_widget(self.layout)
        self.add_widget(self.content)
    
class Laner(MDApp):
    
    def build(self):
        self.title='Laner'
        
        # self.death='Fog'
        # self.bind(death=self.change_theme)
        
        self.theme_cls.backgroundColor=THEME_COLOR_TUPLE
        root_layout=MDBoxLayout(orientation='vertical')
        root_layout.md_bg_color=.3,.3,.3,1
        
        my_screen_manager = WindowManager()
        my_screen_manager.add_widget(UploadScreen())
        self.download_screen=DownloadScreen()
        my_screen_manager.add_widget(self.download_screen)
        my_screen_manager.add_widget(SettingsScreen())
        # my_screen_manager.transition=NoTransition()
        my_screen_manager.current='settings'
        bottom_navigation_bar=BottomNavigationBar(my_screen_manager)

        root_layout.add_widget(my_screen_manager)
        root_layout.add_widget(bottom_navigation_bar)
        # Clock.schedule_once(lambda dt: myDownloadTest())

        
        return root_layout
    def change_theme(self, *args):
        print(self.death)
        
        

if __name__ == '__main__':
    Laner().run()

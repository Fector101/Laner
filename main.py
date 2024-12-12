from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivy.clock import Clock
from kivy.properties import ( BooleanProperty, ListProperty, StringProperty)
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.label import MDIcon, MDLabel
from kivy.metrics import dp,sp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.utils import platform
from kivymd.material_resources import DEVICE_TYPE

import threading
import asyncio
import requests
import os, sys, json
from pathlib import Path

from widgets.popup import PopupDialog,Snackbar
from workers.helper import getSystem_IpAdd, makeFolder

# For Dev
if DEVICE_TYPE != "mobile":
    Window.size = (400, 1000)

# TODO For Theme
THEME_COLOR_TUPLE=(.6, .9, .8, 1)
__DIR__ = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
MY_DATABASE_PATH = os.path.join(__DIR__, 'data', 'store.json')

# For Dev PC IP
SERVER_IP = getSystem_IpAdd()

# So all class have access to download screen special settings
download_screen = None

# Dev getting Downloads Folder
my_folder=os.getcwd()

if platform == 'android':
    SERVER_IP=''
    try:
        from jnius import autoclass
        from android import mActivity
        context =  mActivity.getApplicationContext()
        SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Sendnoti'
        service = autoclass(SERVICE_NAME)
        service.start(mActivity,'')
        print('returned service')
    except Exception as e:
        print(f'Foreground service failed {e}')

    
    from android.permissions import request_permissions, Permission,check_permission
    from android.storage import app_storage_path, primary_external_storage_path
    
    #Making/Getting Downloads Folder
    my_folder=os.path.join(primary_external_storage_path(),'Download','Laner')
    makeFolder(my_folder)
    
    print('Asking permission...')
    def check_permissions(permissions):
        for permission in permissions:
            if check_permission(permission) != True:
                return False
        return True

    permissions=[Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE]
    if check_permissions(permissions):
        request_permissions(permissions)



async def async_download_file(url, save_path):
    try:
        response = requests.get(url)
        file_name = save_path
        file_path = os.path.join(my_folder, file_name)
        print("Done")
        with open(file_path, "wb") as file:
            file.write(response.content)
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
    threading.Thread(target=download_file,args=(url, file_path)).start()


Builder.load_string('''
<MyCard>:
    radius: dp(5)
    size_hint:(1,1)
    theme_bg_color: "Custom"
    on_release: app.my_screen_manager.current_screen.setPath(self.path)
    
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
        on_release: app.my_screen_manager.current_screen.showDownloadDialog(root.path)
        
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
            if self.current != 'settings' and len(self.current_screen.screen_history):
                # might switch to "if []:" since it works on python but "if len([]):" is more understandable
                # print(self.current_screen.screen_history)
                last_dir = self.current_screen.screen_history.pop()
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
        self.size_hint=[1,1]
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

            else:
                self.btn_icon.text_color=self.label.color = [0, 0, 0, 1]

            if self.screen == cur_screen:
                # print(self.screen,cur_screen)
                # MDIcon.text_color=Label.color = THEME_COLOR_TUPLE
                self.btn_icon.text_color=self.label.color = self.theme_cls.backgroundColor


class BottomNavigationBar(MDBoxLayout):
    screen = StringProperty()
    def __init__(self, screen_manager:WindowManager,**kwargs):
        super(BottomNavigationBar, self).__init__(**kwargs)

        self.screen_manager=screen_manager
        icons = ['home', 'download', 'connection']
        for_label_text = ['Home','Storage','Link']
        screens=screen_manager.screen_names
        self.size_hint =[ 1, .1]
        self.padding=0
        self.spacing=0
        self.md_bg_color = (.2, .2, .2, .5)

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

validated_paths=[]
class MyCard(RecycleDataViewBehavior,RectangularRippleBehavior,ButtonBehavior,MDRelativeLayout):
    path=StringProperty()
    icon=StringProperty()
    text=StringProperty()
    thumbnail_url=StringProperty()
    thumbnail_path=StringProperty()
    is_dir=BooleanProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_effect=False
        # print(self.thumbnail_url,'lll')
        # if not self.is_dir:
        #     print('polrwda---wdewwniw====')
        # Clock.schedule_once(lambda dt: self.update_image(), 6)

    def isFile(self,path:str):

        try:
            response=requests.get(f"http://{SERVER_IP}:8000/api/isfile",json={'path':path},timeout=3)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1="Dev pinging for thumb valid"))
                return False
            # print(response.json()['data'])
            return response.json()['data']

        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1="Dev pinging for thumb valid"))
            print(f"isDir method: {e}")
            return False

    def on_thumbnail_url(self, instance, value):
        """Called whenever thumbnail_url changes."""
        self.event = Clock.schedule_interval(lambda dt: self.update_image(), 1)
                
    def update_image(self):
        global validated_paths
        if self.thumbnail_url and (self.thumbnail_path in validated_paths or self.isFile(self.thumbnail_path)):
            if self.thumbnail_path not in validated_paths:
                validated_paths.append(self.thumbnail_path)
            
            self.icon = self.thumbnail_url
            self.event.cancel()
        elif not self.thumbnail_url:
            self.event.cancel()
            
            
    def myFormat(self, text:str):
        if len(text) > 20:
            return text[0:18] + '...'
        return text

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV,self).__init__(**kwargs)

class HomeScreen(MDScreen):
    screen_history = []  # Stack to directory screens

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='upload'
        # self.size_hint=[1,1]
        self.current_dir = 'Home'
        # """ Only set with setPath function"""
        self.current_dir_info:list[dict]=[]
        # """ Only set with setPathInfo function"""
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
        # self.setPathInfo()
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
            response = requests.get(f"http://{SERVER_IP}:8000/api/getpathinfo",json={'path':self.current_dir},timeout=5)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return
            self.screen_scroll_box.data=self.current_dir_info=response.json()['data']
            # Clock.schedule_once(lambda dt: self.screen_scroll_box.refresh_from_data(), 6)
            
            # Clock.schedule_once(lambda dt: print(f"File saved at {file_path}"))
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(e,"Failed opening Folder async")
                   
    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
   
            
    def isDir(self,path:str):

        try:
            response=requests.get(f"http://{SERVER_IP}:8000/api/isdir",json={'path':path},timeout=3)
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
            needed_file = f"http://{SERVER_IP}:8000/{path}"
            url = needed_file.replace(' ', '%20').replace('\\', '/')
            
            saving_path = os.path.join(my_folder, file_name)
            threading.Thread(target=self.b_c,args=(url, saving_path)).start()
        PopupDialog(
        failedCallBack=failedCallBack,successCallBack=successCallBack,
        h1="Verify Download",
        caption=f"{file_name} Will be saved in \"Laner\" Folder in your device \"Downloads\"",
        # caption=f"{truncateStr(path.replace('\\', '/').split('/')[-1])} Will be saved in \"Laner\" Folder in your device \"Downloads\"",
        cancel_txt="Cancel",confirm_txt="Ok",
        )
    def b_c(self,url, save_path):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download_file(url, save_path))

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
    def changeTitle(self,text):
        self.header_label.text=text

class StorageScreen(MDScreen):
    screen_history = []  # Stack to directory screens

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='download'
        # self.size_hint=[1,1]
        self.current_dir = '.'
        # """ Only set with setPath function"""
        self.current_dir_info:list[dict]=[]
        # """ Only set with setPathInfo function"""
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
        # self.setPathInfo()
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
            response = requests.get(f"http://{SERVER_IP}:8000/api/getpathinfo",json={'path':self.current_dir},timeout=5)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return
            self.screen_scroll_box.data=self.current_dir_info=response.json()['data']
            # Clock.schedule_once(lambda dt: self.screen_scroll_box.refresh_from_data(), 6)
            
            # Clock.schedule_once(lambda dt: print(f"File saved at {file_path}"))
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print(e,"Failed opening Folder async")
                   
    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
   
            
    def isDir(self,path:str):

        try:
            response=requests.get(f"http://{SERVER_IP}:8000/api/isdir",json={'path':path},timeout=3)
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
            needed_file = f"http://{SERVER_IP}:8000/{path}"
            url = needed_file.replace(' ', '%20').replace('\\', '/')
            
            saving_path = os.path.join(my_folder, file_name)
            threading.Thread(target=self.b_c,args=(url, saving_path)).start()
        PopupDialog(
        failedCallBack=failedCallBack,successCallBack=successCallBack,
        h1="Verify Download",
        caption=f"{file_name} Will be saved in \"Laner\" Folder in your device \"Downloads\"",
        # caption=f"{truncateStr(path.replace('\\', '/').split('/')[-1])} Will be saved in \"Laner\" Folder in your device \"Downloads\"",
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

        portInput=MDTextField(theme_text_color= "Custom",text_color_focus=[.9,.9,1,1],text_color_normal=[1,1,1,1],pos_hint={'center_x':.5},size_hint=[.8,None],height=dp(80))
        verifyBtn=MDButton(
                           theme_height= "Custom", theme_width= "Custom",
                           on_release=lambda x: self.setIP(portInput.text),
                        #    on_release=lambda x: Snackbar(confirm_txt='Ok'),
                           pos_hint={'center_x':.5},size_hint=[None,None],size=[sp(120),dp(50)],radius=0)
        verifyBtn.add_widget(MDButtonText(text='Verify Code',pos_hint= {"center_x": .5, "center_y": .5}))
        self.layout.add_widget(self.header)
        # TODO Get PC name when connection verifed and display connected to ...

        self.content.add_widget(MySwitch(text='Show hidden files'))
        self.content.add_widget(portInput)
        self.content.add_widget(verifyBtn)

        self.add_widget(self.layout)
        self.add_widget(self.content)
    def setIP(self,text):
        global SERVER_IP
        SERVER_IP=text
        Clock.schedule_once(lambda dt: download_screen.startSetPathInfo_Thread())
        print('My address',text, SERVER_IP)
        
class Laner(MDApp):

    def build(self):
        global download_screen
        self.title='Laner'
        
        self.theme_cls.backgroundColor=THEME_COLOR_TUPLE
        root_layout=MDBoxLayout(orientation='vertical')
        root_layout.md_bg_color=.3,.3,.3,1

        self.my_screen_manager = WindowManager()
        self.my_screen_manager.add_widget(HomeScreen())
        self.download_screen=download_screen=StorageScreen()
        self.my_screen_manager.add_widget(download_screen)
        self.my_screen_manager.add_widget(SettingsScreen())
        self.my_screen_manager.transition=NoTransition()
        self.my_screen_manager.current='settings'
        bottom_navigation_bar=BottomNavigationBar(self.my_screen_manager)

        root_layout.add_widget(self.my_screen_manager)
        root_layout.add_widget(bottom_navigation_bar)

        return root_layout



if __name__ == '__main__':
    Laner().run()

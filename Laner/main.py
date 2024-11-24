from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import StringProperty,ListProperty
from kivymd.uix.label import MDIcon, MDLabel
from kivy.metrics import dp,sp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
# from kivymd.uix.button import MDButton
import os, sys, json


from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window
from kivy.app import runTouchApp


# from kivy.uix.screenmanager import NoTransition
# from kivymd.uix.button import BaseButton, MDIconButton, MDRectangleFlatButton,MDRectangleFlatIconButton,ButtonContentsIconText
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    BoundedNumericProperty,
    ColorProperty,
    DictProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)
# from kivy.uix.boxlayout import BoxLayout
# from kivymd.uix.button import MDRaisedButton
from kivymd.uix.stacklayout import MDStackLayout
# from kivymd.uix.relativelayout import MDRelativeLayout
# from kivymd.uix.behaviors import CircularRippleBehavior
from kivy.uix.label import Label
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen

from kivy.uix.slider import Slider
from kivymd.uix.slider import MDSlider
from kivy.uix.switch import Switch
from kivymd.uix.selectioncontrol import MDSwitch

from kivymd.uix.fitimage import FitImage

from kivy.clock import Clock

from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText

from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
import requests

from kivy.lang import Builder

Builder.load_string('''
<MyCard>:
    style: 'filled'
    size_hint: (.5, None)
    height: '140sp'
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: [1,0,0,0]
    
    AsyncImage:
        id: stored_state
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
        width:  '32sp'
        height: '32sp'
        md_bg_color: [.7,.6,.9,1]
        pos_hint: {"top": .979, "right": .97}
        MDButtonIcon:
            icon: "download"
            pos_hint: {'x':.19,'y':.17}
            theme_icon_color: "Custom"
            icon_color: [1,1,1,1]
        
    Label:
        text: root.myFormat(root.text)
        font_size: '11sp'
        height: '40sp'
        pos_hint: {'left': 1}
        size_hint: [1,None]
''')


                    
                    
                    
                    
                    
                    
                


# Window.size = (400, 1000)
THEME_COLOR_TUPLE=(.6, .9, .8, 1)
__DIR__ = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
MY_DATABASE_PATH = os.path.join(__DIR__, 'data', 'store.json') 


# import socket
import ipaddress
import threading
# from multiprocessing.dummy import Pool as ThreadPool
import os

SERVER_IP = '192.168.2.4'





rechable_ips=[]
lock=threading.Lock()
def ping(ip):
    """
    Ping an IP address to check if it is reachable.
    Returns the IP address if reachable, otherwise None.
    """
    # Execute a ping command
    response = os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1")
    if response == 0:
        with lock:
            rechable_ips.append(ip)
            
def scan_network(network):
    """
    Scan the provided network to find active devices.
    Returns a list of IP addresses of devices that respond to ping.
    """
    print(f"Scanning network: {network}")
    # Create a pool of threads for faster execution
    threads=[]
    
    for ip in ipaddress.IPv4Network(network, strict=False):
        t=threading.Thread(target=ping, args=(str(ip),))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

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
        self.size_hint = 1, .1
        
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


class MySwitch(MDRelativeLayout):
    text=StringProperty()
    switch_state=BooleanProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=[1,None]
        self.height='40sp'
        # self.md_bg_color=[1,1,0,1]
        self.add_widget(MDLabel( pos_hint={'right':  .25,'top':.7},
                                # md_bg_color=[1,0,0,1],
                                text_color=[1,1,1,1],
                                adaptive_size=True,text=self.text))
        self.add_widget(MDSwitch(pos_hint={'right':.9,'top':.9},
                                #  theme_bg_color='Custom',md_bg_color=[1,0,.5,1]
                                 ))

from kivy.uix.recycleview.views import RecycleDataViewBehavior
class MyCard(RectangularRippleBehavior,ButtonBehavior,RelativeLayout):
    '''Implements a material card.'''
    path=StringProperty()
    icon=StringProperty()
    text=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
            
    def myFormat(self, text:str):
        if len(text) > 20:
            return text[0:18] + '...'
        return text.capitalize()

class MyScrollBox_ChildernContainer(RecycleDataViewBehavior,GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        
import json
class DownloadScreen(MDScreen):
    download_screen_history = []  # Stack to directory screens
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='download'
        
        self.current_dir = './'
        # """ Only set with setPath function"""
        self.current_dir_info:list[dict]=[]
        # """ Only set with setPathInfo function"""
        
        # self.md_bg_color=[1,0,1,1]
        self.layout=MDStackLayout(md_bg_color=[.4,.4,.4,1],)
        
        # self.header=MDBoxLayout(size_hint=[1,.1])
        # self.header_label=Label(color=self.theme_cls.backgroundColor,text="~ Root",halign='center',valign='center')
        # self.header.add_widget(self.header_label)
        
        self.header=Header(
                           text='~ Root',
                           size_hint=[1,.1],
                           text_halign='center',
                           title_color=self.theme_cls.backgroundColor,
                           
                           )
        self.layout.add_widget(self.header)
        
        # Needs to be after Header because function adds widget
        self.screen_scroll_box = RecycleView(size_hint=(1, .9))
        self.cur_dir_elements = None#GridLayout(cols=4, spacing=18, size_hint_y=None,padding=dp(10))
        self.layout.add_widget(self.screen_scroll_box)
        self.setPathInfo()
        
        self.theme_bg_color="Custom"
        # self.md_bg_color=[1,1,1,1]#bg
                
        self.add_widget(self.layout)
    
    def setPathInfo(self):
        try:
            response = requests.get(f"http://{SERVER_IP}:8000/api/getpathinfo",json={'path':self.current_dir})   #os.listdir(self.current_dir)
            if response.status_code != 200:
                return
            self.current_dir_info=response.json()['data']
            # requests.get(server,data='to be sent',auth=(username,password))
            self.renderPath()
        except Exception as e:
            print(e)
    def isDir(self,path:str):
        
        try:
            response=requests.get(f"http://{SERVER_IP}:8000/api/ispath",json={'path':path})
            if response.status_code != 200:
                return False
            return response.json()['data']
            
        except:...
    def setPath(self,path,add_to_history=True):
        if not self.isDir(path):
            return
        if add_to_history:  # Saving Last directory for screen history
            self.download_screen_history.append(self.current_dir) 
            
        self.current_dir = path
        self.header.chandeTitle(path)
        self.setPathInfo()              
              
    def renderPath(self):
        list_of_path_info=self.current_dir_info
        import time
        start_timer=time.time()
        
        self.screen_scroll_box.clear_widgets() # If Widget not already added it won't cause can error
        
        elapsed_timer=time.time() - start_timer
        print(f'Done in {elapsed_timer} seconds --1')
        
        self.cur_dir_elements = MyScrollBox_ChildernContainer(cols=4, spacing=18, size_hint_y=None,padding=dp(10))
        # Make sure the height is such that there is something to scroll.
        self.cur_dir_elements.bind(minimum_height=self.cur_dir_elements.setter('height'))
        
        start_timer=time.time()
        
        for each in list_of_path_info:# ("elevated", "filled", "outlined"):
              
            self.cur_dir_elements.add_widget(
                MyCard(
                    icon=each['icon'],
                    text=each['name'],
                    path=each['path'],
                    on_release=lambda item_self_prop__,current_file_path=each['path']: self.setPath(current_file_path)
                )
            )
        elapsed_timer=time.time() - start_timer
        print(f'Done in {elapsed_timer} seconds --2')
        
        self.screen_scroll_box.add_widget(self.cur_dir_elements)
        
        # self.layout.remove_widget(self.screen_scroll_box)
        # self.layout.add_widget(self.screen_scroll_box)
        
class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='settings'
        self.layout=MDStackLayout()
        self.layout.spacing=sp(10)
        self.header=Header(size_hint=[1,.1],text="Settings",text_halign='left')
        # self.header_label=Label(color=self.theme_cls.backgroundColor,text="~ Root",halign='center',valign='center')
        # self.header.add_widget(self.header_label)
        
        # self.header_label=Label(color=self.theme_cls.backgroundColor,text="Settings",halign='center',valign='center')
        
        label=MDLabel(text="Settings Screen",halign='center')
        self.layout.add_widget(self.header)
        self.layout.add_widget(MySwitch(text='Start Server'))
        self.layout.add_widget(label)
        self.add_widget(self.layout)

class Laner(MDApp):
    def build(self):
        self.title='Laner'
        root_layout=MDBoxLayout(orientation='vertical')
        root_layout.md_bg_color=.3,.3,.3,1
        my_screen_manager = WindowManager()
        self.theme_cls.backgroundColor=THEME_COLOR_TUPLE
        my_screen_manager.add_widget(UploadScreen())
        my_screen_manager.add_widget(DownloadScreen())
        my_screen_manager.add_widget(SettingsScreen())
        my_screen_manager.current='download'

        bottom_navigation_bar=BottomNavigationBar(my_screen_manager)

        root_layout.add_widget(my_screen_manager)
        root_layout.add_widget(bottom_navigation_bar)
        # Clock.schedule_once(self.change_theme, 2)
        
        return root_layout
    # def change_theme(self, dt):
    #     print(999)
    #     self.theme_cls.backgroundColor=[1,0,0,1]
    #     self.theme_cls
    # def update_theme_colors(self, *args):
    #     print('change')
        

if __name__ == '__main__':
    Laner().run()

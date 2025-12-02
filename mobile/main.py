import os, traceback, logging


from kivy.metrics import dp,sp
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.utils import platform # OS
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition

from kivymd.app import MDApp
from kivymd.uix.label import MDIcon
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationdrawer import  MDNavigationLayout

from ui.components import PictureViewer,FileReader
from utils.helper import (
    THEME_COLOR_TUPLE, makeDownloadFolder,
    setHiddenFilesDisplay, getAndroidBounds,
    getViewPortSize,
    getStatusBarHeight,requestMultiplePermissions
    )

# Start logging
try:
    from utils.log_redirect import start_logging
    start_logging()
except Exception as e:
    traceback.print_exc()

from utils import Settings
from ui.screens import DisplayFolderScreen, ConnectScreen,SettingsScreen
from ui.components.templates import MyBtmSheet
from ui.components import BottomNavigationBar,TabButton



logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("kivy").setLevel(logging.WARNING)  # If using Kivy

# try:
#     from  utils import test
#     print('Ran All Android Notify Tests')
# except Exception as e:
#     print('Andorid notify Tests failed -----',e)

#Making/Getting Downloads Folder
if platform == 'android':
    my_downloads_folder=makeDownloadFolder()
    from utils.permissions import PermissionHandler
    try:
        PermissionHandler().requestStorageAccess()
    except Exception as e:
        print('My PermissionHandler101: ',e)
        traceback.print_exc()
    # requestMultiplePermissions()
else:
    Window.size = (400, 600)


class WindowManager(MDScreenManager):
    screen_history = []  # Stack to manage visited screens
    def __init__(self, btm_sheet,**kwargs):
        super().__init__(**kwargs)
        self.btm_sheet=btm_sheet
        self.md_bg_color =[.12,.12,.12,1] if self.theme_cls.theme_style == "Dark" else [0.98, 0.98, 0.98, 1]
        # self.size_hint=[1,None]
        # self.size_hint_y=None
        self.app:Laner=MDApp.get_running_app()
        self.pos_hint={'top': 1}
        self.add_widget(DisplayFolderScreen(name='upload',current_dir='Home'))
        # self.add_widget(DisplayFolderScreen(name='upload',current_dir='/home/fabian/Documents/my-projects-code/mobile-dev'))
        self.add_widget(DisplayFolderScreen(name='download',current_dir='.'))
        self.settings=SettingsScreen()
        self.add_widget(self.settings)
        self.add_widget(ConnectScreen())
        self.transition=NoTransition()
        self.current='settings'
        # self.current='upload'
        # self.current='connect'
        Window.update_viewport()
        Window.bind(on_keyboard=self.Android_back_click)

    def changeScreenAnimation(self, screen_name):
         self.transition = SlideTransition(direction='left' if self.screen_names.index(screen_name) > self.screen_names.index(self.current) else 'right')
    def change_screen(self, screen_name):
        """Navigate to a specific screen and record history. (don't call directly outside class, this is a helper function)"""
        self.changeScreenAnimation(screen_name)

        if self.current != screen_name:
            self.screen_history.append(self.current)
            self.current = screen_name
    
    def findTabButtonsAndChangeDesign(self):
        tabs_buttons_list=self.parent.children[1].children
        for each_btn in tabs_buttons_list:
            each_btn.checkWidgetDesign(self.current)
    def Android_back_click(self, window, key, *args):
        """Handle the Android back button."""
        if key == 27:  # Back button key code
            if isinstance(self.current_screen,DisplayFolderScreen) and (len(self.current_screen.screen_history) or self.current_screen.current_popup):
                # might switch to "if []:" since it works on python but "if len([]):" is more understandable
                # print(self.current_screen.screen_history)
                # last_dir = self.current_screen.screen_history.pop()
                # self.current_screen.set_folder(last_dir, False)
                self.current_screen.set_last_folder_screen()
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
    
class MyMDIcon(MDIcon):
    "MDIcon Font size doesn't work unless creating my own class and passing MDIcon in it."
    font_size__ = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.font_size = self.font_size__
    
class Laner(MDApp):
    # android_app = autoclass('android.app.Application')pls checkout
    
    bottom_navigation_bar=ObjectProperty()
    btm_sheet = ObjectProperty()
    settings = Settings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nav_layout = None
        self.my_screen_manager = None
        self.theme_cls.theme_style = self.get_stored_theme()
        self.theme_cls.primary_palette = "White"

    def get_stored_theme(self):
        return self.settings.get('display', 'theme')

    def toggle_theme(self):
        current = self.theme_cls.theme_style
        new_theme = 'Dark' if current == 'Light' else 'Light'
        self.theme_cls.theme_style = new_theme
        self.settings.set('display', 'theme', new_theme)
        
        # Update theme for main navigation and buttons
        for each in self.bottom_navigation_bar.walk():
            if isinstance(each, TabButton):
                each.checkWidgetDesign(self.my_screen_manager.current)
                
        light_grey_for_dark_theme=[.15,.15,.15,1]
        light_grey_for_light_theme=[0.92, 0.92, 0.92, 1]
        if self.theme_cls.theme_style == "Dark":
            self.my_screen_manager.md_bg_color =[.12,.12,.12,1]
            
            for screen in self.my_screen_manager.screens:
                if not isinstance(screen, ConnectScreen):
                    screen.header.md_bg_color = light_grey_for_dark_theme
                
                # Update DisplayFolderScreen backgrounds
                if isinstance(screen, DisplayFolderScreen):
                    screen.details_box.md_bg_color = light_grey_for_dark_theme
                    screen.details_label.color =[.8, .8, .8, 1]
                    
                
        else:
            self.my_screen_manager.md_bg_color = [0.98, 0.98, 0.98, 1]
            
            # Update DisplayFolderScreen backgrounds
            for screen in self.my_screen_manager.screens:
                if not isinstance(screen, ConnectScreen):
                    screen.header.md_bg_color = light_grey_for_light_theme
                if isinstance(screen, DisplayFolderScreen):
                    screen.details_box.md_bg_color =light_grey_for_light_theme
                    screen.details_label.color = [0.41, 0.42, 0.4, 1]

    def toggle_image_viewer(self,urls:list,start_from:str):
        def on_close_pic_viewer():
            pass
        layout=PictureViewer(urls,start_from,close_btn_callback=on_close_pic_viewer,bottom_navigation_bar=self.bottom_navigation_bar)
        self.my_screen_manager.current_screen.add_widget(layout)


    def open_file_reader(self, file_path):
        def on_close_file_reader():
            pass
        layout = FileReader(file_path, close_btn_callback=on_close_file_reader,bottom_navigation_bar=self.bottom_navigation_bar)
        self.my_screen_manager.current_screen.add_widget(layout)

    def build(self):
        self.title = 'Laner'
        Window.bind(size=self.on_resize)
        # self.__root_screen = ScreenManager()
        self.root_screen = BoxLayout(size_hint=[1,1])#,md_bg_color=[1,0,0,1])
        # self.root_screen = MDScreen()
        self.nav_layout = MDNavigationLayout()
        
        self.btm_sheet = MyBtmSheet()
        self.my_screen_manager = WindowManager(self.btm_sheet)
        self.bottom_navigation_bar = BottomNavigationBar(self.my_screen_manager)
        # self.my_screen_manager.settings.doConnectionRequest()
        # print('doing connect screen')
        # self.bottom_navigation_bar.close()
        
        # if DEVICE_TYPE == "mobile":
        #     viewport_size=getViewPortSize()
        #     self.root_screen.size_hint=[None, None]
        #     self.root_screen.size=viewport_size
        #     y= Window.height - viewport_size[1] - getStatusBarHeight()
        #     print("Working Y-axis",y)
        #     self.root_screen.y=y
        self.nav_layout.add_widget(self.my_screen_manager)
        self.nav_layout.add_widget(self.bottom_navigation_bar)
        self.nav_layout.add_widget(self.btm_sheet)
            
        self.root_screen.add_widget(self.nav_layout)
        # self.toggle_image_viewer('http://192.168.88.4:8000//home/fabian/Pictures/inspo.png')
        # self.open_file_reader('/home/fabian/Desktop/linked_clipboard.txt')
        return self.root_screen

    def on_resize(self, *args):
        btm_nav_btns=self.bottom_navigation_bar.children if isinstance(self.bottom_navigation_bar.children[0],TabButton) else []
        for btn in btm_nav_btns:
            btn.width=Window.width/3
        
        # print('What app see\'s as window height',Window.height)
        # print('BTM NAV Height',self.bottom_navigation_bar.height)
    def on_resume(self):
        from android_notify import NotificationHandler
        name = NotificationHandler.get_name()
        print("on_resume", name)
        if name == 'change_app_page':
            print('change_app_page inside')
        elif name == 'change_app_color':
            print('change_app_color inside')
        
if __name__ == '__main__':
    Laner().run()




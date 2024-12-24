from kivy.uix.filechooser import FileChooserListView
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivy.core.window import Window
from kivymd.uix.label import MDIcon, MDLabel
from kivy.metrics import dp,sp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition
from kivy.uix.label import Label
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.image import AsyncImage,Image
from kivy.uix.spinner import Spinner
from kivy.utils import platform # OS
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import (MDNavigationDrawer,
                MDNavigationLayout)
from kivymd.uix.divider import MDDivider
import requests
import os, sys, json
from plyer import filechooser

from widgets.popup import Snackbar
from widgets.templates import CustomDropDown, DetailsLabel, DisplayFolderScreen, Header, MDTextButton
from workers.helper import THEME_COLOR_TUPLE, getSERVER_IP, makeDownloadFolder, setHiddenFilesDisplay, setSERVER_IP
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

# For Dev
if DEVICE_TYPE != "mobile":
    # Window.size = (400, 600)
    ...



#Making/Getting Downloads Folder
my_downloads_folder=makeDownloadFolder()
ROOT='/home'
if platform == 'android':
    from kivymd.toast import toast
    from jnius import autoclass
    
    setSERVER_IP('')
    try:
        from android import mActivity # type: ignore
        context =  mActivity.getApplicationContext()
        SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Sendnoti'
        service = autoclass(SERVICE_NAME)
        service.start(mActivity,'')
        print('returned service')
    except Exception as e:
        print(f'Foreground service failed {e}')


    from android.permissions import request_permissions, Permission,check_permission # type: ignore
    from android.storage import app_storage_path, primary_external_storage_path # type: ignore


    ROOT=primary_external_storage_path() if primary_external_storage_path() else '.'
    print(primary_external_storage_path(),'|ROOT|',ROOT)

    print('Asking permission...')
    def check_permissions(permissions):
        for permission in permissions:
            if check_permission(permission) != True:
                return False
        return True


    def request_all_permission():
        try:
            from android import api_version  # type: ignore

            def on_permissions_result(permissions, grants):
                print('What grants is ---->',grants)
                if Permission.POST_NOTIFICATIONS in permissions and grants[permissions.index(Permission.POST_NOTIFICATIONS)]:
                # if Permission.POST_NOTIFICATIONS in permissions and permissions.index(Permission.POST_NOTIFICATIONS) < len(grants) and grants[permissions.index(Permission.POST_NOTIFICATIONS)]:
                    # Notification permission granted, request storage permissions
                    storage_permissions = [
                        Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE
                    ]
                    request_permissions(storage_permissions, on_storage_permissions_result)
                else:
                    print("Notification permission denied")

            def on_storage_permissions_result(permissions, grants):
                if all(grants):
                    # Storage permissions granted, request all files access for Android 11+
                    if api_version >= 30:
                        Environment = autoclass('android.os.Environment')
                        Intent = autoclass('android.content.Intent')
                        Settings = autoclass('android.provider.Settings')

                        if not Environment.isExternalStorageManager():
                            intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                            Clock.schedule_once(lambda dt: mActivity.startActivity(intent), 2)
                else:
                    print("Storage permissions denied")

            # Request notification permission first
            request_permissions([Permission.POST_NOTIFICATIONS], on_permissions_result)


        except Exception as e:
            print(f"Failed to request storage permission: {e}") 
    
    request_all_permission()



# class MDLabel(MDLabel):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.md_bg_color= self.theme_cls.primaryColor
    
Builder.load_string('''

<MyCard>:
    radius: dp(5)
    size_hint:(1,1)
    # theme_bg_color: "Custom"
    on_release: app.my_screen_manager.current_screen.setPath(self.path)
    
    AsyncImage:
        id: test_stuff
        source: root.icon
        size_hint: [.8,.6] if root.icon=='assets/icons/file.png' else [.9,.7]
        fit_mode: 'contain'
        mipmap: True
        pos_hint: {"top":1}
        radius: (dp(5),dp(5),0,0)
    MDButton:
        # theme_bg_color:  "Custom"
        theme_height:  "Custom"
        theme_width:  "Custom"
        opacity: 0 if root.is_dir else 1
        radius: '15sp'
        size_hint:  [None, None]
        width:  '35sp'
        height: '35sp'
        # md_bg_color: [.7,.6,.9,1]
        pos_hint: {"top": .979, "right": .97}
        on_release: app.my_screen_manager.current_screen.showDownloadDialog(root.path)
        
        MDButtonIcon:
            icon: "download"
            pos_hint: {'x':.23,'y':.2}
            # theme_icon_color: "Custom"
            # icon_color: [1,1,1,1]
        
    MDLabel:
        text: root.myFormat(root.text)
        theme_font_size:'Custom'
        font_size: '11sp'
        size_hint: [None, None]
        size: (root.width, 40)
        text_size: (root.width, None)
        # max_lines: 2

<RV>:
    viewclass: 'MyCard'
    size_hint: (1, .9)
    My_RecycleGridLayout:
        id: scroll_content
        default_size: 1, '140sp' # children widgets default size
        default_size_hint: 1, None
        cols:4
        spacing:18
        padding:"10dp"
        size_hint: (1, None)
        height: self.minimum_height + 140
        canvas.before:
            Color:
                rgba: 1, 0, 0, 1  # Red color
            Rectangle:
                pos: self.pos
                size: self.size
        Image:
            id
        (source='spinner.png', size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.spinner.opacity = 0
        self.add_widget(self.spinner)
        self.spinner_anim = Animation(rotation=360, duration=1)
        self.spinner_anim.repeat = True
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


class WindowManager(MDScreenManager):
    screen_history = []  # Stack to manage visited screens
    def __init__(self, btm_sheet,**kwargs):
    # def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btm_sheet=btm_sheet
        self.md_bg_color =[.12,.12,.12,1] if self.theme_cls.theme_style == "Dark" else [0.98, 0.98, 0.98, 1]
        self.size_hint=[1,None]
        self.height=Window.height-sp(65)   # Bottom nav height
        self.pos_hint={'top':1}
        
        # Set theme colors and properties
        # self.theme_cls = MDApp.get_running_app().theme_cls
        # self.theme_cls.primaryColor = [1, 1, 1, 1]
        
        self.add_widget(DisplayFolderScreen(name='upload',current_dir='Home'))
        self.add_widget(DisplayFolderScreen(name='download',current_dir='.'))
        self.add_widget(SettingsScreen())
        self.transition=NoTransition()
        self.current='settings'
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
        # print(self.parent.children,self.parent.children[1].children)
        tabs_buttons_list=self.parent.children[1].children
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
        self.padding=[dp(0),dp(15),dp(0),dp(15)]
        self.line_color=(.2, .2, .2, 0)
        self._radius=1
        self.id=self.text
        self.spacing="2sp"
        self.size_hint=[None,1]
        self.width=Window.width/3
        self.label= MDLabel(
            text=self.text, halign='center',
            font_name='assets/fonts/Helvetica.ttf',
            # theme_text_color="Primary",
            # text_color=self.theme_cls.primaryColor,
            font_size=sp(13),
            )
        self.btn_icon = MDIcon(
                icon=self.icon,
                # font_size__='40sp',
                # size_hint=[.5,.5],
                pos_hint={'center_x': 0.5},
                # theme_text_color="Primary",
                # text_color=self.theme_cls.primaryColor
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
        # return
        # print(self.screen, "==", cur_screen)
        if self.screen == cur_screen:
            # self.btn_icon.theme_text_color = "Custom"
            # self.btn_icon.text_color = THEME_COLOR_TUPLE
            self.label.color = self.theme_cls.primaryColor  
            self.btn_icon.icon_color = self.theme_cls.primaryColor
            
            # self.btn_icon.theme_text_color = "Primary"
            # self.label.theme_text_color = "Primary"
        else:
            # self.btn_icon.theme_text_color = "Primary"
            # self.label.color = self.theme_cls.primaryColor
            # self.btn_icon.icon_color = self.theme_cls.primaryColor
            grey_color=[.6,.6,.6,1]
            self.label.color = grey_color
            self.btn_icon.icon_color = grey_color


        # with open(MY_DATABASE_PATH) as change_mode1:
        #     Bool_theme = json.load(change_mode1)
        #     if Bool_theme['Dark Mode']:
        #         self.btn_icon.text_color=self.label.color = [1, 1, 1, 1]

        #     else:
        #         self.btn_icon.text_color=self.label.color = [0, 0, 0, 1]

        #     if self.screen == cur_screen:
        #         # print(self.screen,cur_screen)
        #         # MDIcon.text_color=Label.color = THEME_COLOR_TUPLE
        #         self.btn_icon.text_color=self.label.color = self.theme_cls.backgroundColor

class BottomNavigationBar(MDNavigationDrawer):
    screen = StringProperty()
    def __init__(self, screen_manager:WindowManager,**kwargs):
        super(BottomNavigationBar, self).__init__(**kwargs)
        self.drawer_type='standard'
        self.set_state('open')
        self.radius=0
        
        
        self.screen_manager=screen_manager
        icons = ['home', 'download', 'connection']
        # icons = ['home', 'server-network-outline', 'connection']
        
        for_label_text = ['Home','Storage','Link']
        screens=screen_manager.screen_names
        self.size_hint =[ 1, None]
        self.height='70sp'
        self.padding=0
        self.spacing=0
        # self.md_bg_color = (.1, 1, 0, .5)
        # self.md_bg_color = (.1, .1, .1, 1)
        self.pos=[0,-2]

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
    switch_state=BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=[1,None]
        self.height='40sp'
        self.padding=[sp(20),0]
        # self.md_bg_color=[1,1,0,1]

        self.add_widget(MDLabel(
            halign='left',valign='center',
                                # text_color=[1,1,1,1],
                                text=self.text))
        self.checkbox_=MDCheckbox(size_hint=(None,None),size=['40sp','40sp'],
                                #   color_active=[.6, .9, .8, 2],color_inactive=[.6, .9, .8, .5],
                                  radius=0,active=self.switch_state,
        # self.checkbox_=MDCheckbox(size_hint=(None,None),size=['40sp','40sp'],icon_color=[.6, .9, .8, 2],theme_icon_color='Custom',theme_bg_color='Custom', _md_bg_color=[1,0,0,1],radius=0,active=self.switch_state,
                                  pos_hint={'right':1,'top':.8}
                                  )
        self.add_widget(self.checkbox_)
        

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
            response=requests.get(f"http://{getSERVER_IP()}:8000/api/isfile",json={'path':path},timeout=2)
            if response.status_code != 200:
                # Clock.schedule_once(lambda dt:Snackbar(h1="Dev pinging for thumb valid"))
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

class PortBoxLayout(MDBoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation= 'horizontal'
        self.padding = [dp(10), dp(10)]
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(50) # Importance for dropdown custom widget (this is the sum of children heights)

        self.add_widget(MDLabel(
            text='port:',theme_font_size='Custom',
            font_size='18sp',adaptive_width=True,
            adaptive_height=True,pos_hint={'center_y': .5},
            theme_text_color="Secondary"
            )
        )
          

        
        self.port_input = MDTextField(
            hint_text="Enter Port Number",
            size_hint=[None,None],
            size=[dp(60),dp(10)],
            pos_hint={'center_y': .5},
            max_height=30,
        )
        self.add_widget(self.port_input)

        # self.verify_button = MDTextButton(
        #     text="Verify",
        #     size_hint=[1, None],
        #     height=sp(40),
        #     
        # )
        self.add_widget(
            MDTextButton(
                text='Verify', font_size='13sp',
                size=[50,35],on_release=self.verify_port,
                radius=0,pos_hint={'center_y': .5}
            )
        )
        
        # self.add_widget(self.verify_button)

    def verify_port(self, instance):
        port = self.port_input.text
        if port.isdigit() and 0 < int(port) < 65536:
            Snackbar(h1="Port is valid")
        else:
            Snackbar(h1="Invalid port number")


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'

        # Main layout
        self.layout = MDBoxLayout(
            orientation='vertical',
            size_hint=[1, 1],
            spacing=sp(10)
        )

        # Header
        self.header = Header(
            size_hint=[1, 0.1],
            text="Settings",
            text_halign='left',
            theme_text_color='Primary',
            title_color=self.theme_cls.primaryColor,
        )

        # Content ScrollView
        scroll = MDScrollView(
            size_hint=[1, 1],
            do_scroll_x=False
        )
        self.content = MDBoxLayout(
            orientation='vertical',
            spacing=sp(20),
            padding=[sp(15), sp(10)],
            adaptive_height=True
        )

        # Categories
        self.ipAddressInput = MDTextField(pos_hint={'center_x': .5}, size_hint=[.8, None], height=dp(80))
        
        self.advanced_options =PortBoxLayout()
        

        self.add_category("Connection", [
            {"type": "text", "title": "Server IP", "widget": self.ipAddressInput},
            {"type": "button", "title": "Verify Connection", "callback": lambda x: self.setIP(self.ipAddressInput.text)},
        ])
        
        self.add_category("Display", [
            {"type": "switch", "switch_state": False, "title": "Show Hidden Files", "callback": self.on_checkbox_active},
            {"type": "switch", "switch_state": True if MDApp.get_running_app().get_stored_theme() == 'Dark' else False, "title": "Dark Mode", "callback": self.toggle_theme}
        ])
        print('Saved theme',MDApp.get_running_app().get_stored_theme())
        self.add_category("Storage", [
            {"type": "button", "title": "Clear Cache", "callback": self.clear_cache},
            {"type": "info", "title": "Storage Used", "value": "Calculate storage"}
        ])
        
        self.add_category("Advanced Options", [{"type": "custom", "widget": self.advanced_options}])

        scroll.add_widget(self.content)
        self.layout.add_widget(self.header)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def add_category(self, title, items):
        if title == 'Advanced Options':
            category=CustomDropDown()
        else:
            category = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing=sp(10)
            )

            # Category header
            category.add_widget(
                MDLabel(
                    text=title,
                    bold=True,
                    theme_text_color="Secondary",
                    adaptive_height=True
                )
            )

        # Category items
        for item in items:
            item_layout = MDBoxLayout(
                adaptive_height=True,
                spacing=sp(10),
                padding=[sp(10), sp(5)]
            )

            if item["type"] == "switch":
                switch = MySwitch(text=item["title"],switch_state=item['switch_state'])
                switch.checkbox_.bind(active=item["callback"])
                item_layout.add_widget(switch)

            elif item["type"] == "text":
                item_layout.add_widget(item["widget"])

            elif item["type"] == "button":
                btn = MDTextButton(
                    text=item["title"],
                    on_release=item["callback"],
                    size_hint=[None, None],
                    size=[sp(120), dp(50)]
                )
                item_layout.add_widget(btn)

            elif item["type"] == "custom":
                item_layout.add_widget(item["widget"])

            category.add_widget(item_layout)

        self.content.add_widget(category)
        self.content.add_widget(MDDivider())
    
    def toggle_theme(self, instance,value):
        # Call the app's toggle_theme method
        MDApp.get_running_app().toggle_theme()

        
    
    def verify_port(self, instance):
        # Add your verification logic here
        pass

    def clear_cache(self, instance):
        # Cache clearing implementation
        
        pass
    def testx(self):
        print("sending new notification")

        from android_notify.core import send_notification
        from android_notify.styles import NotificationStyles

            
        i=self.ipAddressInput.text
        try:
            if i=='1':
                send_notification("Hello", "This is a basic notification.")
            elif i=='2':
                send_notification("Big Text", "This is a notification with a lot of text to show.", style=NotificationStyles.BIG_TEXT)
            elif i=='3':
                send_notification("Large Icon", "Here's a notification with a picture.", style=NotificationStyles.LARGE_ICON, img_path='assets/icons/sql.png')
            elif i == '4':
                send_notification("Big Picture", "Here's a notification with a picture.", style=NotificationStyles.BIG_PICTURE, img_path='assets/imgs/icon.png')
            elif i == '5':
                send_notification(
                    "Inbox Style",
                    "Line 1\nLine 2\nLine 3\nLine 4",
                    style=NotificationStyles.INBOX
                )
            else:
                send_notification("Hello!", i if i else "This is a notification from Kivy.")

        except Exception as e:
            print("Fisrt Noti: ",e)
        # permissions=[Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE]
        # request_permissions(permissions)

    # def test(self):
    #     def test1(file_path):
    #         print(file_path,'img path')
    #         if file_path:
    #             self.img.source=file_path[0]
            # from PIL import Image as PILImage
            # img=PILImage.open(file_path)
            # file_name=os.path.basename(file_path)
            # ext_and_name=os.path.splitext(file_name)
            # new_path=os.path.join('.',f"{ext_and_name[1]}{ext_and_name[0]}")
            # img.save(new_path,optimize=True,quality=80)
            # exit_manager()
            # self.img.reload()
        def exit_manager(path=''):
            # self.filechooser.close()
            print('exit path------------|',path)
            toast('Toast more profess')
        # filechooser.open_file(on_selection=test1)
        
        # print(self.manager.btm_sheet)#.set_state("toggle")
        # layout=FloatLayout()
        # self.filechooser=MDFileManager(exit_manager=exit_manager, select_path=test1)#rootpath=ROOT)
        # self.filechooser.show(ROOT)
        # filechooser.bind(on_selection=test1)
        # layout.add_widget(filechooser)
        # self.add_widget(layout)
        
    def on_checkbox_active(self,checkbox, value):
        setHiddenFilesDisplay(value)
    def setIP(self,text):
        setSERVER_IP(text)
        try:
            response=requests.get(f"http://{text}:8000/ping",json={'passcode':'blah blah'},timeout=.2)
            if response.status_code == 200:
                Snackbar(h1="Verification Successfull")
            else:
                Snackbar(h1="Bad Code check 'Laner PC' for right one")
        except Exception as e:
            print("here---|",e)
            Snackbar(h1="Bad Code check \"Laner PC\" for right one")
            
        print('My address',text, getSERVER_IP())


from widgets.templates import MyBtmSheet
class TypeMapElement(MDBoxLayout):
    selected = BooleanProperty(False)
    icon = StringProperty()
    title = StringProperty()

from kivy.storage.jsonstore import JsonStore
# from kivymd.color_definitions import colors

class Laner(MDApp):
    btm_sheet = ''
    theme_store = JsonStore('theme_settings.json')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Default theme settings
        # self.theme_cls.theme_style='Dark'
        # self.theme_cls.dark_palette = "Amber"
        # self.theme_cls.primary_palette = "Blue"
        # self.theme_cls.accent_palette = "Amber"
        # Default theme settings
        # self.theme_cls.primary_palette = "Blue"
        # self.theme_cls.accent_palette = "Amber"
        # self.theme_cls.theme_style = self.get_stored_theme()
        
    def get_stored_theme(self):
        try:
            return self.theme_store.get('theme')['mode']
        except Exception as e:
            print("Error",e)
            self.theme_store.put('theme', mode='Dark')
            return 'Light'
    
    def toggle_theme(self):
        current = self.theme_cls.theme_style
        new_theme = 'Dark' if current == 'Light' else 'Light'
        self.theme_cls.theme_style = new_theme
        self.theme_store.put('theme', mode=new_theme)
        
        # Update theme for main navigation and buttons
        for each in self.bottom_navigation_bar.walk():
            if isinstance(each, TabButton):
                each.checkWidgetDesign(self.my_screen_manager.current)
                
        # Update header title colors
        # for screen in self.my_screen_manager.screens:
        #     # if hasattr(screen, 'header'):
        #     #     # screen.header.header_label.theme_text_color = "Custom"
        #     #     # screen.header.header_label.text_color = THEME_COLOR_TUPLE
            
        #     #     screen.header.header_label.theme_text_color = "Primary"
        #     #     screen.header.header_label.text_color = self.theme_cls.primaryColor
            
        light_grey_for_dark_theme=[.15,.15,.15,1]
        light_grey_for_light_theme=[0.92, 0.92, 0.92, 1]
        if self.theme_cls.theme_style == "Dark":
            self.my_screen_manager.md_bg_color =[.12,.12,.12,1]
            
            for screen in self.my_screen_manager.screens:
                screen.header.md_bg_color = light_grey_for_dark_theme
                
                # Update DisplayFolderScreen backgrounds
                if isinstance(screen, DisplayFolderScreen):
                    screen.details_box.md_bg_color = light_grey_for_dark_theme
                    screen.details_label.color =[.8, .8, .8, 1]
                    
                
        else:
            self.my_screen_manager.md_bg_color = [0.98, 0.98, 0.98, 1]
            
            # Update DisplayFolderScreen backgrounds
            for screen in self.my_screen_manager.screens:
                screen.header.md_bg_color = light_grey_for_light_theme
                if isinstance(screen, DisplayFolderScreen):
                    screen.details_box.md_bg_color =light_grey_for_light_theme
                    screen.details_label.color = [0.41, 0.42, 0.4, 1]
                    
                    
    def build(self):
        self.title = 'Laner'
        self.theme_cls.theme_style = self.get_stored_theme()
        self.theme_cls.primary_palette = "White"
        # self.theme_cls.accent_palette = "Blue"
        
        # self.theme_cls.backgroundColor = THEME_COLOR_TUPLE
        
        # Theme configuration
        # self.theme_cls.material_style = "M3"
        # self.theme_cls.primary_hue = "500"
        # self.theme_cls.accent_hue = "500"
        
        root_screen = MDScreen()
        nav_layout = MDNavigationLayout()
        
        self.btm_sheet = MyBtmSheet()
        self.my_screen_manager = WindowManager(self.btm_sheet)
        self.bottom_navigation_bar = BottomNavigationBar(self.my_screen_manager)
        
        nav_layout.add_widget(self.my_screen_manager)
        nav_layout.add_widget(self.bottom_navigation_bar)
        nav_layout.add_widget(self.btm_sheet)
        
        root_screen.add_widget(nav_layout)
        return root_screen

if __name__ == '__main__':
    Laner().run()

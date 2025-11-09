import random
import traceback

from kivy.utils import platform
from jnius import autoclass, cast
import os, sys, json, requests, asyncio, threading,time


from kivy.metrics import sp
# from kivy.uix.scatterlayout import ScatterLayout

from kivymd.app import MDApp
# from kivymd.uix.gridlayout import MDGridLayout
# from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.divider import MDDivider

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDIcon, MDLabel

from components.loading_layout import LoadingScreen
from utils import Settings,NetworkManager,AsyncRequest,FindHosts

from kivy.clock import Clock

from components import Header,HeaderBasic
from components.templates import CustomDropDown, MDTextButton,MyBtmSheet
from utils.typing.main import Laner
from utils.helper import setHiddenFilesDisplay,test101,log_error_to_file
from utils.constants import PORTS
from components.popup import Snackbar, PopupScreen


try:
    from android_notify.config import run_on_ui_thread
    from android_notify import Notification
except Exception as e:
    print("failed at import....")
    error_traceback = traceback.format_exc()
    log_error_to_file(error_traceback)
    


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

class PortBoxLayout(MDBoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app=MDApp.get_running_app()
        self.orientation= 'horizontal'
        self.padding = [sp(10), sp(10)]
        self.spacing = sp(10)
        self.size_hint_y = None
        self.height = sp(50) # Importance for dropdown custom widget (this is the sum of children heights)

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
            size_hint_y=None,
            height=sp(25),
            width=sp(100),
            # size=[sp(70),sp(20)],
            pos_hint={'center_y': .5},
            max_height=sp(40),
        )
        self.add_widget(self.port_input)

        self.add_widget(
            MDTextButton(
                text='Verify',
                # font_size='13sp',
                size=[sp(55),sp(30)],
                on_release=self.verify_port,
                radius=0,pos_hint={'center_y': .5}
            )
        )

    def verify_port(self, instance=None):
        port = self.port_input.text
        ports =  [
                    8000, 8080, 9090, 10000, 11000, 12000, 13000, 14000, 
                    15000, 16000, 17000, 18000, 19000,
                    20000, 22000, 23000, 24000, 26000,
                    27000, 28000, 29000, 30000
                ]
        ip_address= self.app.settings.get('server', 'ip')
        print('Port:',port,'ip_address',ip_address)
        print(f"http://{ip_address}:{port}/ping")
        if port.isdigit() and int(port) in ports:
            try:
                response=requests.get(f"http://{ip_address}:{port}/ping",json={'passcode':'08112321825'},timeout=.2)
                
                if response.status_code == 200:
                    self.app.settings.set('server', 'port', port)
                    Snackbar(h1="Port is valid")
                else:
                    Snackbar(h1="Try tying in code from Laner PC first")
            except Exception as e:
                print("Dev Port Error: ",e)
            
        else:
            Snackbar(h1="Invalid port Check 'Laner PC' for right one")

class ScanningLayout(MDRelativeLayout,PopupScreen):
    def __init__(self, change_working_server, **kwargs):
        super().__init__(**kwargs)
        # self.md_bg_color = [1, 0, 1, 1]
        self.md_bg_color =[.12,.12,.12,1] if self.theme_cls.theme_style == "Dark" else [0.98, 0.98, 0.98, 1]
        self.loading_widget=None
        self.change_working_server=change_working_server
        
        # Header
        self.header = HeaderBasic(
            text='Tap Your PC to Request Connection',back_btn_func=self.close,
            height=70,pos_hint={'top': 1}
        )
        self.add_widget(self.header)

        # Found Laner-PC's Container
        self.found_pcs_container = MDBoxLayout(md_bg_color=[.41, .41, .4, 1], adaptive_width=True, adaptive_height=True,
                                               pos_hint={'center_x': 0.5, 'center_y': 0.7}, orientation='vertical',
                                               spacing=sp(20), padding=[sp(20)], radius=[sp(10)])
        self.add_widget(self.found_pcs_container)

        # Controls Btn
        control_btns_layout = MDBoxLayout(adaptive_width=True, adaptive_height=True, orientation='vertical',
                                          spacing=sp(10),
                                          pos_hint={'center_x': 0.5, 'y': .05})
        self.retry_scan_btn = MDTextButton(on_release=self.start_scan, adaptive_width=True,
                                           disabled=True)
        cancel_btn = MDTextButton(text='Close', on_release=self.close, adaptive_width=True, pos_hint={'center_x': 0.5})
        control_btns_layout.add_widget(self.retry_scan_btn)
        control_btns_layout.add_widget(cancel_btn)

        self.add_widget(control_btns_layout)
        self.start_scan()
    def start_scan(self,widget=None):
        self.retry_scan_btn.disabled=True
        self.retry_scan_btn.text='Scanning...'
        self.found_pcs_container.clear_widgets()
        FindHosts().scan_ports(ports=PORTS, timeout=5, on_find=self._render_pc, on_complete=self._done_finding_pcs)

    def _done_finding_pcs(self, ips_list: list):
        # print('gg data ', ips_list)
        self.retry_scan_btn.disabled = False
        self.retry_scan_btn.text = 'Scan Again'

    def _render_pc(self, sent_data=None):
        self.found_pcs_container.add_widget(
            MDTextButton(text=sent_data['name'], on_release=lambda x: self._ask_laner_pc_for_password(sent_data),
                         adaptive_width=True))

    def _ask_laner_pc_for_password(self, sent_data: dict):
        """
            {'name': '', 'ip': '','websocket_port':''}
        """
        self.disabled = True
        FindHosts().start_password_request(sent_data['ip'], sent_data['websocket_port'],
                                           self._received_password_response)
        self.loading_widget = LoadingScreen()
        self.add_widget(self.loading_widget)
        print(sent_data)

    def _received_password_response(self, response: dict):
        self.loading_widget.remove()
        print(response)
        if response.get('auth'):
            self._set_pc_data(response)
            self.md_bg_color = [0, 1, 0, 1]
            self.change_working_server(ip=response['ip'])
            self.close()
        elif not response.get('auth', False):  # , False) very important
            self.md_bg_color = [1, 0, 0, 1]
            Snackbar('Request Rejected')
        elif response.get('error'):
            Snackbar('Connection Error ' + response.get('error', ''))
            self.md_bg_color = [0, 0, 1, 1]
        self.disabled = False

    @staticmethod
    def _set_pc_data(response_data):
        """Sets new PC and adds PC to pcs object because Laner-PC accepted request"""
        ip = response_data['ip']
        port = response_data['main_server_port']
        settings = Settings()
        settings.set('server', 'ip', ip)
        settings.set('server', 'port', port)
        data = {'ip': ip, 'token': response_data['token'], 'port': port}
        settings.set_pc(pc_name=response_data['name'], value=data)


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app:Laner=MDApp.get_running_app()

        self.name = 'settings'
        self.pc_name = ''
        # Main layout
        self.layout = MDBoxLayout(
            orientation='vertical',
            size_hint=[1, 1],
            spacing=sp(10)
        )

        # Header
        self.header = Header(
            # size_hint=[1, 0.1],
            screen=self,
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
        self.ipAddressInput = MDTextField(pos_hint={'center_x': .5}, size_hint=[.8, None], height=sp(80))

        self.advanced_options =PortBoxLayout()

        # use discover | enter specify address
        self.add_category("Connection", [
            {"type": "label","text": "Use Discovery"},
            {'size':[sp(150),sp(50)],"type": "button",'id':'', "title": "Find PC", "callback": self.doConnectionRequest},
            {"type": "label","text": "Enter Specify Address"},
            {'size':[sp(130),sp(50)],"type": "text", 'id':'ip_addr_input',"title": "Server IP", "widget": self.ipAddressInput},
            {'size':[sp(100),sp(50)],"type": "button",'id':'connect_btn', "title": "Verify Connection", "callback": self.setIP},
        ])

        self.add_category("Display", [
            {"type": "switch", "switch_state": False, "title": "Show Hidden Files", "callback": self.on_checkbox_active},
            {"type": "switch", "switch_state": True if MDApp.get_running_app().get_stored_theme() == 'Dark' else False, "title": "Dark Mode", "callback": self.toggle_theme}
        ])

        self.add_category("Storage", [
            {'size':[sp(100),sp(50)],"type": "button", 'id':'clear_btn', "title": "Clear Cache", "callback": self.clear_cache},
    {'size':[sp(120),sp(50)], "type": "button", 'id':'backup_btn', "title": "Backup Data", "callback": self.backup_data},
    {'size':[sp(120),sp(50)], "type": "button", 'id':'restore_btn', "title": "Restore Data", "callback": self.restore_data},
            {"type": "info", "title": "Storage Used", "value": "Calculate storage"}
        ])

        self.add_category("Advanced Options", [{"type": "custom", "widget": self.advanced_options}])

        scroll.add_widget(self.content)
        self.layout.add_widget(self.header)
        self.layout.add_widget(scroll)
        self.layout.add_widget(MDBoxLayout(height='70sp',size_hint=[1,None]))  # Buffer cause of bottom nav bar (will change to padding later)
        self.add_widget(self.layout)
        self.scanningScreen=None
        # print('not doing auto connect')
        # self.autoConnect()

    def doConnectionRequest(self, widget=None):
        self.scanningScreen = ScanningLayout(
                                change_working_server=self.setIP,
                                bottom_navigation_bar=self.app.bottom_navigation_bar)
        self.add_widget(self.scanningScreen)

    def add_category(self, title, items):
        def addID(item: dict, widget: object = None) -> None:
            """Add widget to ids dictionary if item contains an 'id' key.

            Args:
                item (dict): Dictionary containing widget information
                widget (object, optional): Widget to add to ids dictionary.
                    Defaults to item["widget"] if exists, otherwise None.

            Example:
                >>> item = {"id": "my_button", "widget": Button()}
                >>> addID(item)
                >>> self.ids["my_button"]  # Returns Button instance
            """
            widget = item["widget"] if "widget" in item else widget
            if "id" in item:
                self.ids[item["id"]] = widget

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
                addID(item)
                item_layout.add_widget(item["widget"])

            elif item["type"] == "label":
                label = MDLabel(
                    text=item["text"],
                    theme_text_color="Primary",
                    adaptive_height=True

                )
                item_layout.add_widget(label)

            elif item["type"] == "button":
                btn = MDTextButton(
                    text=item["title"],
                    size_hint=[None, None],
                    size=item['size'],
                    # size=[sp(130), sp(50)] if item['id'] in ['connect_btn'] else [sp(100),sp(50)]
                )
                btn.bind(on_release=item["callback"])

                addID(item,widget=btn)
                item_layout.add_widget(btn)

            elif item["type"] == "custom":
                item_layout.add_widget(item["widget"])

            category.add_widget(item_layout)

        self.content.add_widget(category)
        self.content.add_widget(MDDivider())

    def toggle_theme(self, instance,value):
        self.app.get_running_app().toggle_theme()

    def clear_cache(self, instance):
        try:
            notification = Notification(
                title="Test Notification",
                message="This is a test message."
                )
            notification.addLine("Line 1: Test data")
            notification.addLine("Line 2: More test data")
            notification.addLine("Line 3: Placeholder info")
            notification.send()
        except Exception as e:
            print("failed at sending1....")
            
            error_traceback = traceback.format_exc()
            log_error_to_file(error_traceback)
        finally:
            return
        try:
            test101()
        except Exception as e:
            Notification(title="Error", body=str(e)).send()
        # try:
        #     show_custom_layout_notification()
        # except Exception as e:
        #     print("Color Expectation 1: ",e)
        #     traceback.print_exc()

        try:
            n=Notification(
                title='Your device will restart in 10 mins to complete important updates',
                message='Make sure to save your work to avoid losing any unsaved changes',
                title_color='#FF5722',
                message_color='#3693e4',
                logs=True
            )
            n.addButton('open app',lambda :print('clicked'))
            n.setLargeIcon('assets/imgs/profile.jpg')
            n.setBigPicture('assets/imgs/a.jpg')
            n.progress_max_value=100
            n.updateProgressBar(current_value=10,message='super custom',title='custom title')
            n.send()

            n = Notification(
                title='Your device will restart in 10 mins to complete important updates',
                message='Make sure to save your work to avoid losing any unsaved changes',
                logs=True
            )
            n.addButton('open app', lambda: print('clicked'))
            n.setLargeIcon('assets/imgs/profile.jpg')
            n.setBigPicture('assets/imgs/a.jpg')
            n.progress_max_value = 100
            n.updateProgressBar(current_value=10, message='super custom', title='custom title')
            n.send()

            n = Notification(
                title='Your device will restart in 10 mins to complete important updates',
                message='Make sure to save your work to avoid losing any unsaved changes',
                title_color='#FF5722',
                message_color='#3693e4',
                logs=True
            )
            n.addButton('open app', lambda: print('clicked'))
            n.setLargeIcon('assets/imgs/profile.jpg')
            n.setBigPicture('assets/imgs/a.jpg')
            n.send()
            # show_custom_notification("Hi", " Fabian", "You have 2 new messages")
        except Exception as e:
            print("Color Expectation 2: ",e)
            traceback.print_exc()

        # try:
        #     show_spannable_notification()
        # except Exception as e:
        #     print("Color Expectation 3: ",e)
        #     traceback.print_exc()
        # self.open_folder(instance)

        # Cache clearing implementation

        # pass

    def on_checkbox_active(self,checkbox_instance, value):
        setHiddenFilesDisplay(value)

    def autoConnect(self):
        ip_input=self.ids['ip_addr_input']
        connect_btn=self.ids['connect_btn']
        stay_active_fun=False
        doing_call=False
        notif : Notification = None
        def failed_noti(erro_name):
            nonlocal doing_call
            print(erro_name)
            doing_call = False


        def set_data(pc_name,ip_address):
            self.pc_name = pc_name
            ip_input.text="Connected to: "+pc_name
            ip_input.disabled=True
            connect_btn.text= 'Disconnect'
            self.change_button_callback(connect_btn,self.setIP, self.disconnect,ip_address)

        def update_noti(good,pc_name=''):
            nonlocal notif
            fallback_name=self.pc_name or "PC"
            if not notif:
                notif = Notification(logs=False,channel_name='Active State')
                notif.send(silent=True,persistent=True,close_on_click=False)
            notif.updateTitle('Laner Connected' if good else 'Laner Disconnected')
            notif.updateMessage(f"Connection To {pc_name} Active" if good else f"No Active Connection To {fallback_name}")

        def success(pc_name,ip_address):
            nonlocal stay_active_fun, doing_call
            set_data(pc_name,ip_address)
            update_noti(True,pc_name)
            # print('not checking for new ip')
            # return # comment out for autoconnect
            if not stay_active_fun:
                Snackbar(h1="Auto Connect Successfull")
                stayActive()
            doing_call = False
            stay_active_fun=True

        def stayActive():
            nonlocal doing_call
            # print('not checking for new ip')
            # return
            def do_check(dt):
                nonlocal doing_call
                if not doing_call:
                    doing_call = True
                    AsyncRequest().find_server_with_ports(success,failed_noti)

            # Scans Ports For If InCase IP Has Changed
            Clock.schedule_interval(do_check,2)
            # According to my calculations AsyncRequest().find_server_with_ports Takes 6 secs to complete if scanning all PORTS

        def fun():
            print('not checking for new ip')
        AsyncRequest().auto_connect(success,failed=stayActive)# comment out for autoconnect
        # AsyncRequest().auto_connect(success,failed=fun)

    def setIP(self, widget_that_called=None,ip=''):
        ip_input=self.ids['ip_addr_input']
        input_ip_address:str=ip or ip_input.text.strip()
        self.app.settings.set('server', 'ip', input_ip_address)
        port=MDApp.get_running_app().settings.get('server', 'port')
        # TODO create an async quick scanner to check valid port from a list of ports


        def success(pc_name):
            self.pc_name = pc_name
            self.app.settings.add_recent_connection(input_ip_address)

            connect_btn=self.ids['connect_btn']

            ip_input.text="Connected to: "+self.pc_name
            ip_input.disabled=True
            connect_btn.text= 'Disconnect'
            self.change_button_callback(connect_btn,self.setIP, self.disconnect,input_ip_address)

            self.advanced_options.port_input.text = str(Settings().get('server','port'))
            Snackbar(h1="Verification Successfull")
        def failed():
            Snackbar(h1="Bad Code check 'Laner PC' for right one")
        AsyncRequest().ping(input_ip_address,port,success,failed)
        # text=ip_input.text
        # buttons = MDApp.get_running_app().bottom_navigation_bar.children
        # for btn in buttons:
        #     if 'sp' not in text:
        #         btn.spacing=text

        #     else:
        #         btn.btn_icon.font_size=text

        print(input_ip_address,'===', self.app.settings.get('server', 'ip'))

    def change_button_callback(self, button, old_callback,new_callback,*args):
        button.unbind(on_release=old_callback)
        button.bind(on_release=new_callback)

    def disconnect(self,instance):
        ip_input=self.ids['ip_addr_input']
        connect_btn=self.ids['connect_btn']

        ip_input.text=self.app.settings.get('server', 'ip')
        ip_input.disabled=False
        connect_btn.text= 'Verify Connection'
        self.change_button_callback(connect_btn,self.disconnect, self.setIP,connect_btn)
        self.app.settings.set('server', 'ip', '')
        Snackbar(h1="Disconnected from " + self.pc_name)
        print('Disconnected')

    def open_folder(self, instance):
        if platform != 'android':
            print("This only works on Android.")
            return

        folder_path = "/storage/emulated/0/Download"  # Change this to your folder

        try:
            File = autoclass('java.io.File')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            folder = File(folder_path)
            context = cast('android.content.Context', PythonActivity.mActivity)

            uri = FileProvider.getUriForFile(
                context,
                context.getPackageName() + ".fileprovider",
                folder
            )

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "*/*")
            intent.setFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(intent)

        except Exception as e:
            print("Could not open folder:", e)

    def disable_click(self,popup:PopupScreen=None):
        self.layout.disabled=True

    def enable_click(self):
        self.layout.disabled=False

    def backup_data(self, instance):
        try:
            Snackbar(h1="Backing up data...")
            # Add your backup logic here
            print("Backup started...")
            # Simulate process
            time.sleep(1)
            Snackbar(h1="Backup completed successfully")
        except Exception as e:
            print("Backup error:", e)
            error_traceback = traceback.format_exc()
            log_error_to_file(error_traceback)

    def restore_data(self, instance):
        try:
            from android_notify.core import asks_permission_if_needed
            asks_permission_if_needed(no_androidx=True)
        except Exception as e:
            print("Restore error:", e)
            error_traceback = traceback.format_exc()
            log_error_to_file(error_traceback)


@run_on_ui_thread
def show_spannable_notification():
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity

    # Required Java classes
    SpannableString = autoclass('android.text.SpannableString')
    ForegroundColorSpan = autoclass('android.text.style.ForegroundColorSpan')
    Spanned = autoclass('android.text.Spanned')

    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    Build_VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
    Color = autoclass('android.graphics.Color')

    channel_id = "color_channel"
    channel_name = "Color Notifications"

    # Create NotificationChannel for Android 8+
    if Build_VERSION.SDK_INT >= Build_VERSION_CODES.O:
        channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
        manager = context.getSystemService(NotificationManager)
        manager.createNotificationChannel(channel)

    # Create SpannableString and apply spans
    return
    title_text = SpannableString("Hello Fabian")
    title_text.setSpan(ForegroundColorSpan(Color.RED), 0, 5, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
    title_text.setSpan(ForegroundColorSpan(Color.BLUE), 6, 12, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)\
        .setSmallIcon(autoclass("android.R$drawable").ic_menu_save)\
        .setContentTitle(cast('java.lang.CharSequence', title_text))\
        .setContentText("This is a dynamic color notification")\
        .setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)

    notification = builder.build()
    # NotificationManagerCompat.from_(context).notify(1, notification)
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    manager = cast(NotificationManagerCompat, notification_service)
    manager.notify(1082, notification)

# @run_on_ui_thread
# def show_custom_notification(title1, title2, message):
#     PythonActivity = autoclass('org.kivy.android.PythonActivity')
#     context = PythonActivity.mActivity
#     NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
#     NotificationManager = autoclass('android.app.NotificationManager')
#     NotificationChannel = autoclass('android.app.NotificationChannel')
#     RemoteViews = autoclass('android.widget.RemoteViews')
#
#     # Defaults
#     notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
#     notification_manager = cast(NotificationManager, notification_service)
#     channel = NotificationChannel('default_channel', 'default_channel', NotificationManager.IMPORTANCE_DEFAULT)
#     if notification_manager.getNotificationChannel('default_channel') is None:
#         notification_manager.createNotificationChannel(channel)
#
#
#     builder = NotificationCompatBuilder(context, 'default_channel')
#     builder.setSmallIcon(context.getApplicationInfo().icon)
#
#     # Create RemoteViews
#     resources = context.getResources()
#     package_name = context.getPackageName()

#     ids
#     small = resources.getIdentifier("small", "layout", package_name)
#     large = resources.getIdentifier("large", "layout", package_name)
#
#     notificationLayout = RemoteViews(package_name, small)
#     notificationLayoutExpanded = RemoteViews(package_name, large)
#     print('small: ',small,'big: ',large, 'notificationLayout: ',notificationLayout, 'notificationLayoutExpanded: ',notificationLayoutExpanded)
#
#     builder.setStyle(autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')())
#     builder.setCustomContentView(notificationLayout)
#     builder.setCustomBigContentView(notificationLayoutExpanded)
#     builder.setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)
#     notification_manager.notify(2351, builder.build())

# @run_on_ui_thread
def show_custom_layout_notification():
    # Java context
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity

    # Load required Java classes
    # LayoutInflater = autoclass('android.view.LayoutInflater')
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
    NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    Build_VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
    R = autoclass('android.R')

    # Create NotificationChannel (Android 8+)
    channel_id = "custom_channel"
    channel_name = "Custom Layout Notifications"

    if Build_VERSION.SDK_INT >= Build_VERSION_CODES.O:
        channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
        notification_manager = context.getSystemService(NotificationManager)
        notification_manager.createNotificationChannel(channel)

    # Inflate custom view from XML
    inflater = context.getSystemService(context.LAYOUT_INFLATER_SERVICE)
    layout = inflater.inflate(
        context.getResources().getIdentifier("custom_colored_title", "layout", context.getPackageName()),
        None
    )

    # Set the content title programmatically (optional)
    title_part1 = layout.findViewById(
        context.getResources().getIdentifier("title_part1", "id", context.getPackageName()))
    title_part2 = layout.findViewById(
        context.getResources().getIdentifier("title_part2", "id", context.getPackageName()))

    # title_part1.setText("Hello")
    # title_part2.setText(" Fabian")

    # .setSmallIcon(R.drawable.ic_dialog_info) \
        # Build and show notification
    builder = NotificationCompatBuilder(context, channel_id) \
        .setSmallIcon(context.getApplicationInfo().icon) \
        .setCustomContentView(layout) \
        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
    notification = builder.build()
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    manager = cast(NotificationManagerCompat, notification_service)
    # NotificationManagerCompat.from_(context).notify(1, )
    manager.notify(251, notification)
    print('sent /////////////////////////////////////////////////')


@run_on_ui_thread
def show_custom_notification(title1, title2, message):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationManager = autoclass('android.app.NotificationManager')
    RemoteViews = autoclass('android.widget.RemoteViews')
    NotificationChannel = autoclass('android.app.NotificationChannel')

    # Defaults
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    notification_manager = cast(NotificationManager, notification_service)
    channel_id='default_channel1'
    channel_name='Default Channel 1'
    channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_HIGH)
    if notification_manager.getNotificationChannel(channel_id) is None:
        notification_manager.createNotificationChannel(channel)

    builder = NotificationCompatBuilder(context, channel_id)
    builder.setSmallIcon(context.getApplicationInfo().icon)

    # Create RemoteViews
    resources = context.getResources()
    package_name = context.getPackageName()

    layout_id = resources.getIdentifier("custom_colored_onepart_title", "layout", package_name)
    title_part1_id = resources.getIdentifier("title_part1", "id", package_name)
    title_part2_id = resources.getIdentifier("title_part2", "id", package_name)
    message_id = resources.getIdentifier("message", "id", package_name)
    print('layout_id: ',layout_id, 'title_part1_id: ',title_part1_id,'title_part2_id: ',title_part2_id,'message_id: ',message_id)

    notificationLayout = RemoteViews(package_name, layout_id)

    # Dynamically set texts
    notificationLayout.setTextViewText(title_part1_id, title1)
    notificationLayout.setTextViewText(title_part2_id, title2)
    notificationLayout.setTextViewText(message_id, message)

    # print('notificationLayout: ',notificationLayout)

    builder.setStyle(autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')())
    builder.setCustomContentView(notificationLayout)
    builder.setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)
    notification_manager.notify(2351+random.randint(0,100), builder.build())

    # notificationLayoutExpanded = RemoteViews(package_name, big)
    # builder.setCustomBigContentView(notificationLayoutExpanded)

import os, sys, json, requests, asyncio, threading,time
from kivy.metrics import sp

from kivymd.app import MDApp
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
from utils import Settings,NetworkManager,AsyncRequest
from android_notify import send_notification,Notification,NotificationStyles
from kivy.clock import Clock

from components import Header
from components.templates import CustomDropDown, MDTextButton,MyBtmSheet
from components.popup import Snackbar
from utils.typing.main import Laner
from utils.helper import setHiddenFilesDisplay
from utils.constants import PORTS

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

    def verify_port(self, instance):
        port = self.port_input.text
        ports =  [
                    8000, 8080, 9090, 10000, 11000, 12000, 13000, 14000, 
                    15000, 16000, 17000, 18000, 19000,
                    20000, 22000, 23000, 24000, 26000,
                    27000, 28000, 29000, 30000
                ]
        ip_address= self.app.settings.get('server', 'ip')
        print('Port:',port,'ip_address',ip_address)
        print("http://{ip_address}:{port}/ping")
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
            {'size':[sp(150),sp(50)],"type": "button",'id':'', "title": "Request Connection", "callback": self.doConnectionRequest},
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
            {"type": "info", "title": "Storage Used", "value": "Calculate storage"}
        ])

        self.add_category("Advanced Options", [{"type": "custom", "widget": self.advanced_options}])

        scroll.add_widget(self.content)
        self.layout.add_widget(self.header)
        self.layout.add_widget(scroll)
        self.layout.add_widget(MDBoxLayout(height='70sp',size_hint=[1,None]))  # Buffer cause of bottom nav bar (will change to padding later)
        self.add_widget(self.layout)
        print('not doing auto connect')
        # self.autoConnect()
    def doConnectionRequest(self,widget=None):
        self.app.bottom_navigation_bar.close()
        self.scanningScreen=MDRelativeLayout(md_bg_color=[1,0,1,1])
        # self.scanningScreen.orientation='vertical'
        msg = MDLabel(text='Tap Your PC to Request Connection',md_bg_color=[1,0,.5,1],pos_hint={'top':1})
        msg.adaptive_height=True

        self.scanningScreen.add_widget(msg)
        self.add_widget(self.scanningScreen)
        res=NetworkManager().scan_ports(ports=PORTS,timeout=5,on_find=self._render_pc)
    def _render_pc(self, sent_data=None):
        if sent_data is None:
            sent_data = {'name': '', 'ip': '','websocket_port':''}
        y_pos = len([child for child in self.scanningScreen.children if isinstance(child, MDTextButton)])+1
        self.scanningScreen.add_widget(MDTextButton(text=sent_data['name'], y=y_pos * 40, on_release=lambda x: self._ask_laner_pc_for_password(sent_data), adaptive_width=True))
    def _ask_laner_pc_for_password(self, sent_data:dict):
        """
            {'name': '', 'ip': '','websocket_port':''}
        """
        self.disabled=True
        NetworkManager().start_password_request(sent_data['ip'], sent_data['websocket_port'], self._received_password_response)
        self.loading_widget = LoadingScreen()
        self.scanningScreen.add_widget(self.loading_widget)
        print(sent_data)
    def _received_password_response(self, response):
        self.loading_widget.remove()
        print(response)
        self.disabled=False

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
        # Call the app's toggle_theme method
        MDApp.get_running_app().toggle_theme()


    def clear_cache(self, instance):
        # Cache clearing implementation

        pass
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
            print('not checking for new ip')
            return # comment out for autoconnect
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
            #According to my calculations AsyncRequest().find_server_with_ports Takes 6 secs to complete if scanning all PORTS

        def fun():
            print('not checking for new ip')
        # AsyncRequest().auto_connect(success,failed=stayActive)# comment out for autoconnect
        AsyncRequest().auto_connect(success,failed=fun)

    def setIP(self, widget_that_called):
        ip_input=self.ids['ip_addr_input']
        input_ip_address:str=ip_input.text.strip()
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

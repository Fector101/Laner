from imports import *
#Making/Getting Downloads Folder
if platform == 'android':
    my_downloads_folder=makeDownloadFolder()
    requestMultiplePermissions()
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
        self.add_widget(DisplayFolderScreen(name='download',current_dir='.'))
        self.add_widget(SettingsScreen())
        self.transition=NoTransition()
        self.current='upload'
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
    def Android_back_click(self, window, key, *largs):
        """Handle the Android back button."""
        if key == 27:  # Back button key code
            if self.current != 'settings' and len(self.current_screen.screen_history):
                # might switch to "if []:" since it works on python but "if len([]):" is more understandable
                # print(self.current_screen.screen_history)
                last_dir = self.current_screen.screen_history.pop()
                self.current_screen.set_folder(last_dir, False)
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
        self.spacing="10"
        self.size_hint=[None,1]
        self.width=Window.width/3
        self.label= MDLabel(
            text=self.text, halign='center',
            font_name='assets/fonts/Helvetica.ttf',
            # theme_text_color="Primary",
            # text_color=self.theme_cls.primaryColor,
            font_size=sp(12),
            theme_font_size="Custom"
            
            )
        self.btn_icon = MDIcon(
                icon=self.icon,
                font_size=sp(30),
                theme_font_size="Custom",
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
        if self.screen == cur_screen:
            self.label.color = self.theme_cls.primaryColor  
            self.btn_icon.icon_color = self.theme_cls.primaryColor
        else:
            grey_color=[.6,.6,.6,1]
            self.label.color = grey_color
            self.btn_icon.icon_color = grey_color

class BottomNavigationBar(MDNavigationDrawer):
    screen = StringProperty()
    def __init__(self, screen_manager:WindowManager,**kwargs):
        super(BottomNavigationBar, self).__init__(**kwargs)
        self.drawer_type='standard'
        self.set_state('open')
        self.radius=0
        
        
        self.screen_manager=screen_manager
        icons = ['home', 'download', 'link']
        # icons = ['home', 'server-network-outline', 'connection']
        
        for_label_text = ['Home','Storage','Link']
        screens=screen_manager.screen_names
        self.size_hint =[ 1, None]
        self.size_hint_y= None
        self.height='70sp'
        # self.height=sp(70)
        self.padding=0
        self.spacing=0
        # self.md_bg_color = (.1, 1, 0, .5)
        # self.md_bg_color = (.1, .1, .1, 1)
        self.pos=[0,-1]
        self.closing_time=0

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
    def close(self,widget=None):
        self.set_state('close')
    def open(self,widget=None):
        self.set_state('open')

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
        self.ipAddressInput = MDTextField(pos_hint={'center_x': .5}, size_hint=[.8, None], height=dp(80))
        
        self.advanced_options =PortBoxLayout()
        

        self.add_category("Connection", [
            {"type": "text", 'id':'ip_addr_input',"title": "Server IP", "widget": self.ipAddressInput},
            {"type": "button",'id':'connect_btn', "title": "Verify Connection", "callback": self.setIP},
        ])
        
        self.add_category("Display", [
            {"type": "switch", "switch_state": False, "title": "Show Hidden Files", "callback": self.on_checkbox_active},
            {"type": "switch", "switch_state": True if MDApp.get_running_app().get_stored_theme() == 'Dark' else False, "title": "Dark Mode", "callback": self.toggle_theme}
        ])
        
        self.add_category("Storage", [
            {"type": "button", 'id':'clear_btn', "title": "Clear Cache", "callback": self.clear_cache},
            {"type": "info", "title": "Storage Used", "value": "Calculate storage"}
        ])
        
        self.add_category("Advanced Options", [{"type": "custom", "widget": self.advanced_options}])

        scroll.add_widget(self.content)
        self.layout.add_widget(self.header)
        self.layout.add_widget(scroll)
        self.layout.add_widget(MDBoxLayout(height='70sp',size_hint=[1,None]))  # Buffer cause of bottom nav bar (will change to padding later)
        self.add_widget(self.layout)
        self.autoConnect()

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

            elif item["type"] == "button":
                btn = MDTextButton(
                    text=item["title"],
                    size_hint=[None, None],
                    size=[sp(130), sp(50)] if item['id'] in ['connect_btn'] else [sp(100),sp(50)]
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
            if not stay_active_fun:
                Snackbar(h1="Auto Connect Successfull")
                stayActive()
            doing_call = False
            stay_active_fun=True
        
        def stayActive():
            nonlocal doing_call
            def do_check(dt):
                nonlocal doing_call
                if not doing_call:
                    doing_call = True
                    AsyncRequest().find_server_with_ports(success,failed_noti)
                    
            # Scans Ports For If InCase IP Has Changed
            Clock.schedule_interval(do_check,2)
            #According to my calculations AsyncRequest().find_server_with_ports Takes 6 secs to complete if scanning all PORTS
            
        AsyncRequest().auto_connect(success,failed=stayActive)
        
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

class Laner(MDApp):
    # android_app = autoclass('android.app.Application')pls checkout
    
    bottom_navigation_bar=ObjectProperty()
    btm_sheet = ObjectProperty()
    settings = Settings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
    
    def toogle_image_viewer(self,urls:list,start_from:str):
        def on_close_pic_viewer():
            self.bottom_navigation_bar.open()
            self.my_screen_manager.current_screen.enable_click()
        layout=PictureViewer(urls,start_from,on_close_pic_viewer)
        self.my_screen_manager.current_screen.disable_click()
        self.my_screen_manager.current_screen.add_widget(layout)
        self.bottom_navigation_bar.close()

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
        # self.toogle_image_viewer('http://192.168.88.4:8000//home/fabian/Pictures/inspo.png')
        return self.root_screen

    def on_resize(self, *args):
        btm_nav_btns=self.bottom_navigation_bar.children if isinstance(self.bottom_navigation_bar.children[0],TabButton) else []
        for btn in btm_nav_btns:
            btn.width=Window.width/3
        
        # print('What app see\'s as window height',Window.height)
        # print('BTM NAV Height',self.bottom_navigation_bar.height)

if __name__ == '__main__':
    Laner().run()

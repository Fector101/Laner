import time

from kivy.metrics import sp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivymd.uix.label import MDIcon, MDLabel



from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window

from kivy.clock import Clock

from components.popup import BookMarkedFolders


class TabButton(RectangularRippleBehavior,ButtonBehavior,MDBoxLayout):
    duration_long_touch=1
    text=StringProperty()
    icon=StringProperty()
    screen=StringProperty() # screen name
    screen_manager_current=StringProperty() # current screen name
    # color=ListProperty()
    tabs_buttons_list=[]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ripple
        self.double_tap_clock = None

        self.orientation='vertical'
        self.padding=[sp(0),sp(15),sp(0),sp(15)]
        self.line_color=(.2, .2, .2, 0)
        self._radius=1
        self.id=self.text
        self.spacing="10"
        self.size_hint=[None,1]
        self.width=Window.width/3
        self.start=0
        self.end=0
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
        self.no=1
    def on_release(self):
        self.designWidgets(self.screen)

        if self.start and self.end:
            dur = time.time() - self.start
            if dur < self.duration_long_touch:
                self.on_double_tap(self)
            self.start=0
            self.end=0
        else:
            self.end=time.time()
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

    def on_touch_down(self, touch):
        if not self.start:
            self.start=time.time()
        Clock.schedule_once(self.clear_double_tap_wait, self.duration_long_touch)
        super().on_touch_down(touch)

    def clear_double_tap_wait(self,dt):
        self.start = 0
        self.end = 0

    def on_double_tap(self,widget):
        pass

class BottomNavigationBar(MDNavigationDrawer):
    screen = StringProperty()
    # def __init__(self, screen_manager:WindowManager,**kwargs):
    def __init__(self, screen_manager,**kwargs):
        super(BottomNavigationBar, self).__init__(**kwargs)
        self.drawer_type='standard'
        self.set_state('open')
        self.radius=0
        self.bookmark_layout = BookMarkedFolders(0,0,0)

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
            if index == 0:
                self.btn.on_double_tap = self.show_favourite_folders
            self.add_widget(self.btn)

    def setScreen(self,btn:TabButton,screen_name):
        self.screen_manager.change_screen(screen_name)
        # btn.designWidgets(self.screen_manager.current)

    def close(self,widget=None):
        """My Method to hide bottom nav, mainly to show other screens

        Args:
            widget (object, optional): widget that calls method in callback. Defaults to None.
        """
        self.set_state('close')

    def open(self,widget=None):
        """My Method to show bottom nav

        Args:
            widget (_type_, optional): widget that calls method in callback. Defaults to None.
        """
        TabButton.designWidgets(TabButton,self.screen_manager.current)
        self.set_state('open')


    def show_favourite_folders(self,widget):
        container = self.parent.parent.parent  # <kivy.core.window.window_sdl2.WindowSDL object
        if self.bookmark_layout.state:
            self.bookmark_layout.close()
        else:
            print('closed',self.bookmark_layout.state)
            self.bookmark_layout.width=widget.width*2
            self.bookmark_layout.x=widget.x
            self.bookmark_layout.y=widget.height
                # =BookMarkedFolders(width=widget.width, x=widget.x, y=widget.height)
            container.add_widget(self.bookmark_layout)
        # self.parent.parent.parent.parent.add_widget(layout)

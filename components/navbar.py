from kivy.metrics import sp

from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivymd.uix.label import MDIcon, MDLabel



from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window

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
        self.padding=[sp(0),sp(15),sp(0),sp(15)]
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
    # def __init__(self, screen_manager:WindowManager,**kwargs):
    def __init__(self, screen_manager,**kwargs):
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
        TabButton.designWidgets(TabButton,self.screen_manager.current)
        self.set_state('open')

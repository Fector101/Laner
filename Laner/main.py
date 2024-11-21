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
from kivymd.uix.button import MDIconButton,MDButton
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

from kivy.uix.widget import Widget


#Window.size = (400, 1000)
THEME_COLOR_TUPLE=(.6, .9, .8, 1)
__DIR__ = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
MY_DATABASE_PATH = os.path.join(__DIR__, 'data', 'store.json') 

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


class MyCard(MDCard):
    '''Implements a material card.'''

class UploadScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='upload'
        label=MDLabel(text="Upload Screen",halign='center')
        self.add_widget(label)
        self.theme_bg_color="Custom"
        self.md_bg_color=self.theme_cls.backgroundColor

class Header(MDBoxLayout):
    text=StringProperty()
    text_halign=StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (.2, .2, .2, .5)
        self.header_label=MDLabel(
            color=self.theme_cls.backgroundColor,
            text=self.text,
            halign=self.text_halign,
            valign='center'
            )
        if self.text_halign == 'left':
            self.header_label.padding=[sp(50),0,0,0]
        self.add_widget(self.header_label)
    
class DownloadScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='download'
        
        # self.md_bg_color=[1,0,1,1]
        self.layout=MDStackLayout(md_bg_color=[.4,.4,.4,1],)
        
        # self.header=MDBoxLayout(size_hint=[1,.1])
        # self.header_label=Label(color=self.theme_cls.backgroundColor,text="~ Root",halign='center',valign='center')
        # self.header.add_widget(self.header_label)
        
        self.header=Header(text='~ Root',size_hint=[1,.1], text_halign='center')
        
        self.scroll_box=MDBoxLayout(size_hint=[1,.9],md_bg_color=[.6,.6,1,1])
        self.layout.add_widget(self.header)
        self.theme_bg_color="Custom"
        # self.md_bg_color=[1,1,1,1]#bg
        
        self.addData()        
        
        self.layout.add_widget(self.scroll_box)
        self.add_widget(self.layout)
    def addData(self):
        def myFormat(text:str):
            if len(text) > 20:
                return text[0:18] + '...'
            return text.capitalize()
        layout = GridLayout(cols=4, spacing=18, size_hint_y=None,padding=dp(10))
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        list_=['american_psycho_D12.mp3', 'anything_but_normal_juice_wrld.mp3', 'ass_like_that_eminem.mp3', 'AUD-20221201-WA0066.mp3', 'A_Boogie_Wit_Da_Hoodie_-_06_Demons_and_Angels_Ft_Juice_WRLD.mp3', 'central_cee_x_dave_uk_rap_lyrics_mp3_43300.mp3', 'coolio_gangsta_s_paradise_feat._l.v.mp3', 'd4vd_romantic_homicide_out_on_all_platforms.mp3', 'Dave - Streatham (Lyrics) (128 kbps).mp3', 'eminem-the_kids_explict_version.mp3', 'Eminem_-_Baby.mp3', 'Eminem_-_Bad_Guy.mp3', 'Eminem_-_Beautiful_Pain_feat_Sia_.mp3', 'Eminem_-_Berzerk.mp3', 'Eminem_-_Brainless.mp3', 'Eminem_-_Desperation_feat_Jamie_N_Commons_.mp3', 'Eminem_-_Evil_Twin.mp3', 'Eminem_-_feat_Skylar_Grey_.mp3', 'Eminem_-_Groundhog_Day.mp3', 'Eminem_-_Headlights_feat_Nate_Ruess_.mp3', 'Eminem_-_Legacy.mp3', 'Eminem_-_Love_Game_feat_Kendrick_Lamar_.mp3', 'Eminem_-_Parking_Lot_skit_.mp3', 'Eminem_-_Rap_God.mp3', 'Eminem_-_Rhyme_Or_Reason.mp3', 'Eminem_-_So_Far.mp3', 'Eminem_-_So_Much_Better.mp3', 'Eminem_-_Stronger_Than_I_Was.mp3', 'Eminem_-_Survival.mp3', 'Eminem_-_The_Monster_feat_Rihanna_.mp3', 'Eminem_-_Wicked_Ways.mp3', 'eminem_godzilla_lyrics_ft._juice_wrld.mp3', 'eminem_guilty_conscience_explicit_mp3_12807.mp3', 'eminem_my_dad_s_gone_crazy_official_instrumental.mp3', 'eminem_stan_uncensored_mp3_43810.mp3', 'frente_goodbye_goodguy.avi_mp3_1318.mp3', 'girls_D12.mp3', 'Juice WRLD - Burn (Official Music Video).mp3', 'juicewrld_sadv3_....doing_drugs_since_13.mp3', 'juice_wrld-what_else_lyrics_unrelased_mp3_55291.mp3', 'juice_wrld_already_dead_lyrics_mp3_41771.mp3', 'juice_wrld_awful_times_unreleased_lyrics_mp3_66378.mp3', 'juice_wrld_denial_mp3_49929.mp3', 'juice_wrld_fast_lyrics_mp3_39841.mp3', 'juice_wrld_in_my_head_official_music_video_mp3_66213.mp3', 'juice_wrld_lost_in_the_abyss_unreleased_mp3_67221.mp3', 'juice_wrld_my_x_was_poison_official_audio_mp3_67541.mp3', 'juice_wrld_no_good_unreleased.mp3', 'juice_wrld_reminds_me_of_the_summer_unreleased.mp3', 'juice_wrld_run.mp3', 'juice_wrld_split_my_brains_unreleased.mp3', 'K Like A Russian Juice WRLD UNRELESED.mp3', 'led_zeppelin_whole_lotta_love_official_audio_mp3_1674.mp3', 'lil_dicky_jail_full_song_mp3_47902.mp3', 'michael_jackson_billie_jean_mp3_69662.mp3', 'my_dad_s_gone_crazy.mp3', 'NF  HOPE Lyrics.mp3', 'NF - HOPE.mp3', 'Nirvana - Something In The Way (Audio).mp3', 'playboi_carti_immortal_prod._cash_carti_mp3_46670.mp3', 'psycho_mp3_41385.mp3', 'these_drugs_D12.mp3', 'the_beastie_boys_no_sleep_till_brooklyn_mp3_70041.mp3', 'the_rains_of_castamere_lannister_song_lyrics_hd_mp3_65667.mp3', 'tmnt_opening_theme_original_intro_mp3_52020.mp3', 'untitled_mp3_9846.mp3', 'van_halen_jump_mp3_45276.mp3', 'VID-20230324-WA0085_mp3.mp3', 'young_m.a_10_bands_x_brooklyn_poppin_freestyle_music_videos_mp3_64854.mp3', 'gtp.py', 'main.py', 'myfile.py', 'Screenshot-2.png']
        for each_file in list_[0:10]:# ("elevated", "filled", "outlined"):
            layout.add_widget(
                MyCard(
                    MDRelativeLayout(
                        FitImage(
                        source="assets/imgs/test.png",
                        size_hint=[1,.7],
                        pos_hint={"top":1},
                        radius=(dp(5),dp(5),0,0),
                    ),
                        MDButton(
                            MDButtonIcon(
                                icon="download",
                                pos_hint={'x':.19,'y':.17},
                                theme_icon_color="Custom",
                                icon_color=[1,1,1,1],
                            ),
                            theme_bg_color= "Custom",
                            theme_height= "Custom",
                            theme_width= "Custom",
                            radius='15sp',
                            size_hint= [None, None],
                            width= '30sp',
                            height='30sp',
                            md_bg_color=[.7,.6,.9,1],
                            pos_hint={"top": .979, "right": .97},
                        ),
                        MDLabel(
                            text=myFormat(each_file),
                            shorten_from='center',
                            font_size='11sp',
                            theme_font_size= "Custom",
                            text_color=[1,1,1,1],
                            height='40sp',
                            size_hint=[1,None]
                        ),
                        md_bg_color=[0,0,0,0]
                    ),
                    style='filled',
                    size_hint=(.5, None),
                    height='140sp',
                    radius=dp(5),theme_bg_color="Custom",
                    md_bg_color=[1,0,0,0],
                )
            )
        root = ScrollView(size_hint=(1, .9))
        root.add_widget(layout)
        self.layout.add_widget(root)
        
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
        my_screen_manager.current='settings'

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

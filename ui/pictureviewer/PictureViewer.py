import os

from kivy.lang import Builder
from kivy.clock import Clock

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.swiper.swiper import MDSwiperItem,MDSwiper

from utils.helper import getAppFolder
from .SafeAsyncImage import SafeAsyncImage


kv_file_path = os.path.join(getAppFolder(), "ui", "pictureviewer", "PictureViewer.kv")
with open(kv_file_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="PictureViewer.kv")
    
class MySwiper(MDSwiperItem):
    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SafeAsyncImage(source=source))
        
class PictureViewer(MDFloatLayout):
    def __init__(self, sources:list,start_from:str,close_btn_callback, **kwargs):
        super().__init__(**kwargs)
        self.swiper:MDSwiper=self.ids.swiper_id
        self.sources = sources
        self.close_btn_callback = close_btn_callback
        self.md_bg_color=[0,0,0,1]
        self.add_widget(MDIconButton(icon='close',pos_hint={'top': .99,'right': .99},on_release=self.close))
        self.swiper.transition_duration = 0
        current_img_index = self.index_of(sources,start_from)
        Clock.schedule_once(lambda dt:self.reset_transition_duration(),0.2)
        
        self.swiper.set_current(current_img_index)
        for each_source in sources:
                self.swiper.add_widget(MySwiper(source=each_source))
    def index_of(self,list_,item_):
        try:
            return list_.index(item_)
        except ValueError:
            print('Big Problem Url Still constitent101 ValueError')
            return 0
        
    def reset_transition_duration(self):
        self.swiper.transition_duration = 0.2
        
    def close(self,widget=None):
        self.parent.remove_widget(self)
        self.close_btn_callback()
import os
from kivy.lang import Builder
from kivy.metrics import sp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.swiper.swiper import MDSwiperItem
from kivymd.uix.fitimage.fitimage import FitImage
from workers.helper import getAppFolder
from widgets.img.SafeAsyncImage import SafeAsyncImage
from kivy.core.window import Window


kv_file_path = os.path.join(getAppFolder(), "widgets", "img", "PictureViewer.kv")
with open(kv_file_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="PictureViewer.kv")
    
class MySwiper(MDSwiperItem):
    
    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SafeAsyncImage(source=source))
    def on_touch_down(self,touch):
        return True    
class PictureViewer(MDFloatLayout):
    def __init__(self, sources,close_btn_callback, **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
        self.close_btn_callback = close_btn_callback
        self.md_bg_color=[0,0,0,1]
        self.add_widget(MDIconButton(icon='close',pos_hint={'top': .99,'right': .99},on_release=self.close))
        for each_source in sources:
            print(each_source,'|||')
            self.ids.swiper_id.add_widget(MySwiper(source=each_source))
    def close(self,widget=None):
        self.parent.remove_widget(self)
        self.close_btn_callback()
    
import os
from kivy.lang import Builder

from kivymd.uix.widget import MDWidget
from kivymd.uix.button import MDButton
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDIcon, MDLabel
from kivy.uix.boxlayout import BoxLayout
from utils.helper import getAppFolder
from kivymd.uix.swiper.swiper import MDSwiperItem
import ui.templates
filename="ConnectScreen.kv"
kv_file_path = os.path.join(getAppFolder(), "ui", "screens", filename)
with open(kv_file_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename=filename)

class FirstSlide(MDSwiperItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class SecondSlide(MDSwiperItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class LastSlide(MDSwiperItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
                
class ConnectScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'connect'
        # self.app = MDApp.get_running_app()
    def next_slide(self):
        swiper = self.ids.swiper
        current_index = swiper.get_current_index()
        if swiper.get_current_index() < len(swiper.children) - 1:
            swiper.set_current(current_index + 1)
        self.update_dots(current_index)

    def prev_slide(self):
        swiper = self.ids.swiper
        print(swiper)
        current_index = swiper.get_current_index()
        
        if current_index > 0:
            swiper.set_current(current_index - 1)
        self.update_dots(current_index)

    def update_dots(self, current_index):
        dots = self.ids.dots
        dots.clear_widgets()
        for i in range(3):  # Total slides
            color = (0, 0.4, 1, 1) if i == current_index else (0.8, 0.8, 0.8, 1)
            icon=MDIcon(icon="circle", text_color=color, font_size="10sp",theme_text_color="Custom")
            icon.theme_text_color="Custom"
            icon.theme_font_size="Custom"
            icon.font_size= "10sp"
            dots.add_widget(icon)
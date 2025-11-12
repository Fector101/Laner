from kivymd.app import MDApp
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
import ui.components.templates
filename="ConnectScreen.kv"
kv_file_path = os.path.join(getAppFolder(), "screens", filename)
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
        
        self.app = MDApp.get_running_app()
    def sendToSettingsScreen(self):
        self.manager.current = 'settings'
        self.app.bottom_navigation_bar.open()
        
    def next_slide(self):
        swiper = self.ids.swiper
        current_index = swiper.get_current_index()
        items=swiper.get_items()
        if swiper.get_current_index() < len(items) - 1:
            swiper.set_current(current_index + 1)
        self.updateBtns()

    def prev_slide(self):
        swiper = self.ids.swiper
        current_index = swiper.get_current_index()
        if current_index > 0:
            swiper.set_current(current_index - 1)
        self.updateBtns()
    def updateBtns(self):
        main_card = self.ids.main_card
        swiper = self.ids.swiper
        current_index = swiper.get_current_index()
        firstBtn = self.ids.first_btn
        def showSecondBtn():
            secondBtn.disabled=False
            secondBtn.opacity=1
            secondBtn.height='40sp'
            self.ids.btns_padding.height='10sp'
            
        secondBtn = self.ids.second_btn
        if (current_index == 0):
            firstBtn.text='Continue'
            
            secondBtn.disabled=True
            secondBtn.opacity=0
            self.ids.btns_padding.height='0sp'
            secondBtn.height='0sp'
            
        elif (current_index == 1):
            firstBtn.text='Next'
            showSecondBtn()
        elif (current_index == 2):
            firstBtn.text='Request Connection'
            showSecondBtn()
            
            
            
    def update_dots(self, current_index):
        dots = [*self.ids.dots.children]
        
        dots.reverse()
        print('-----start')
        print('color --> ','--', 'current_index -->',current_index)
        for i in range(3):  # Total slides
            color = (0, 0.4, 1, 1) if i == current_index else (0.8, 0.8, 0.8, 1)
            print(dots[i].text)
            dots[i].text_color=color

from kivymd.app import MDApp
from kivymd.uix.button import MDFabButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ( ListProperty, StringProperty)
from kivymd.uix.label import MDLabel
from kivy.metrics import sp
from kivymd.uix.menu import MDDropdownMenu

from utils import Settings
from utils.helper import getFileName


class HeaderBtn(MDFabButton):
    def __init__(self,font_size=26, **kwargs):
        super().__init__(**kwargs)
         # self.back_btn.radius=0
        self.theme_bg_color="Custom"
        self.theme_shadow_color="Custom"
        self.shadow_color=[0,0,0,0]
        self.md_bg_color=[0,0,0,0]

        self.font_size=sp(font_size)
        size__=45
        self.size=[sp(size__),sp(size__)]

class Header(MDBoxLayout):
    """_summary_

    Args:
        text (str): _description_
        text_halign (str): _description_
        title_color (str): _description_
    """
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    theme_text_color=StringProperty()
    def __init__(self,screen, **kwargs):
        super().__init__(**kwargs)
        self.app=MDApp.get_running_app()
        self.dropDown = None
        self.screen=screen
        self.md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1]
        self.size_hint=[1,None]
        self.height=sp(70)
        self.header_label=MDLabel(
            text_color=self.title_color,
            theme_text_color=self.theme_text_color,
            text='~ '+self.text if self.text == 'Home' else self.text,
            halign=self.text_halign,
            valign='center',
            shorten_from='left',
            shorten=True,
            # md_bg_color=[1,0,0,1]
            )
        if self.text_halign == 'left':
            self.header_label.padding=[sp(40),0,0,0]
        elif screen.__class__.__name__ == "DisplayFolderScreen":
            def fun():
                print(screen.manager.Android_back_click('_',27))
            grey_i= 0.44
            self.back_btn = HeaderBtn(icon="arrow-left", style= "standard", pos_hint={"center_y": .5},x=sp(10))
            self.back_btn.on_release=screen.set_last_folder_screen
            self.back_btn.color=[grey_i,grey_i,grey_i,1]
            self.add_widget(self.back_btn)
            self.padding=[sp(10),0,sp(10),0]

        self.add_widget(self.header_label)
        if self.text_halign != 'left':
            self.opts_btn = HeaderBtn(icon="dots-vertical", style= "standard", pos_hint={"center_y": .5},x=sp(10),on_release=lambda this:self.open_menu(this))
            self.saved_theme_color = self.opts_btn.color # IMPORTANT for back btn color reset
            self.add_widget(self.opts_btn)
    def changeTitle(self,text:str):
        self.header_label.text='~ '+ text if text == 'Home' else text
    def open_menu(self, item):
        icons=['refresh',
               'bookmark'
        # 'file','folder'
        ]
        titles=['Refresh','Add to Favorites','New file','New folder']
        functions = [self.refreshBtnClicked,self.bookmark_path,None,None]
        menu_items = [
            {
                "text": titles[i],
                'leading_icon': icons[i],
                'height': sp(45),
                
                "on_release": lambda real_index=i:functions[real_index](),
            } for i in range(len(icons))
        ]
        self.dropDown=MDDropdownMenu(caller=item, items=menu_items)
        self.dropDown.open()
    def refreshBtnClicked(self):
        self.screen.set_path_info(from_btn='frm_btn')
        self.dropDown.dismiss()
    def bookmark_path(self):
        self.app.my_screen_manager.current_screen.addToFavourite()


class HeaderBasic(MDBoxLayout):
    """Component For Page,Modal,... other component headers

    Args:
        text (str): header title
        text_halign (str): _description_
        title_color (str): _description_
    """
    text=StringProperty()
    text_halign=StringProperty()
    title_color=ListProperty([1,1,1,1])
    theme_text_color=StringProperty()
    def __init__(self,back_btn_func=None,btns=[],height=72, **kwargs):
        super().__init__(**kwargs)
        self.dropDown = None
        self.back_btn_func=back_btn_func
        self.md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1]
        self.size_hint=[1,None]
        self.height=sp(height)
        self.header_label=MDLabel(
            text_color=self.title_color,
            # theme_text_color=self.theme_text_color if self.theme_text_color else 'Primary',
            text=getFileName(self.text),
            halign=self.text_halign if self.text_halign else 'left',
            valign='center',
            shorten_from='right',
            shorten=True,
            # md_bg_color=[1,0,0,1]
            )

        if self.back_btn_func:
            grey_i = 0.44
            self.back_btn = HeaderBtn(
                icon="arrow-left",
                style= "standard",
                pos_hint={"center_y": .5},
                x=sp(10),
                on_release=self.close,
                color=[grey_i,grey_i,grey_i,1]
            )
            self.add_widget(self.back_btn)

        self.padding=[sp(10),0,sp(10),0]
        self.spacing=sp(10)
        self.add_widget(self.header_label)
        for each_btn in btns:
            button=HeaderBtn(
                icon=each_btn['icon'],
                style= "standard",
                pos_hint={"right":1,'center_y':.5},
                font_size=21,
                x=sp(10),
                on_release=each_btn['function']
            )
            self.add_widget(button)
        self.set_theme(self.theme_cls.theme_style)
    def change_title(self,text:str):
        self.header_label.text='~ '+ text if text == 'Home' else text
    def open_menu(self, item):
        icons=['refresh',
        # 'file','folder'
        ]
        titles=['Refresh','New file','New folder']
        functions = [self.refreshBtnClicked,None,None]
        menu_items = [
            {
                "text": titles[i],
                'leading_icon': icons[i],
                'height': sp(45),

                "on_release": lambda real_index=i:functions[real_index](),
            } for i in range(len(icons))
        ]
        self.dropDown=MDDropdownMenu(caller=item, items=menu_items)
        self.dropDown.open()
    def close(self,widget=None):
        self.back_btn_func()

    def set_theme(self, theme):
        """

        :param theme: Dark|Light|`custom` custom would be some dict key
        :return:
        """
        if theme == 'Light':
            self.header_label.theme_text_color='Custom'
            self.header_label.color  = [0,0,0,1]
            # self.header_label.text_color  = [0,0,0,1] same as .color one might get deprecated,this is for reference
        else:
            self.header_label.color  = [1,1,1,1]

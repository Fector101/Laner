import os
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from ..popup import PopupScreen

if platform == 'android':
    from kivymd.toast import toast

from components import HeaderBasic
from components.popup import Snackbar
from utils.helper import getFileName, urlSafePath, getAppFolder
from utils import AsyncRequest

class CustomTextInput(TextInput):
    def __init__(self, header_height,**kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.header_height=header_height
        self.background_normal = '' # border-color active focus
        # self.background_active = '' # border-color inactive focus
        self.background_color = (.1, .1, .1, 1) if self.app.theme_cls.theme_style == 'Dark' else [.9,.9,.9,1]
        self.foreground_color=[1,1,1,1] if self.app.theme_cls.theme_style == 'Dark' else (.1, .1, .1, 1)
        self.multiline = True
        self.size_hint_y = None
        self.padding=10
        self.height = Window.height - self.header_height
        Window.bind(size=self.on_resize_box)
        self.cursor_color = self.app.theme_cls.primaryColor
        # self._editable=False
        # self.disabled=False
        # Changes|Add more than border color change text color
        # with self.canvas.before:
            # self.border_color = Color(1, 0, .1, 1)  # changes textcolor for some reason
        #     self.border_rect = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        # self.bind(pos=self.update_border, size=self.update_border)

    def on_resize_box(self, window_object, window_size):
        self.height = window_size[1] - self.header_height

    # def update_border(self, *args):
    #     self.border_rect.rectangle = (self.x, self.y, self.width, self.height)

class FileReader(MDBoxLayout,PopupScreen):
    def __init__(self, file_path:str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.save_folder = os.path.join(getAppFolder(),'.filereader')
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)
        self.orientation='vertical'
        btns_data=[
            {'icon':'content-paste','function':self.paste_content},
            {'icon': 'content-copy', 'function': self.copy_all_content},
            # {'icon':'select-all','function':self.select_all_content},
            {'icon':'upload','function':self.upload_file}
        ]
        self.header = HeaderBasic(text=self.file_path,btns=btns_data,back_btn_func=self.close,height=80)
        self.text_box= CustomTextInput(text='Loading...',header_height=self.header.height)
        self.text_box.readonly = True
        self.add_widget(self.header)
        self.add_widget(self.text_box)
        self.__download_content()
        # self.dropDown = MDDropdownMenu()

    def __download_content(self):
        file_name = getFileName(self.file_path)
        save_path=os.path.join(self.save_folder, file_name)
        AsyncRequest(notifications=False).download_file(file_path=urlSafePath(self.file_path),save_path=save_path,success=self.read_content,failed=self.failed_to_download)

    def read_content(self, saved_path):
        with open(saved_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text_box.text = content

    @staticmethod
    def failed_to_download():
        failed_msg = 'Failed to Download File'
        if platform == 'android':
            toast(failed_msg)
        else:
            Snackbar(h1=failed_msg)

    def upload_file(self,widget=None):

        file_path =  getFileName(self.file_path)
        with open(file_path, 'w') as f:
            f.write(self.text_box.text)
        folder_path =  os.path.dirname(self.file_path)

        AsyncRequest(notifications=False).upload_file(file_path=file_path,save_path=folder_path,success=self.success_upload)

    def success_upload(self):
        self.toast_msg('Uploaded Successfully')

    @staticmethod
    def toast_msg(text,widget=None):
        if platform == 'android':
            toast(text)
        else:
            Snackbar(h1=text)

    def copy_all_content(self,widget=None):
        Clipboard.copy(self.text_box.text)
        self.toast_msg('File Copied')

    def paste_content(self,widget=None):
        copy_board_content = Clipboard.paste()
        self.text_box.text = copy_board_content
        self.text_box.cancel_selection()

    def reset_transition_duration(self):
        self.swiper.transition_duration = 0.2


    # def select_all_content(self,widget=None):
    #     self.text_box.select_all()

    # def save_file(self,widget=None):
    #     pass
    # def show_more_options(self,widget=None):
    #     icons = ['upload',
    #              'upload'
    #              ]
    #     titles = ['Upload', 'Download']
    #     functions = [self.save_file, self.download_file]
    #     menu_items = [
    #         {
    #             "text": titles[i],
    #             'leading_icon': icons[i],
    #             'height': sp(45),
    #
    #             "on_release": lambda real_index=i: functions[real_index](),
    #         } for i in range(len(icons))
    #     ]
    #     self.dropDown.caller=widget
    #     self.dropDown.items=menu_items
    #
    #     self.dropDown.open()
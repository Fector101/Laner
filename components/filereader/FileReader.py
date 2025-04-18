import os

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.utils import platform

if platform == 'android':
    from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.textinput import TextInput

from components import HeaderBasic
from components.popup import Snackbar
from utils.helper import makeDownloadFolder, getFileName, urlSafePath
from utils import AsyncRequest


class FileReader(MDBoxLayout):
    def __init__(self, file_path:str, close_btn_callback, **kwargs):
        super().__init__(**kwargs)
        self.file_path =file_path
        self.orientation='vertical'
        self.close_btn_callback = close_btn_callback
        self.md_bg_color = [0, 0, 0, 1]
        btns_data=[
            {'icon':'content-copy','function':self.copy_all_content},
            {'icon':'content-paste','function':self.paste_content},
            {'icon':'select-all','function':self.select_all_content},
            {'icon':'upload','function':self.upload_file}
        ]
        self.header = HeaderBasic(text=self.file_path,btns=btns_data,back_btn_func=self.close)
        self.text_box= TextInput(text='Hello world', multiline=True,size_hint_y=None,height=Window.height-self.header.height)
        Window.bind(size=self.on_resize_box)
        self.add_widget(self.header)
        self.add_widget(self.text_box)
        self.download_content()
        # self.dropDown = MDDropdownMenu()
    def download_content(self):
        file_name = getFileName(self.file_path)
        my_downloads_folder = makeDownloadFolder()
        save_path=urlSafePath(os.path.join(my_downloads_folder,file_name))
        print('file.path',self.file_path)
        AsyncRequest().download_file(file_path=self.file_path,save_path=save_path,success=self.read_content,failed=self.failed_to_download)

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

        AsyncRequest().upload_file(file_path=file_path,save_path=folder_path,success=self.success_upload)
    def success_upload(self):
        self.toast_msg('Uploaded Successfully')
    def on_resize_box(self,window_object,window_size):
        self.text_box.height=window_size[1]-self.header.height
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

    def select_all_content(self,widget=None):
        self.text_box.select_all()

    def reset_transition_duration(self):
        self.swiper.transition_duration = 0.2

    def close(self, widget=None):
        self.parent.remove_widget(self)
        self.close_btn_callback()

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
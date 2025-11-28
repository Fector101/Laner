"""Folder Screen Widget"""
import json
import os
import traceback
from urllib.parse import urlparse

import requests
from kivy.clock import Clock
from kivy.properties import StringProperty,BooleanProperty
from kivy.metrics import sp
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.uix.recyclegridlayout import RecycleGridLayout

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFabButton

from plyer import filechooser # pylint: disable=import-error

from ui.components.header import Header
from ui.components.popup import PopupDialog, Snackbar, PopupScreen
from ui.components.pictureviewer import SafeAsyncImage # it's been Used in .kv file
from utils.helper import getHiddenFilesDisplay_State, makeDownloadFolder, getAppFolder, getFormat, getFileName, \
    is_text_by_mime,get_destination_folder_for_file
from utils import AsyncRequest, Settings
from utils.constants import IMAGE_FORMATS


if platform == "android":
    from kivymd.toast import toast # pylint: disable=ungrouped-imports
    from jnius import autoclass, cast
else:
    def toast(text):
        print('fallback for android toast101 folder_screen file')
        Snackbar(text)
# Setup paths and load KV file.
my_downloads_folder = makeDownloadFolder()
kv_file_path = os.path.join(getAppFolder(), "ui","screens", "folderscreen.kv")
with open(kv_file_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="folderscreen.kv")


class RV(RecycleView):
    """Custom RecycleView to display folder contents."""


class DetailsLabel(Label):
    """Label with custom style for displaying folder details."""

class MyCard(RecycleDataViewBehavior,RectangularRippleBehavior,ButtonBehavior,MDRelativeLayout):
    path=StringProperty()
    icon=StringProperty()
    text=StringProperty()
    thumbnail_url=StringProperty()
    is_dir=BooleanProperty()
    validated_paths=[] # Suppose to save across instances
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_effect=False
        self.thumbnail_update_interval=None

    def isFile(self,path:str):
        sever_ip=MDApp.get_running_app().settings.get('server', 'ip')
        port=MDApp.get_running_app().settings.get('server', 'port')
        # print('What file ',path)
        try:
            response=requests.get(f"http://{sever_ip}:{port}/api/isfile",json={'path':path},timeout=2)
            # print(response.json())
            if response.status_code != 200:
                # Clock.schedule_once(lambda dt:Snackbar(h1="Dev pinging for thumb valid"))
                return False
            # print(response.json()['data'])
            return response.json()['data']

        except Exception as out_reach_to_server_error:
            # Clock.schedule_once(lambda dt:Snackbar(h1="Dev pinging for thumb valid"))
            print(f"isDir method: {out_reach_to_server_error}")
            return False

    def on_thumbnail_url(self, instance, value):
        """Called whenever thumbnail_url changes."""
        self.thumbnail_update_interval = Clock.schedule_interval(lambda dt: self.update_image(), 1)
        
    def on_parent(self, widget,parent):
        # Cleanup intervals when user leaves screen before thumbnail is created
        try:
            if not parent and self.thumbnail_update_interval:
                # print('canceling ',self.thumbnail_update_interval,'parent ',parent)
                self.thumbnail_update_interval.cancel()
                self.thumbnail_update_interval=None
        except Exception as e:
            print('interval cancel error ',e)
        
    def update_image(self):
        def without_url_format(url:str):
            return urlparse(url).path#os.path.join(*url.split('/')[4:]) (changing because it tempered with the path)
        
        # print('cheacking self.thumbnail_url for ---> ',self.thumbnail_url)
        # if self.thumbnail_url:
            # print(self.validated_paths,'||', without_url_format(self.thumbnail_url))
        if self.thumbnail_url and (self.thumbnail_url in self.validated_paths or self.isFile(without_url_format(self.thumbnail_url))):
            if self.thumbnail_url not in self.validated_paths:
                self.validated_paths.append(self.thumbnail_url)
            
            self.icon = self.thumbnail_url
            self.thumbnail_update_interval.cancel()
            self.thumbnail_update_interval=None
        elif not self.thumbnail_url:
            self.thumbnail_update_interval.cancel()

    def myFormat(self, text:str):
        if len(text) > 20:
            return text[0:18] + '...'
        return text



class MyRecycleGridLayout(RecycleGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adjust_columns()

    def adjust_columns(self):
        if Window.width > 500:
            self.cols = 4
        else:
            value = max(2, int(Window.width / 100))
            self.cols = 2 if value < 2 else value

    def on_size(self, *args):
        self.adjust_columns()


class DisplayFolderScreen(MDScreen):
    """Screen for displaying folder contents, handling navigation and file upload/download."""
    current_dir = StringProperty('.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen_history: list[str] = []
        # noinspection PyTypeChecker
        self.current_popup:PopupScreen|None=None # To track if i need to close popup when android back btn is pressed
        self.current_dir_info: list[dict]=[]
        self.could_not_open_path_msg = "Couldn't Open Folder Check Laner on PC"
        # self.md_bg_color=[1,1,0,1]

        # Set position.
        self.pos_hint={'top': 1}
        self.layout=MDBoxLayout(orientation='vertical')

        # Setup Header.
        self.header=Header(
            screen=self,
            text=self.current_dir,
            text_halign='center',
            theme_text_color='Primary',
            title_color=self.theme_cls.primaryColor,
            )
        self.layout.add_widget(self.header)

        # Setup content RecycleView.
        self.screen_scroll_box = RV()
        self.screen_scroll_box.data=self.current_dir_info
        self.layout.add_widget(self.screen_scroll_box)

        # Setup upload button.
        self.upload_btn=MDFabButton(
                icon="upload",
                style= "standard",
                pos_hint={"center_x": .82, "center_y": .25},
                on_release=lambda x: self.choose_file()
        )

        # Setup details box at bottom.
        self.details_box=MDRelativeLayout(
            height='35sp',
            adaptive_width=True,
            md_bg_color =[.15,.15,.15,1] if self.theme_cls.theme_style == "Dark" else  [0.92, 0.92, 0.92, 1],
            size_hint=[1,None]
            )
        self.details_label=DetailsLabel(text='0 files and 0 folders')
        self.details_box.add_widget(self.details_label)
        self.layout.add_widget(self.details_box)

        # Buffer for bottom navigation bar. (will change to padding later)
        self.layout.add_widget(MDBoxLayout(height='70sp',size_hint=[1,None]))
        self.add_widget(self.layout)
        self.add_widget(self.upload_btn)

    def disable_click(self,popup:PopupScreen=None):
        self.layout.disabled=True
        self.upload_btn.disabled=True
        self.current_popup = popup

    def enable_click(self):
        self.layout.disabled=False
        self.upload_btn.disabled=False

    def on_enter(self, *args):
        """When the screen is entered, update the folder listing."""
        # UrlRequest(url=f"http://{self.get_server_ip()}:{self.get_port_number()}/api/isdir",json={'path':path})
        def failed():
            Snackbar(h1=self.could_not_open_path_msg)
        instance=AsyncRequest()
        instance.is_folder(path=self.current_dir,success=self.set_path_info,failed=failed)

    def set_last_folder_screen(self) -> None:
        """Navigate to the last folder if history exists."""
        # print('self.screen_history ',self.screen_history)
        if self.screen_history:
            if self.current_popup:
                self.current_popup.close()
                self.current_popup=None
                last_dir = self.current_dir
            else:
                last_dir = self.screen_history.pop()
            self.set_folder(last_dir, add_to_history=False)

    def get_server_ip(self) -> str:
        """Return the server IP from settings."""
        return self.app.settings.get("server", "ip")

    def get_port_number(self) -> str:
        """Return the server port number from settings"""
        return self.app.settings.get("server", "port")

    def choose_file(self):
        """Open a file chooser dialog to select a file for upload."""
        print("Choosing file...")

        def parse_choice(file_paths:list):
            print(file_paths,'plyer chosen path')
            if file_paths:
                selected=file_paths if isinstance(file_paths,str) else file_paths[0]
                FileOperations(selected).upload_file(file_path=selected,current_dir=self.current_dir,callback=self.set_path_info)
        filechooser.open_file(on_selection=parse_choice)

    def set_path_info(self, from_btn: bool = False) -> None:
        """
        Asynchronously fetch folder information from the server and update the UI.
        :param from_btn: Whether this update was triggered from a button.
        """
        
        def success(folder_data):
            # Reset and populate current directory information.
            self.current_dir_info.clear()
            no_of_files=0
            no_of_folders=0

            
            show_hidden = getHiddenFilesDisplay_State()

            for item in folder_data:
                # Skip hidden files if not showing them
                if not show_hidden and item['text'].startswith('.'):
                    continue

                self.current_dir_info.append(item)
                if item['is_dir']:
                    no_of_folders+=1
                else:
                    no_of_files+=1

            # Update details label.
            file_label='file' if no_of_files == 1 else 'files'
            folder_label='folder' if no_of_folders == 1 else 'folders'
            self.details_label.text=f'{no_of_files} {file_label} and {no_of_folders} {folder_label}'

            # Update the recycle view data.
            self.screen_scroll_box.data=self.current_dir_info

            # Update back button color based on history.
            grey_i = 0.44
            if not self.screen_history:
                # no need to change btn color in App.toogle_theme() method since this method will get called everytime user enters screen
                self.header.back_btn.color = [grey_i, grey_i, grey_i, 1]
            else:
                self.header.back_btn.color=self.header.saved_theme_color

            if from_btn and platform == 'android':
                toast("Refresh Done") # pylint: disable=possibly-used-before-assignment
                    
        def failed():
            Snackbar(h1=self.could_not_open_path_msg)
            
    
        # requests.get(server,data='to be sent',auth=(username,password))
        instance=AsyncRequest()
        instance.get_path_data(path=self.current_dir,success=success,failed=failed)        
        
    def set_file(self, path: str) -> None:
        def success(file_url):
            
            file_name = os.path.basename(path.replace('\\', '/'))
            file_operations = FileOperations(path)
            self.manager.btm_sheet.show(file_name,items_object=[
            {'title':"Preview",'icon': "eye",'function': lambda x: file_operations.open_file_viewer(current_dir_info=self.current_dir_info)},
            {'title':"Download",'icon': "download",'function': lambda _: self.show_download_dialog(path)},
            {'title':"Open with",'icon': "apps",'function': file_operations.query_open_with},
            {'title':"Info",'icon': "information",'function': file_operations.share_file},
            {'title':"Share",'icon': "share",'function': file_operations.share_file}
        ])
        def fail():
            print('Not Folder')
        instance=AsyncRequest()
        instance.is_file(path=path,success=success,failed=fail)
        
    def set_folder(self, path: str, add_to_history: bool = True) -> None:
        """
        Change the current directory.
        :param path: The new path to set.
        :param add_to_history: Whether to add the current path to history.
        """
        def success():
            if add_to_history:
                self.screen_history.append(self.current_dir)
                print('last_dir ',self.screen_history)
            self.current_dir = path
            self.header.changeTitle(path)
            self.set_path_info()

        def failed():
            Snackbar(h1=self.could_not_open_path_msg)

        instance=AsyncRequest()
        instance.is_folder(path=self.current_dir,success=success,failed=failed)
        
    def show_download_dialog(self,path:str) -> None:
        """
        Show a dialog for download confirmation. If confirmed, start download.
        :param path: The path to download.
        """
        print('frm dialog')
        file_name = getFileName(path)
        target_folder = get_destination_folder_for_file(file_name)
        # put this line in FileOperations Class
        saving_path = os.path.join(my_downloads_folder,target_folder, file_name)
        def success(url):
            def failed_callback():
                pass

            def success_callBack():
                FileOperations(path).download_file(save_path=saving_path)

            txt='/'.join(my_downloads_folder.split('/')[-2:])
            PopupDialog(
                    failedCallBack=failed_callback,
                    successCallBack=success_callBack,
                    caption=f'Do you want to Download "{file_name}"',
                    sub_caption=f'It Will be saved in "{txt}"',
                    cancel_txt="Cancel",confirm_txt="Ok",
            )
        AsyncRequest().is_file(path,success=success)

    def addToFavourite(self):
        res=Settings().add_to_list_with_two_keys('bookmark_paths', 'paths', self.app.my_screen_manager.current_screen.current_dir)
        toast(res['msg'])
        if self.app.bottom_navigation_bar.bookmark_layout.state:
            self.app.bottom_navigation_bar.bookmark_layout.refresh()


class FileOperations:

    def __init__(self, file_path):
        self.path = file_path
        self.app = MDApp.get_running_app()

    def download_file(self,save_path) -> None:
        """
        Download a file from the given file_path and save it locally.
        Displays a notification when done.
        """
        needed_file = self.path.replace(' ', '%20').replace('\\', '/')
        
        def success(file_name):
            Snackbar(confirm_txt='Open',h1='Download Successfull')
        def failed():
            Snackbar(confirm_txt='Open',font_size=sp(15),h1="Download Failed try Checking Laner on PC")

        def startService():
            data = {'file_path': needed_file, 'save_path': save_path}
            STRING_DATA = json.dumps(data)
            # try:
            #     # from android import mActivity
            #     # print(mActivity)
            #     mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            #     context = mActivity.getApplicationContext()
            #     SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Download'
            #     service = autoclass(SERVICE_NAME)
            #     service.start(mActivity, 'round_music_note_white_24', 'title', 'content', STRING_DATA)
            # except Exception as e:
            #     print(f'Download service failed101 {e}')
            #     traceback.print_exc()
            try:
                Service(name='Download',args_str=STRING_DATA)
            except Exception as e1:
                print('Second try1:',e1)
                toast('Downloading From App State')
                AsyncRequest().download_file(needed_file, save_path, success, failed)
        if platform == "android":
            startService()
        else:
            instance=AsyncRequest()
            instance.download_file(needed_file,save_path,success,failed)

    def upload_file(self, file_path:str,current_dir:str,callback,file_data=None) -> None:
        """
        Upload a file to the server.
        :param file_path: Local file path.
        :param file_data: Optional file-like object.
        :param current_dir: path
        :param callback: callable
        """
        
        def success():
            Snackbar(h1="File Uploaded Successfully")
            # Refresh the folder.
            callback()
        def fail():
            Snackbar(h1="Failed to Upload File check Laner on PC")

        def startService():
            try:
                # mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                # context = mActivity.getApplicationContext()
                # SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Upload'
                # service = autoclass(SERVICE_NAME)
                data = {'file_path': file_path, 'save_path': current_dir}
                STRING_DATA = json.dumps(data)
                # service.start(mActivity, 'small_icon', 'title', 'content', STRING_DATA)
                Service(name='Upload',args_str=STRING_DATA)
            except Exception as e:
                print(f'Upload service failed101 {e}')
                toast('Uploading From App State')
                AsyncRequest().upload_file(file_path,current_dir,success,fail)

        if platform == "android":
            startService()
        else:
            AsyncRequest().upload_file(file_path,current_dir,success,fail)
    
    def open_file_viewer(self,current_dir_info):
        if is_text_by_mime(getFileName(self.path)):
            self.app.open_file_reader(file_path=self.path)
        else:
            self.__open_image_viewer(current_dir_info)

    def __open_image_viewer(self,current_dir_info):
        img_urls=[]
        if getFormat(self.path) not in IMAGE_FORMATS:
            return
        
        selected_file_index = None
        i=0
        for each in current_dir_info:
            if getFormat(each['path']) in IMAGE_FORMATS:
                img_urls.append(each['thumbnail_url'])  #thumbnail_url is the async img generated by server
                if each['path'] == self.path:
                    selected_file_index = i
                i+=1
                
        # print(img_urls,selected_file_index)
        self.app.toggle_image_viewer(img_urls,start_from=selected_file_index)

    def share_file(self,widget_at_called=None):
        print(self.path)

    def query_open_with(self,widget_at_called=None):
        print('query_open_with')



class Service:
    def __init__(self,name,args_str):
        from android import mActivity
        self.mActivity = mActivity
        self.args_str=args_str
        self.name=name
        self.start_service_if_not_running()
    def get_service_name(self):
        context = self.mActivity.getApplicationContext()
        return str(context.getPackageName()) + '.Service' + self.name

    def service_is_running(self):
        service_name = self.get_service_name()
        context = self.mActivity.getApplicationContext()
        manager = cast('android.app.ActivityManager',
                       self.mActivity.getSystemService(context.ACTIVITY_SERVICE))
        for service in manager.getRunningServices(100):
            if service.service.getClassName() == service_name:
                return True
        return False

    def start_service_if_not_running(self):
        if self.service_is_running():
            return
        service = autoclass(self.get_service_name())
        title=self.name +' Service'
        msg='Started'
        arg=self.args_str
        icon='round_music_note_white_24'
        service.start(self.mActivity, icon, title, msg, arg)

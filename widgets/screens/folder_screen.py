"""Folder Screen Wigdet"""

import asyncio
import os
import threading
import shutil

from kivy.clock import Clock
# pylint: disable=no-name-in-module
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.utils import platform
from kivy.network.urlrequest import UrlRequest

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFabButton

from android_notify import Notification, NotificationStyles
from plyer import filechooser # pylint: disable=import-error

from widgets.header import Header
from widgets.popup import PopupDialog, Snackbar
from workers.helper import getHiddenFilesDisplay_State, makeDownloadFolder, getAppFolder
from workers.requests.async_request import AsyncRequest

if platform == "android":
    from kivymd.toast import toast # pylint: disable=ungrouped-imports

# Setup paths and load KV file.
my_downloads_folder = makeDownloadFolder()
kv_file_path = os.path.join(getAppFolder(), "widgets", "screens", "folderscreen.kv")
with open(kv_file_path, encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="folderscreen.kv")


class RV(RecycleView):
    """Custom RecycleView to display folder contents."""


class DetailsLabel(Label):
    """Label with custom style for displaying folder details."""


class DisplayFolderScreen(MDScreen):
    """Screen for displaying folder contents, handling navigation and file upload/download."""
    current_dir = StringProperty('.')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.screen_history: list[str] = []
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


    def on_enter(self, *args):
        """When the screen is entered, update the folder listing."""
        # UrlRequest(url=f"http://{self.get_server_ip()}:{self.get_port_number()}/api/isdir",json={'path':path})
        instance=AsyncRequest()
        instance.is_folder(path=self.current_dir,success=self.set_path_info)

    def set_last_folder_screen(self) -> None:
        """Navigate to the last folder if history exists."""
        if self.screen_history:
            last_dir = self.screen_history.pop()
            self.set_folder(last_dir, add_to_history=False)

    def get_server_ip(self) -> str:
        """Return the server IP from settings."""
        return self.app.settings.get("server", "ip")

    def get_port_number(self) -> str:
        """Return the server port number from settings"""
        return self.app.settings.get("server", "port")

    def upload_file(self, file_path: str, file_data=None) -> None:
        """
        Upload a file to the server.
        :param file_path: Local file path.
        :param file_data: Optional file-like object.
        """
        
        def success():
            Snackbar(h1="File Uploaded Successfully")
            Notification(title='Completed upload',message=os.path.basename(file_path),channel_name="Upload Completed").send()
            # Refresh the folder.
            self.set_path_info()
            
        def fail():
            Snackbar(h1="Failed to Upload File check Laner on PC")
        
        AsyncRequest().upload_file(file_path,self.current_dir,success)
    def choose_file(self):
        """Open a file chooser dialog to select a file for upload."""
        print("Choosing file...")

        def parse_choice(file_paths:list):
            print(file_paths,'plyer choosen path')
            if file_paths:
                selected=file_paths if isinstance(file_paths,str) else file_paths[0]
                self.upload_file(selected)
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
        print('clicked!!')
        def success():
            self.manager.btm_sheet.enable_swiping=True
            self.manager.btm_sheet.set_state("toggle")
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
            
        instance=AsyncRequest()
        instance.is_folder(path=self.current_dir,success=success)
        
    def show_download_dialog(self,path:str) -> None:
        """
        Show a dialog for download confirmation. If confirmed, start download.
        :param path: The path to download.
        """
        print('frm dialog')
        def success():
            file_name = os.path.basename(path.replace('\\', '/'))
            def failed_callback():
                pass

            def success_callBack():
                needed_file = path.replace(' ', '%20').replace('\\', '/')
                saving_path = os.path.join(my_downloads_folder, file_name)
                self.download_file(file_path=needed_file,save_path=saving_path)
            PopupDialog(
                    failedCallBack=failed_callback,
                    successCallBack=success_callBack,
                    h1="Verify Download",
                    caption=f"{file_name} -- Will be saved in \"Laner\" Folder in your device \"Downloads\"",
                    cancel_txt="Cancel",confirm_txt="Ok",
            )
        AsyncRequest().is_file(path,success=success)
        
    def download_file(self,file_path: str, save_path: str) -> None:
        """
        Download a file from the given URL and save it locally.
        Displays a notification when done.
        """
        def success():
            file_name = os.path.basename(save_path)
            try:
                # If the file is an image, copy it to the app's assets and send a notification.
                IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif')
                if os.path.splitext(file_name)[1] in IMAGE_FORMATS:
                    shutil.copy(save_path, os.path.join(getAppFolder(), 'assets', 'imgs', file_name))
                    Notification(
                        title="Completed download",message=file_name,
                        style=NotificationStyles.LARGE_ICON,large_icon_path=save_path,
                        channel_name="Download Completed"
                    ).send()
                else:
                    Notification(title="Completed download",message=file_name,channel_name="Download Completed").send()
            except Exception as e:
                print(e,"Failed sending Notification")

            Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { file_name }'))
        def failed():
            Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1="Download Failed try Checking Laner on PC"))
            
        instance=AsyncRequest()
        instance.download_file(file_path,save_path,success,failed)

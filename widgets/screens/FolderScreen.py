"""Folder Screen Wigdet"""

import asyncio
import os
import threading
import shutil

import requests
from kivy.clock import Clock
# pylint: disable=no-name-in-module
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.utils import platform

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
        Clock.schedule_once(lambda dt: self.start_set_path_info_thread())

    def last_folder_screen(self) -> None:
        """Navigate to the last folder if history exists."""
        if self.screen_history:
            last_dir = self.screen_history.pop()
            self.set_path(last_dir, add_to_history=False)

    def get_server_ip(self) -> str:
        """Return the server IP from settings."""
        return self.app.settings.get("server", "ip")

    def get_port_number(self) -> str:
        """Return the server port number from settings."""
        return self.app.settings.get("server", "port")

    async def upload_file(self, file_path: str, file_data=None) -> None:
        """
        Upload a file to the server.
        :param file_path: Local file path.
        :param file_data: Optional file-like object.
        """
        try:
            url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/upload"
            files = {'file': file_data if file_data else open(file_path, 'rb')}
            response = requests.post(url, data={'save_path': self.current_dir},files=files ,timeout=0)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1='Connection Error - Check Laner on PC'))
                return
            Clock.schedule_once(lambda dt:Snackbar(h1="File Uploaded Successfully"))
            Notification(title='Completed upload',message=os.path.basename(file_path),channel_name="Upload Completed").send()
            # Refresh the folder.
            Clock.schedule_once(lambda dt: self.start_set_path_info_thread())
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1="Failed to Upload File check Laner on PC"))
            print(e,"Failed Upload")

    def start_upload_thread(self, file_path: str, file_data=None) -> None:
        """Start a thread to upload a file."""
        def query_upload():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.upload_file(file_path, file_data=file_data))
            loop.close()
        threading.Thread(target=query_upload, daemon=True).start()

    def choose_file(self):
        """Open a file chooser dialog to select a file for upload."""
        print("Choosing file...")

        def parse_choice(file_paths:list):
            print(file_paths,'plyer choosen path')
            if file_paths:
                selected=file_paths if isinstance(file_paths,str) else file_paths[0]
                self.start_upload_thread(selected)
        print(filechooser)
        filechooser.open_file(on_selection=parse_choice)

    def start_set_path_info_thread(self,from_btn: bool = False) -> None:
        """Start a thread to update the folder view."""
        threading.Thread(target=self.query_set_path_info_async,args=[from_btn]).start()

    def query_set_path_info_async(self, from_btn: bool) -> None:
        """Run the async update in its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_set_path_info(from_btn))
        loop.close()

    async def async_set_path_info(self, from_btn: bool) -> None:
        """
        Asynchronously fetch folder information from the server and update the UI.
        :param from_btn: Whether this update was triggered from a button.
        """
        try:
            url = f"http://{self.get_server_ip()}:{self.get_port_number()}/api/getpathinfo"
            json_ = {'path':self.current_dir}
            response = requests.get(url,json=json_,timeout=5)
            # requests.get(server,data='to be sent',auth=(username,password))
            print(f"Clicked {response}")
            if response.status_code != 200:
                Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
                return

            # Reset and populate current directory information.
            self.current_dir_info.clear()
            no_of_files=0
            no_of_folders=0

            file_data = response.json()['data']
            show_hidden = getHiddenFilesDisplay_State()

            for item in file_data:
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
                    
        except Exception as e:
            Clock.schedule_once(lambda dt:Snackbar(h1=self.could_not_open_path_msg))
            print("Failed opening Folder async ",e)

    def is_dir(self, path: str) -> bool | int:
        """
        Check if a given path is a directory on the server.
        Returns:
            True if directory,
            False if not a directory,
            404 if error.
        """
        try:
            response=requests.get(f"http://{self.get_server_ip()}:{self.get_port_number()}/api/isdir",json={'path':path},timeout=3)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
                return 404
            return response.json()['data']

        except Exception as e:
            Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
            print(f"is_dir method: {e}")
            return 404
    def set_path(self, path: str, add_to_history: bool = True) -> None:
        """
        Change the current directory.
        :param path: The new path to set.
        :param add_to_history: Whether to add the current path to history.
        """
        dir_status = self.is_dir(path)
        if dir_status != 404 and not dir_status:
            self.manager.btm_sheet.enable_swiping=True
            self.manager.btm_sheet.set_state("toggle")
            return

        if add_to_history:
            self.screen_history.append(self.current_dir)

        self.current_dir = path
        self.header.changeTitle(path)
        Clock.schedule_once(lambda dt: self.start_set_path_info_thread())
        
    def show_download_dialog(self,path:str) -> None:
        """
        Show a dialog for download confirmation. If confirmed, start download.
        :param path: The path to download.
        """
        # Check if path is a file.
        if self.is_dir(path) in [404, True]:
            return

        file_name = os.path.basename(path.replace('\\', '/'))
        def failed_callback():
            pass

        def success_callBack():
            needed_file = f"http://{self.get_server_ip()}:{self.get_port_number()}/{path}"
            url = needed_file.replace(' ', '%20').replace('\\', '/')
            saving_path = os.path.join(my_downloads_folder, file_name)
            threading.Thread(target=self._download_file_thread,args=(url, saving_path)).start()
            
        PopupDialog(
                failedCallBack=failed_callback,
                successCallBack=success_callBack,
                h1="Verify Download",
                caption=f"{file_name} -- Will be saved in \"Laner\" Folder in your device \"Downloads\"",
                cancel_txt="Cancel",confirm_txt="Ok",
        )

    def _download_file_thread(self,url, save_path):
        """Thread target for downloading a file asynchronously."""
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download_file(url, save_path))
        loop.close()


async def async_download_file(url: str, save_path: str) -> None:
    """
    Download a file from the given URL and save it locally.
    Displays a notification when done.
    """
    try:
        response = requests.get(url)
        file_name = os.path.basename(save_path)
        print("This is file name: ", file_name)
        print("This is save_path: ", save_path)
        with open(save_path, "wb") as file:
            file.write(response.content)
        try:
            # If the file is an image, copy it to the app's assets and send a notification.
            IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif')
            if os.path.splitext(file_name)[1] in IMAGE_FORMATS:
                shutil.copy(save_path, os.path.join(getAppFolder(), 'assets', 'imgs', file_name))
                Notification(title="Completed download",message=file_name,style=NotificationStyles.LARGE_ICON,large_icon_path=save_path,channel_name="Download Completed").send()
            else:
                Notification(title="Completed download",message=file_name,channel_name="Download Completed").send()
        except Exception as e:
            print(e,"Failed sending Notification")

        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1=f'Successfully Saved { file_name }'))
    except Exception as e:
        Clock.schedule_once(lambda dt: Snackbar(confirm_txt='Open',h1="Download Failed try Checking Laner on PC"))
        print("Failed Download: ",e)

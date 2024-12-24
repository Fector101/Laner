from kivy.uix.label import Label
from kivy.uix.relativelayout import MDRelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty
from kivy.clock import Clock

class CustomRefreshLayout(ScrollView):
    refreshing = BooleanProperty(False)
    drag_threshold = NumericProperty('50dp')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_touch_y = None
        self._refresh_triggered = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._start_touch_y = touch.y
            self._refresh_triggered = False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._start_touch_y and not self._refresh_triggered:
            if touch.y - self._start_touch_y > self.drag_threshold:
                self.refreshing = True
                self._refresh_triggered = True
                self.dispatch('on_refresh')
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._start_touch_y = None
        return super().on_touch_up(touch)

    def on_refresh(self):
        pass

    def refresh_done(self):
        self.refreshing = False

class DetailsLabel(Label):
    pass

class DisplayFolderScreen(MDScreen):
    current_dir = StringProperty('.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_received = False
        self.screen_history = []
        self.current_dir_info: list[dict] = []
        self.could_not_open_path_msg = "Couldn't Open Folder Check Laner on PC"
        self.layout = MDBoxLayout(orientation='vertical')
        self.header = Header(
            text=self.current_dir,
            size_hint=[1, .1],
            text_halign='center',
            theme_text_color='Primary',
            title_color=self.theme_cls.primaryColor,
        )
        self.layout.add_widget(self.header)

        self.screen_scroll_box = RV()
        self.screen_scroll_box.data = self.current_dir_info
        self.layout.add_widget(self.screen_scroll_box)

        THEME_COLOR = (.12, .65, .46, 1)
        self.upload_btn = MDFabButton(
            icon="upload",
            style="standard",
            pos_hint={"center_x": .82, "center_y": .19},
            on_release=lambda x: self.choose_file()
        )

        self.details_box = MDRelativeLayout(
            height='35sp',
            adaptive_width=True,
            md_bg_color=[.15, .15, .15, 1] if self.theme_cls.theme_style == "Dark" else [0.92, 0.92, 0.92, 1],
            size_hint=[1, None]
        )

        self.details_label = DetailsLabel(text='0 files and 0 folders')
        self.details_box.add_widget(self.details_label)

        self.refresh_layout = CustomRefreshLayout()
        self.refresh_layout.bind(on_refresh=self.refresh_callback)
        self.refresh_layout.add_widget(self.layout)

        self.add_widget(self.refresh_layout)
        self.add_widget(self.details_box)
        self.add_widget(self.upload_btn)

    def refresh_callback(self, *args):
        self.startSetPathInfo_Thread()
        Clock.schedule_once(lambda dt: self.refresh_layout.refresh_done(), 1)

    def uploadFile(self, file_path):
        try:
            response = requests.post(
                f"http://{getSERVER_IP()}:8000/api/upload",
                files={'file': open(file_path, 'rb')},
                data={'save_path': self.current_dir}
            )
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
                return
            Clock.schedule_once(lambda dt: Snackbar(h1="File Uploaded Successfully"))
            Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())
        except Exception as e:
            Clock.schedule_once(lambda dt: Snackbar(h1="Failed to Upload File check Laner on PC"))
            print(e, "Failed Upload")

    def startUpload_Thread(self, file_path):
        threading.Thread(target=self.uploadFile, args=(file_path,)).start()

    def choose_file(self):
        def test1(file_path):
            if file_path:
                self.startUpload_Thread(file_path if isinstance(file_path, str) else file_path[0])
        filechooser.open_file(on_selection=test1)

    def startSetPathInfo_Thread(self):
        threading.Thread(target=self.querySetPathInfoAsync).start()

    def querySetPathInfoAsync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncSetPathInfo())
        loop.close()

    async def asyncSetPathInfo(self):
        try:
            response = requests.get(f"http://{getSERVER_IP()}:8000/api/getpathinfo", json={'path': self.current_dir}, timeout=5)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
                return
            self.current_dir_info = []
            no_of_files = 0
            no_of_folders = 0

            def increase_no_of_files():
                nonlocal no_of_files
                no_of_files += 1

            def increase_no_of_folders():
                nonlocal no_of_folders
                no_of_folders += 1

            file_data = response.json()['data']
            show_hidden = getHiddenFilesDisplay_State()
            for item in file_data:
                if not show_hidden and item['text'].startswith('.'):
                    continue
                self.current_dir_info.append(item)
                if item['is_dir']:
                    increase_no_of_folders()
                else:
                    increase_no_of_files()

            parse_for_files = 'files' if no_of_files > 1 else 'file'
            parse_for_folders = 'folders' if no_of_folders > 1 else 'folder'
            self.details_label.text = f'{no_of_files} {parse_for_files} and {no_of_folders} {parse_for_folders}'
            self.screen_scroll_box.data = self.current_dir_info

        except Exception as e:
            Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
            print(e, "Failed opening Folder async")

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())

    def isDir(self, path: str):
        try:
            response = requests.get(f"http://{getSERVER_IP()}:8000/api/isdir", json={'path': path}, timeout=3)
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
                return False
            return response.json()['data']
        except Exception as e:
            Clock.schedule_once(lambda dt: Snackbar(h1=self.could_not_open_path_msg))
            print(f"isDir method: {e}")
            return 404

    def setPath(self, path, add_to_history=True):
        if self.isDir(path) != 404 and not self.isDir(path):
            self.manager.btm_sheet.set_state("toggle")
            return
        if add_to_history:
            self.screen_history.append(self.current_dir)
        self.current_dir = path
        self.header.changeTitle(path)
        Clock.schedule_once(lambda dt: self.startSetPathInfo_Thread())

    def showDownloadDialog(self, path: str):
        if self.isDir(path) == 404 or self.isDir(path):
            return
        file_name = os.path.basename(path.replace('\\', '/'))

        def failedCallBack(): ...

        def successCallBack():
            needed_file = f"http://{getSERVER_IP()}:8000/{path}"
            url = needed_file.replace(' ', '%20').replace('\\', '/')
            saving_path = os.path.join(my_downloads_folder, file_name)
            threading.Thread(target=self.b_c, args=(url, saving_path)).start()

        PopupDialog(
            failedCallBack=failedCallBack, successCallBack=successCallBack,
            h1="Verify Download",
            caption=f"{file_name} -- Will be saved in \"Laner\" Folder in your device \"Downloads\"",
            cancel_txt="Cancel", confirm_txt="Ok",
        )

    def b_c(self, url, save_path):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download_file(url, save_path))
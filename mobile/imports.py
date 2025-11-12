import os, traceback
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition
from kivy.metrics import dp,sp
from kivy.core.window import Window
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivy.lang import Builder
from kivy.utils import platform # OS

from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.label import MDIcon
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import  MDNavigationLayout

from ui.components import PictureViewer,FileReader

from utils.helper import (
    THEME_COLOR_TUPLE, makeDownloadFolder,
    setHiddenFilesDisplay, getAndroidBounds,
    getViewPortSize,
    getStatusBarHeight,requestMultiplePermissions
    )

# Start logging
try:
    from utils.log_redirect import start_logging
    start_logging()
except Exception as e:
    from utils.helper import log_error_to_file
    error_traceback = traceback.format_exc()
    log_error_to_file(error_traceback)

from utils import Settings
from ui.screens import DisplayFolderScreen, ConnectScreen,SettingsScreen
from ui.components.templates import MyBtmSheet
from ui.components import BottomNavigationBar,TabButton

import logging

logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("kivy").setLevel(logging.WARNING)  # If using Kivy

# try:
#     from  utils import test
#     print('Ran All Android Notify Tests')
# except Exception as e:
#     print('Andorid notify Tests failed -----',e)

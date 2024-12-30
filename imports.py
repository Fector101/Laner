from kivy.uix.filechooser import FileChooserListView
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivy.core.window import Window
from kivymd.uix.label import MDIcon, MDLabel
from kivy.metrics import dp,sp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition
from kivy.uix.label import Label
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.image import AsyncImage,Image
from kivy.uix.spinner import Spinner
from kivy.utils import platform # OS
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import (MDNavigationDrawer,
                MDNavigationLayout)
from kivymd.uix.divider import MDDivider
import requests
import os, sys, json
from plyer import filechooser

from widgets.popup import Snackbar
from widgets.templates import CustomDropDown, DetailsLabel, DisplayFolderScreen, Header, MDTextButton
from workers.helper import THEME_COLOR_TUPLE, get_full_class_name, makeDownloadFolder, setHiddenFilesDisplay,getAndroidBounds,getViewPortSize,getStatusBarHeight
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

from workers.sword import NetworkManager, Settings

# Window.size = getAndroidSize()
# try:
#     FLAG_FULLSCREEN=0x00000400
#     FLAG_FORCE_NOT_FULLSCREEN=0x00000800
#     from jnius import autoclass
#     PythonActivity = autoclass('org.kivy.android.PythonActivity')
#     activity = PythonActivity.mActivity
#     activity.getWindow().clearFlags(FLAG_FORCE_NOT_FULLSCREEN)
#     activity.getWindow().addFlags(FLAG_FULLSCREEN)
# except Exception as e:
#     print('Fullscreen Error: -----| ',e)
    # print('Fullscreen Error: -----| KIVY_DPI=320 KIVY_METRICS_DENSITY=0.90 python3 main.py --size 360x760',e)
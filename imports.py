from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition,NoTransition
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp,sp
from kivy.core.window import Window
from kivy.properties import (ObjectProperty, BooleanProperty, ListProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.image import AsyncImage,Image
from kivy.uix.spinner import Spinner
from kivy.utils import platform # OS

from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import (MDNavigationDrawer, MDNavigationLayout)
from kivymd.uix.divider import MDDivider
# from kivymd.color_definitions import colors

import os, sys, json, requests, asyncio, threading
from plyer import filechooser

from widgets.popup import Snackbar
from widgets.templates import CustomDropDown, DetailsLabel, DisplayFolderScreen, Header, MDTextButton,MyBtmSheet
from workers.helper import THEME_COLOR_TUPLE, get_full_class_name, makeDownloadFolder, setHiddenFilesDisplay,getAndroidBounds,getViewPortSize,getStatusBarHeight,requestMultiplePermissions

from workers.sword import NetworkManager, Settings



if platform == 'android':
    from kivymd.toast import toast
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    Intent = autoclass('android.content.Intent')
    
from android_notify import send_notification
from android_notify import NotificationStyles

try:
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')

    activity = PythonActivity.mActivity
    intent = Intent()
    intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
    intent.setData(Uri.parse(f"package:{activity.getPackageName()}"))
    activity.startActivity(intent)
except Exception as e:
    print("Error battery stuff: ",e)
try:
    activity = PythonActivity.mActivity
    context = cast('android.content.Context', activity)
    # Start Foreground Service
    service_intent = Intent(context, PythonActivity)
    service_intent.setAction("START_FOREGROUND_SERVICE")
    context.startForegroundService(service_intent)
except Exception as e:
    print("Error Start foreground service: ",e)
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
from workers.helper import (
    THEME_COLOR_TUPLE, get_full_class_name,
    makeDownloadFolder, setHiddenFilesDisplay,
    getAndroidBounds,getViewPortSize,
    getStatusBarHeight,requestMultiplePermissions,
    getAppFolder
    )

from workers.sword import NetworkManager, Settings



if platform == 'android':
    from kivymd.toast import toast
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    Intent = autoclass('android.content.Intent')
    PowerManager = autoclass('android.os.PowerManager')    
    Context = autoclass('android.content.Context')
    
    context = cast('android.content.Context', mActivity)
    
    
from android_notify import send_notification
from android_notify import NotificationStyles

def requestBatteryOptimization():
    try:
        settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        intent = Intent()
        intent.setAction(settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
        intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}"))
        mActivity.startActivity(intent)
    except Exception as e:
        print("Error battery stuff: ",e)


def is_battery_optimization_enabled():
    """Check if battery optimization is enabled for the app."""
    power_manager = context.getSystemService(Context.POWER_SERVICE)
    package_name = mActivity.getPackageName()
    return not power_manager.isIgnoringBatteryOptimizations(package_name)

def start_service():
    if is_battery_optimization_enabled():
        print("Battery optimization is enabled. Requesting exclusion...")
        requestBatteryOptimization()
    else:
        print("Battery optimization is already disabled.")


try:
    start_service()
except Exception as e:
    print("Error1 battery stuff: ",e)

try:
    # Start Foreground Service
    # service_intent = Intent(context, PythonActivity)
    # service_intent.setAction("START_FOREGROUND_SERVICE")
    # context.startForegroundService(service_intent)
    # print("Foreground Service Started!")
    
    # # Define the path to the service script
    # service_path = os.path.join(getAppFolder(),'services', "service.py")
    # print(f"Service Path: {service_path}")
    # # Start the service via an intent
    # intent = Intent(context, PythonActivity)
    # intent.setAction("START_FOREGROUND_SERVICE")
    # intent.putExtra("service_script", service_path)    
    # context.startForegroundService(intent)
    # print("Foreground Service Started!")

    # intent = Intent(context, PythonActivity)
    # intent.setClassName(context.getPackageName(), f"{context.getPackageName()}.ServiceSendnoti")
    # context.startService(intent)

    context =  mActivity.getApplicationContext()
    SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Sendnoti'
    service = autoclass(SERVICE_NAME)
    service_intent = Intent(mActivity, service) # Create intent
    context.startForegroundService(service_intent)  # Start the service
    # print("Foreground Service Started! -----------------")
    
except Exception as e:
    print("Error Start foreground service: ",e)

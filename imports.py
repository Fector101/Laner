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
from kivy.uix.image import AsyncImage,Image
from kivy.uix.spinner import Spinner
from kivy.utils import platform # OS

from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivy.uix.scrollview import ScrollView
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import (MDNavigationDrawer, MDNavigationLayout)
from kivymd.uix.divider import MDDivider


import os, sys, json, requests, asyncio, threading

from utils.helper import (
    THEME_COLOR_TUPLE, get_full_class_name,
    makeDownloadFolder, setHiddenFilesDisplay,
    getAndroidBounds,getViewPortSize,
    getStatusBarHeight,requestMultiplePermissions,
    getAppFolder
    )

from utils import Settings,NetworkManager,AsyncRequest


from components.popup import Snackbar
from components.templates import CustomDropDown, MDTextButton,MyBtmSheet
from screens import DisplayFolderScreen, ConnectScreen
from components.header import Header
from components.pictureviewer import PictureViewer


if platform == 'android':
    from kivymd.toast import toast
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    Intent = autoclass('android.content.Intent')
    PowerManager = autoclass('android.os.PowerManager')    
    Context = autoclass('android.content.Context')
    
    context = cast('android.content.Context', mActivity)
    
    
from android_notify import send_notification,Notification,NotificationStyles

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

def useUnlimitedBatteryPower():
    if is_battery_optimization_enabled():
        print("Battery optimization is enabled. Requesting exclusion...")
        requestBatteryOptimization()
    else:
        print("Battery optimization is already disabled.")



     
def startService():
    try:
        mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
        context =  mActivity.getApplicationContext()
        SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Upload'
        service = autoclass(SERVICE_NAME)
        service.start(mActivity,'small_icon','title','content','FECTOR101')
        print('returned service')
    except Exception as e:
        print(f'Foreground service failed {e}')

if platform == 'android':
    startService()






# Get required Android classes
# Context = autoclass('android.content.Context')
# Notification = autoclass('android.app.Notification')
# NotificationManager = autoclass('android.app.NotificationManager')
# PendingIntent = autoclass('android.app.PendingIntent')
# Intent = autoclass('android.content.Intent')
# PythonService = autoclass('org.kivy.android.PythonService')



# Get the application context
# service = PythonService.mService
# context = service.getApplicationContext()

# # Get the NotificationManager
# notif_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)

# # Create a notification channel (for Android 8+)
# if notif_manager.getNotificationChannel("my_channel") is None:
#     NotificationChannel = autoclass('android.app.NotificationChannel')
#     channel = NotificationChannel("my_channel", "Persistent Notification", NotificationManager.IMPORTANCE_LOW)
#     notif_manager.createNotificationChannel(channel)

# # Create an Intent to open the app when tapped
# intent = Intent(context, PythonService)
# pending_intent = PendingIntent.getActivity(context, 0, intent, 0)

# # Build the persistent notification
# builder = autoclass('androidx.core.app.NotificationCompat').Builder(context, "my_channel")
# builder.setContentTitle("My App Running")
# builder.setContentText("This notification stays permanently.")
# builder.setSmallIcon(17301659)  # Default Android icon (change if needed)
# builder.setContentIntent(pending_intent)
# builder.setOngoing(True)  # Make it persistent

# # Start foreground service with the notification
# service.startForeground(1, builder.build())
import logging

logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("kivy").setLevel(logging.WARNING)  # If using Kivy

# try:
#     from  utils import test
#     print('Ran All Android Notify Tests')
# except Exception as e:
#     print('Andorid notify Tests failed -----',e)
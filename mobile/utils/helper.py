import os, platform, traceback, mimetypes
import urllib.parse
from pathlib import Path

from utils.constants import OTHER_TXT_FORMATS
from android_notify.config import from_service_file,get_python_activity_context
try:
	from jnius import autoclass, cast
except Exception as e:
	print("Error importing pyjnius:", e)


import sys
print('sys.path 101 --->',[ path for path in sys.path],os.path.exists("/system/build.prop"),platform.release(),platform.system())
# DEVICE_TYPE = 'desktop'
# if sys.platform.startswith('linux'):
if not from_service_file():
	from kivy.clock import Clock
	from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
	from kivy.utils import platform as kivyplatform
	if kivyplatform == 'android':
		from kivymd.toast import toast
		from android import api_version  # type: ignore

else:
	DEVICE_TYPE = 'mobile'
	kivyplatform = 'android'
	print('no clocks')
	class Clock:
		def schedule_once(self):
			print('A fall back function async_requests',self)

	def toast(txt):
		print('service dummy toast txt:',txt)
	api_version = 101
 
THEME_COLOR_TUPLE=(.6, .9, .8, 1)

def get_ui_context(): # explicitly getting app context not service
	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	return PythonActivity.mActivity

def getFormat(file_path):
	return os.path.splitext(file_path)[1]

def getAppFolder():
	"""
		Returns the correct application folder path, whether running on native Windows,
		Wine, or directly in Linux.
	"""
	if hasattr(sys, "_MEIPASS"): # PyInstaller creates a temp folder (_MEIPASS)
		path__ = os.path.abspath(sys._MEIPASS)
	elif DEVICE_TYPE == 'mobile':
		from android.storage import app_storage_path # type: ignore
		path__= os.path.join(app_storage_path(),'app')
	else: # Running from source code
		function_folder_formatted_to_get_app_folder = os.path.join(os.path.dirname(__file__),'..')
		path__=os.path.abspath(function_folder_formatted_to_get_app_folder)

	if is_wine(): # Uses path from _MEIPASS or source code
		# Normalize path for Wine compatibility
		path__ = wine_path_to_unix(path__) 
	return path__

def is_wine():
	"""
	Detect if the application is running under Wine.
	"""
	# Check environment variables set by Wine
	if "WINELOADER" in os.environ:
		return True

	# Check platform.system for specific hints
	if platform.system().lower() == "windows":
	# If running in "Windows" mode but in a Linux environment, it's likely Wine
		return "XDG_SESSION_TYPE" in os.environ or "HOME" in os.environ

	return False

def wine_path_to_unix(win_path):
	"""
	Converts a Windows-style path to a Unix-style path in Wine.
	"""
	# Wine maps Windows paths under ~/.wine/drive_c
	unix_path = win_path.replace("\\", "/")
	if unix_path.startswith("C:/"):
		wine_home_folder=os.environ['WINEHOMEDIR'].replace("\\","/").split(':/') if 'WINEHOMEDIR' in os.environ else ''
		wine_home_folder=wine_home_folder[1] if len(wine_home_folder) > 0 else ''
		if wine_home_folder:
			unix_path = unix_path.replace("C:/",'/'+wine_home_folder+"/.wine/drive_c/")
		else:
			wine_home_folder=os.environ['WINECONFIGDIR'].replace("\\","/").split(':/') if 'WINECONFIGDIR' in os.environ else ''
			wine_home_folder=wine_home_folder[1] if len(wine_home_folder) > 0 else ''
			unix_path = unix_path.replace("C:/", '/'+wine_home_folder+"/drive_c/")

	return os.path.normpath(unix_path)
  
  

def makeFolder(my_folder: str):
    """Safely creates a folder if it doesn't exist."""
    # Normalize path for Wine (Windows-on-Linux)
    if is_wine():
        my_folder = my_folder.replace('\\', '/')

   
    if not os.path.exists(my_folder):
        try:
            os.makedirs(my_folder)
        except Exception as e:
            print(f"Error creating folder '{my_folder}': {e}")
    return my_folder


def makeDownloadFolder():
    """Creates (if needed) and returns the Laner download folder path."""
    from kivy.utils import platform

    if platform == 'android':
        from android.storage import primary_external_storage_path  # type: ignore
        folder_path = os.path.join(primary_external_storage_path(), 'Download', 'Laner')
    else:
        folder_path = os.path.join(os.getcwd(), 'Download', 'Laner')

    makeFolder(folder_path)
    return folder_path


SHOW_HIDDEN_FILES=False
def setHiddenFilesDisplay(state):
	global SHOW_HIDDEN_FILES
	SHOW_HIDDEN_FILES=state
def getHiddenFilesDisplay_State():
	return SHOW_HIDDEN_FILES


def get_full_class_name(obj):
	module = obj.__class__.__module__
	if module is None or module == str.__class__.__module__:
		return obj.__class__.__name__
	return module + '.' + obj.__class__.__name__


def getAndroidBounds():
	# Access the Android Context and WindowManager
	WindowManager = autoclass('android.view.WindowManager')
	DisplayMetrics = autoclass('android.util.DisplayMetrics')

	# Get system service for WindowManager
	Context = get_ui_context()
	window_manager = Context.getSystemService(Context.WINDOW_SERVICE)


	# Create a DisplayMetrics instance and populate it
	metrics = DisplayMetrics()

	Rect=autoclass('android.graphics.Rect')
	rect=Rect()
	Context.window.getDecorView().getWindowVisibleDisplayFrame(rect)
	print("height ",rect.height(), " width ",rect.width())
	print("Width",rect.right-rect.left, "Height",rect.bottom-rect.top)

	window_manager.getDefaultDisplay().getMetrics(metrics)

	# Print DisplayMetrics values
	print("Android 15 broken sizing: ")
	print(f"Width: {metrics.widthPixels}px")
	print(f"Height: {metrics.heightPixels}px")
	print(f"Density: {metrics.density}")
	print(f"DPI: {metrics.densityDpi}")

def getViewPortSize():
	try:
		# Create a DisplayMetrics instance and populate it
		Context = get_ui_context()
		Rect=autoclass('android.graphics.Rect')
		rect=Rect()
		Context.window.getDecorView().getWindowVisibleDisplayFrame(rect)
		print("My ViewPort: ","height ",rect.height(), " width ",rect.width())
		return [rect.width(),rect.height()]
	except Exception as e:
		from kivy.core.window import Window
		return [Window.width,Window.height]

def getStatusBarHeight():
	# Create a DisplayMetrics instance and populate it
	try:
		Context = get_ui_context()
		resources = Context.getResources()
		resources_id=resources.getIdentifier("status_bar_height", "dimen", "android")
		height=resources.getDimensionPixelSize(resources_id)
		print("Status Bar Height: ",height)  #68
		return height
	except Exception as e:
		print("Status Bar Height Error")
		return 0
  
def requestMultiplePermissions():


	from android import mActivity # type: ignore
	
	# try:
	# 	context =  mActivity.getApplicationContext()
	# 	SERVICE_NAME = str(context.getPackageName()) + '.Service' + 'Sendnoti'
	# 	service = autoclass(SERVICE_NAME)
	# 	service.start(mActivity,'')
	# 	print('returned service')
	# except Exception as e:
	# 	print(f'Foreground service failed {e}')

	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	from android.permissions import request_permissions, Permission,check_permission # type: ignore
	from android.storage import app_storage_path, primary_external_storage_path # type: ignore


	print('Asking permission...')
	def check_permissions(permissions):
		for permission in permissions:
			if check_permission(permission) != True:
				return False
		return True


	def request_all_permission():
		def on_permissions_result(permissions, grants):
			print('What grants is ---->',grants)
			if Permission.POST_NOTIFICATIONS in permissions and not grants[permissions.index(Permission.POST_NOTIFICATIONS)]:
				print("Notification permission denied")
			storage_permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
			request_permissions(storage_permissions, on_storage_permissions_result)

		def on_storage_permissions_result(permissions, grants):
			# Storage permissions granted, request all files access for Android 11+
			if api_version >= 30:
					Environment = autoclass('android.os.Environment')
					Intent = autoclass('android.content.Intent')
					Settings = autoclass('android.provider.Settings')

					if not Environment.isExternalStorageManager():
						mActivity = PythonActivity.mActivity
						Uri = autoclass('android.net.Uri')
						try:
							intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
							print(f"package:{mActivity.getPackageName()}") # package:org.laner.lan_ft
							intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}"))
							Clock.schedule_once(lambda dt: mActivity.startActivity(intent), 2)
						except Exception as e:
							Clock.schedule_once(lambda dt: toast("Failed to request storage permissions"), 2)

			else:
				print("Storage permissions not called Android less 11 | Feature not available 101")

		# Request notification permission first
		request_permissions([Permission.POST_NOTIFICATIONS], on_permissions_result)

	try:
		request_all_permission()
	except Exception as e:
		print(f"Failed to request permissions: {e}") 

def urlSafePath(path:str):
	path_without_drive=os.path.splitdrive(path)[1]
	# Normalizing Windows Path Forward Slashes for Url '\\' ---> '/'
	normalized_path= path_without_drive.replace('\\','/')
	# For URL encoding
	url_safe_path=urllib.parse.quote(normalized_path)
	return url_safe_path

import sys

def get_android_device_name():
	from getpass import getuser
	# print('frm python+++++++++++++++++++++++++++++ ', getuser())
	device_name = ''
	try:
		PythonActivity = autoclass('org.kivy.android.PythonActivity')
		context = PythonActivity.mActivity.getApplicationContext()
		try:
			SettingsGlobal = autoclass('android.provider.Settings$Global')
			device_name = SettingsGlobal.getString(context.getContentResolver(), "device_name")
		except Exception as e:
			print('add this to exception catch ',e)

		if not device_name:
			try:
				SettingsSecure = autoclass('android.provider.Settings$Secure')
				device_name = SettingsSecure.getString(context.getContentResolver(), "bluetooth_name")
				if not device_name:
					device_name = SettingsSecure.getString(context.getContentResolver(), 'device_name')
			except Exception as e:
				print('add this to exception catch ', e)
		if not device_name:
			try:
				SettingsSystem = autoclass('android.provider.Settings$System')
				device_name = SettingsSystem.getString(context.getContentResolver(), 'device_name')
			except Exception as e:
				print('add this to exception catch ', e)
		if not device_name:
			try:
				Build = autoclass('android.os.Build')
				device_name = Build.MANUFACTURER +' - ' + Build.MODEL
			except Exception as e:
				print('add this to exception catch ', e)
	except Exception as e:
		traceback.print_exc()
	return device_name.strip() if device_name else "Unknown Device"

def get_device_name():
	if kivyplatform == 'android':
		try:
			return get_android_device_name()
		except Exception as e:
			print(f"Android device, but error retrieving name: {e}")
			return ''
	else:
		# For non-Android platforms, a basic fallback using the platform module.
		try:
			import platform
			uname = platform.uname()
			# The 'node' part can sometimes be used to get a hostname or device name.
			return f"{uname.system} {uname.node}"
		except Exception as e:
			return f"Unknown Device: {e}"

def getFileName(file_path:str):
	return os.path.basename(file_path.replace('\\', '/'))


def is_text_by_mime(filepath:str):
	mime, _ = mimetypes.guess_type(filepath)
	is_text_type = (mime is not None and mime.startswith('text')) or Path(filepath).suffix in OTHER_TXT_FORMATS
	print(mime,is_text_type)
	return is_text_type

def get_destination_folder_for_file(filename):
    """
    Determines the appropriate subfolder for the file based on its extension.
    Automatically creates the folder if it doesn't exist.
    Returns the absolute folder path.
    """
    categories = {
        "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".csv"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv"],
        "Music": [".mp3", ".wav", ".aac", ".flac"],
        "Archives": [".zip", ".rar", ".tar", ".gz"],
        "Scripts": [".py", ".js", ".html", ".css", ".sh", ".bat"],
        "Subtitles": [".srt", ".vtt", ".sub", ".ass"]
    }

    ext = os.path.splitext(filename)[1].lower()
    base_path = makeDownloadFolder()

    # Find the matching category folder
    for folder, extensions in categories.items():
        if ext in extensions:
            folder_path = os.path.join(base_path, folder)
            makeFolder(folder_path)
            return folder_path

    # Default if no match
    folder_path = os.path.join(base_path, "Others")
    makeFolder(folder_path)
    return folder_path

def test101():
    from jnius import autoclass, cast
    from android import python_act

    # Get current activity and context
    mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
    context = mActivity.getApplicationContext()

    # Autoclass necessary Java classes
    RingtoneManager = autoclass("android.media.RingtoneManager")
    Uri = autoclass("android.net.Uri")
    AudioAttributesBuilder = autoclass("android.media.AudioAttributes$Builder")
    AudioAttributes = autoclass("android.media.AudioAttributes")
    AndroidString = autoclass("java.lang.String")
    NotificationManager = autoclass("android.app.NotificationManager")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    NotificationCompat = autoclass("androidx.core.app.NotificationCompat")
    NotificationCompatBuilder = autoclass("androidx.core.app.NotificationCompat$Builder")
    NotificationManagerCompat = autoclass("androidx.core.app.NotificationManagerCompat")
    NotificationCompatActionBuilder = autoclass("androidx.core.app.NotificationCompat$Action$Builder")

    func_from = getattr(NotificationManagerCompat, "from")
    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")

    # Autoclass your own Java class
    action1 = autoclass("org.laner.lan_ft.Action1")

    # Variables
    channel_id = "channel_id"
    notification_id = 101
    id = 1  # action id

    # === CREATE CHANNEL ===
    sound = cast(Uri, RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
    att = AudioAttributesBuilder()
    att.setUsage(AudioAttributes.USAGE_NOTIFICATION)
    att.setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
    att = cast(AudioAttributes, att.build())

    name = cast("java.lang.CharSequence", AndroidString("Channel Name"))
    description = AndroidString("Channel Description")
    importance = NotificationManager.IMPORTANCE_HIGH

    channel = NotificationChannel(channel_id, name, importance)
    channel.setDescription(description)
    channel.enableLights(True)
    channel.enableVibration(True)
    channel.setSound(sound, att)

    notificationManager = context.getSystemService(NotificationManager)
    notificationManager.createNotificationChannel(channel)

    # === CREATE NOTIFICATION ===
    builder = NotificationCompatBuilder(context, channel_id)
    builder.setSmallIcon(context.getApplicationInfo().icon)
    builder.setContentTitle(cast("java.lang.CharSequence", AndroidString("Notification Title")))
    builder.setContentText(cast("java.lang.CharSequence", AndroidString("Notification Text")))
    builder.setSound(sound)
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)
    builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)

    # Intent for action button
    intent = Intent(context, action1)
    pendingintent = PendingIntent.getBroadcast(
        context, id, intent, PendingIntent.FLAG_CANCEL_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    title = cast("java.lang.CharSequence", AndroidString("Action 1"))
		
    action1_button = NotificationCompatActionBuilder(
        id, title, pendingintent
    ).build()
    builder.addAction(action1_button)

    # Send the notification
    compatmanager = func_from(context)
    compatmanager.notify(notification_id, builder.build())
    

import datetime

def log_error_to_file(error_traceback, file_name='error_log'):
    # Create "errors" folder inside the download folder
    error_folder_path = os.path.join(makeDownloadFolder(), "logs")
    makeFolder(error_folder_path)

    # Append .txt to the file name
    log_file_path = os.path.join(error_folder_path, f"{file_name}.txt")

    # Ensure the file exists before appending
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', encoding='utf-8') as file:
            file.write('')  # Just to create the file

    # Create timestamp
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    # Append error with timestamp and separator
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{timestamp}\n")
        file.write(f"{error_traceback.strip()}\n")
        file.write('-' * 60 + '\n')




class Service:
    def __init__(self,name,args_str=""):
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
        thing=self.mActivity.getSystemService(context.ACTIVITY_SERVICE)
        
        manager = cast('android.app.ActivityManager',thing)
        for service in manager.getRunningServices(100):
        	found_service=service.service.getClassName()
        	print("found_service: ",found_service)
        	if found_service== service_name:
        		return True
        return False
            #
            
        

    def start_service_if_not_running(self):
    	state=self.service_is_running()
    	print(state,"||",self.name,"||", self.get_service_name())
    	if state:
    		return
    	service = autoclass(self.get_service_name())
    	title=self.name +' Service'
    	msg='Started'
    	arg=self.args_str
    	icon='round_music_note_white_24'
    	service.start(self.mActivity, icon, title, msg, arg)
    	

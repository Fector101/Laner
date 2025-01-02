import os,sys,platform
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC
from kivy.clock import Clock

THEME_COLOR_TUPLE=(.6, .9, .8, 1)

        
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
  
  
def makeFolder(my_folder:str):
	if is_wine():
		my_folder = my_folder.replace('\\','/')

	if not os.path.exists(my_folder):
		os.makedirs(my_folder)

def makeDownloadFolder():
	"""Makes downlod folder and returns path
	"""
	from kivy.utils import platform

	folder_path = os.getcwd()
	if platform == 'android':
		from android.storage import app_storage_path, primary_external_storage_path # type: ignore
		folder_path=os.path.join(primary_external_storage_path(),'Download','Laner')
		makeFolder(folder_path)
  	
	return folder_path

def truncateStr(text:str,limit=20):
	if len(text) > limit:
		return text[0:limit] + '...'
	return text


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



if DEVICE_TYPE == 'mobile':
	from kivymd.toast import toast
	from jnius import autoclass
	from android import api_version  # type: ignore
	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	Context = PythonActivity.mActivity

def getAndroidBounds():

    # Access the Android Context and WindowManager
    WindowManager = autoclass('android.view.WindowManager')
    DisplayMetrics = autoclass('android.util.DisplayMetrics')

    # Get system service for WindowManager
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
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
						intent = Intent()
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
    
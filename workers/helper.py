import subprocess
import os
import json
import socket
import sys
import hashlib
from kivymd.material_resources import DEVICE_TYPE # if mobile or PC

THEME_COLOR_TUPLE=(.6, .9, .8, 1)
def getSystemName():
  # Windows
	USER_HOME_PATH=os.getenv('HOMEPATH')
	os_name='Win'
	if(USER_HOME_PATH == None):
		USER_HOME_PATH=os.getenv('HOME')
	os_name='Linux'
	return os_name

def getHomePath():
  # Windows
	USER_HOME_PATH=os.getenv('HOMEPATH')  # Can also be editable to downloads path or something else
	if(USER_HOME_PATH == None):
		USER_HOME_PATH=os.getenv('HOME')
	return USER_HOME_PATH

def findClosestParent(path:str):...

def scanFolder(inputted_folder_path:str):
	folder_paths=[]
	file_paths=[]
	try:
		all_paths = os.listdir(inputted_folder_path)
		for folder_or_file_name in all_paths:
			found_path=os.path.join(inputted_folder_path, folder_or_file_name)
			if os.path.isdir(found_path):
				folder_paths.append(found_path)
			else:
				file_paths.append(found_path)
	except Exception as e:
		print(e) # Display Error in Log Screen "As is" i mean in the same format it's printed out in console (Will Probably only get error if Access Denied or Folder Moved)
	return {'folders':folder_paths,'files':file_paths}
  
import subprocess
import platform

        
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
        
def sortedDir(dir_info:list):
    """Sorts objects Alphabetically and Pushes files with dot to the back.

    Args:
        dir_info (list): a list of objects with a key 'text'

    Returns:
        list: returns a list sort objects according to 'text' attr
    """
    dir_info=sorted(dir_info,key=lambda path: path['text'])
    
    # Push files with dot at front to the back
    items_with_dot=[]
    items_without_dot=[]
    for each in dir_info:
        if each['text'][0] == '.':
            items_with_dot.append(each)
        else:
            items_without_dot.append(each)
    
    return [*items_without_dot, *items_with_dot]

def removeFileExtension(file_path:str):
	return os.path.splitext(os.path.basename(file_path))[0]

def getFileExtension(file_path:str):
	return os.path.splitext(os.path.basename(file_path))[1]
def gen_unique_filname(file_path:str):
	hash_obj=hashlib.sha256(file_path.encode('utf-8'))
	unique_name=hash_obj.hexdigest()
	return unique_name

def removeFirstDot(path:str):
	if path[0] == '.':
		return path[1:]
	else:
		return path


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
  
def getAndroidBounds():
    from jnius import autoclass
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = PythonActivity.mActivity

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
try:
	from jnius import autoclass
	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	Context = PythonActivity.mActivity
except:...

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
  

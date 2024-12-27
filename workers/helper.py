import subprocess
import os
import json
import sys
import hashlib
import urllib.parse
def getSystemName():
  # Windows
  USER_HOME_PATH=os.getenv('HOMEPATH')
  os_name='Win'
  if USER_HOME_PATH is None:
    USER_HOME_PATH=os.getenv('HOME')
    os_name='Linux'
  return os_name

def getHomePath():
  """
  Get user's home directory path across different platforms.
  Returns: str - Path to user's home directory
  """
  # Try platform-independent method first
  home = os.path.expanduser('~')
  if home and os.path.exists(home):
    return home
    
  # Fallback to environment variables
  for env_var in ['HOME', 'USERPROFILE', 'HOMEPATH']:
    path = os.getenv(env_var)
    if path and os.path.exists(path):
      return path
      
  # Last resort - current directory
  return os.getcwd()

def getdesktopFolder():
  """
  Get path to user's desktop folder across different platforms.
  Returns: str - Path to desktop directory
  """
  # First try standard desktop location
  home = getHomePath()
  desktop = os.path.join(home, 'Desktop')
  if os.path.exists(desktop):
    return desktop
    
  # Try Windows-specific location
  desktop = os.path.join(home, 'OneDrive', 'Desktop')
  if os.path.exists(desktop):
    return desktop
  
  # Fallback to home directory
  return home
  

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
  
def writeIntoDB(data):
  with open("public/data.json") as file:
      Dict_Structure = json.load(file)  
  Dict_Structure['pc_storage']=data

  dictionary_words = json.dumps(Dict_Structure, indent=4)
  with open("public/data.json", mode="w") as new_word:
      new_word.write(dictionary_words)
import subprocess
import platform
import re
import shutil
import socket



import socket
import subprocess
import platform

def getAppFolder():
    """
    Returns the correct application folder path, whether running on native Windows,
    Wine, or directly in Linux.
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller creates a temp folder (_MEIPASS)
        path__ = os.path.abspath(sys._MEIPASS)
    else:
        # Running from source code
        path__ = os.path.abspath(os.path.dirname(__file__))

    # Normalize path for Wine compatibility
    if is_wine():
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
  # from kivy.utils import platform
  folder_path = os.path.dirname(os.path.abspath(__file__))
  # Check if on android
  
  try:
    from android.storage import app_storage_path, primary_external_storage_path # type: ignore
    folder_path=os.path.join(primary_external_storage_path(),'Download','Laner')
    makeFolder(folder_path)
  except:...
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


def getUserPCName():
    """
    Get the current user's PC name.
    Returns: str - PC name
    """
    pc_name=None
    try:
        # Try socket hostname first
        pc_name = socket.gethostname()
        
        # Clean and validate hostname
        if pc_name and isinstance(pc_name, str):
            # Remove special characters and extra spaces
            cleaned_name = ' '.join(pc_name.split())
            # Limit length and capitalize
            pc_name= cleaned_name[:30]
        # Fallback methods if socket failed
        
    except Exception as e:
        print(f"Error in getUserPCName: {e}")
    def fallbackPCName():
      """Helper function to get PC name using environment variables"""
      pc_name= 'Unknown-PC'
      try:
          # Try different environment variables
        for env_var in ['COMPUTERNAME', 'HOSTNAME', 'HOST', 'USER']:
            name = os.environ.get(env_var)
            if name:
                pc_name= name.strip()[:30]
                break
        
      except Exception as e:
        print(f"Error in fallbackPCName: {e}")
        pc_name= 'Unknown-PC'
      return pc_name
          
    return pc_name or fallbackPCName()
  
def urlSafePath(path:str):
  path_without_drive=os.path.splitdrive(path)[1]
  # Normalizing Windows Path Forward Slashes for Url '\\' ---> '/'
  normalized_path= path_without_drive.replace('\\','/')
  # For URL encoding
  url_safe_path=urllib.parse.quote(normalized_path)
  return url_safe_path

def inHomePath(request_path,folder):
    print(os.path.join(getHomePath(),folder), "==", os.path.join(request_path,folder))
    return os.path.join(getHomePath(),folder) == os.path.join(request_path,folder)

import urllib.parse
import hashlib,os,sys,platform,socket
from os.path import join as _joinPath

def gen_unique_filname(file_path:str):
  hash_obj=hashlib.sha256(file_path.encode('utf-8'))
  unique_name=hash_obj.hexdigest()
  return unique_name


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
        
        venv_root = os.path.abspath(os.path.join(sys.executable, '..', '..','..'))   # Go up one level from sys.executable
        path__=venv_root
        # function_folder_formatted_to_get_app_folder = os.path.join(os.path.dirname(__file__),'..')
        # path__=os.path.abspath(function_folder_formatted_to_get_app_folder)

    # Normalize path for Wine compatibility
    if is_wine():
        path__ = wine_path_to_unix(path__)

    return path__


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



def removeFirstDot(path:str):
  if path[0] == '.':
    return path[1:]
  else:
    return path
  

def getFileExtension(file_path:str):
  return os.path.splitext(os.path.basename(file_path))[1]
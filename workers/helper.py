import subprocess
import os
import json
import socket
import sys
import hashlib
# import subprocess

# /home/fabian/Documents/my projects code/mobile dev/Laner/venv/lib64/python3.12/site-packages/kivymd/uix/menu/menu.py
# Run this from VSCode content menu (Run Python) --> /home/fabian/Documents/my projects code/mobile dev/Laner/venv/lib64/python3.12/site-packages/kivymd/icon_definitions.py
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
  
def writeIntoDB(data):
  with open("public/data.json") as file:
      Dict_Structure = json.load(file)  
  Dict_Structure['pc_storage']=data

  dictionary_words = json.dumps(Dict_Structure, indent=4)
  with open("public/data.json", mode="w") as new_word:
      new_word.write(dictionary_words)

import re
def getSystem_IpAdd():
  try:
    # hostname=socket.gethostname()
    # ip_addr = ip_addr if ip_addr not in ['127.0.0.1','127.0.1.1'] else None
    ip_addr=subprocess.run(['ifconfig'],capture_output=True,text=True)
    output=ip_addr.stdout
    ip_pattern = re.compile(r'inet\s([\d.]+)')
    ip_addresses=ip_pattern.findall(output)
    ip_addresses=[ip for ip in ip_addresses if ip != '127.0.0.1']
    return ip_addresses[0]
  except Exception as e:
    print(f"Getting IP Error: {e}")
    return None

  
def getAppFolder():
  path__=None
  if hasattr(sys, "_MEIPASS"):
    path__= sys._MEIPASS
  else:
    path__= os.path.dirname(__file__)
  return os.path.splitdrive(path__)[1]
    
def makeFolder(my_folder):
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

SERVER_IP=getSystem_IpAdd()
def setSERVER_IP(value):
  global SERVER_IP
  SERVER_IP=value
def getSERVER_IP():
  return SERVER_IP
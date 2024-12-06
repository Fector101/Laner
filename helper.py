import os
import json
import socket

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
def getSystem_IpAdd():
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8",80))
            return s.getsockname()[0]
    except Exception as e:
        return f"Getting IP Error: {e}"

  

def makeFolder(my_folder):
    if not os.path.exists(my_folder):
        os.makedirs(my_folder)
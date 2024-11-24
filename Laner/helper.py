import os
import json
from http.server import SimpleHTTPRequestHandler,HTTPServer
import socketserver
import os
import threading

# /home/fabian/Documents/my projects code/mobile dev/Laner/venv/lib64/python3.12/site-packages/kivymd/uix/menu/menu.py
# Run this from VSCode content menu (Run Python) --> /home/fabian/Documents/my projects code/mobile dev/Laner/venv/lib64/python3.12/site-packages/kivymd/icon_definitions.py
def getSystemName():
  # Windows
  USER_HOME_PATH=os.getenv('HOMEPATH')  # Can also be editable to downloads path or something else
  os_name='Win'
  if(USER_HOME_PATH == None):
    USER_HOME_PATH=os.getenv('HOME')
    os_name='Linux'
  return os_name

def findClosestParent(path:str):
  if getSystemName() == 'Win':
    number_of_slash=path.count(r'\\')
  else:# anroid slash same as linux
    number_of_slash=path.count('/')
  
  print(number_of_slash,path)

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
  
os.chdir("public")  # <dev> Ensure this folder exists in your app's root
def writeIntoDB(data):
  with open("public/data.json") as file:
      Dict_Structure = json.load(file)  
  Dict_Structure['pc_storage']=data

  dictionary_words = json.dumps(Dict_Structure, indent=4)
  with open("public/data.json", mode="w") as new_word:
      new_word.write(dictionary_words)
# cellphone-link

# with open("/home/fabian/Desktop/safe/worked/Application 2/json_maker/DataBase.json") as file:
#   Dict_Structure = json.load(file)
#   print(Dict_Structure.keys())
  

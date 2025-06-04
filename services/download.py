import random,time, traceback, json
print('from download------------------****---------------------',random.randint(100,200),'---------------------****---------------------')
from os import environ
from jnius import autoclass

ARG =  environ.get('PYTHON_SERVICE_ARGUMENT','')
print('python Entered Download Service, Args', ARG)
DATA=json.loads(ARG)
print('python "I Download" service parsed args ---> ', DATA)

from android_notify import Notification
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService
# service.setAutoRestartService(True)

def done():
    print('done downloading')

try:
    n = Notification(
        id=101,
        title='Laner download service',
        message='Please keep this running to avoid download interruption')
    n.addButton('Cancel all',done)
    n.send(persistent=True, close_on_click=False)
except Exception as e:
    print("service python error:",e)
    traceback.print_exc()

try:
    from utils.requests.async_request import AsyncRequest
    instance = AsyncRequest(notification_id=random.randint(1000,2000))
    instance.download_file(file_path=DATA['file_path'], save_path=DATA['save_path'], success=done)
    # instance.download_file(file_path='/home/fabian/Downloads/Untitled.png',save_path='/storage/emulated/0/Download/Laner/biz.png',success=done)
    while instance.running:
        print('this is my download service and its running')
        time.sleep(3)
    print('ending my download service')
    service.stopSelf()

except Exception as e:
    print("service python error1:", e)
    traceback.print_exc()

import traceback,json,random
print('from upload----------------****---------------------',random.randint(100,200),'---------------------****---------------------')
from os import environ
from jnius import autoclass

ARG =  environ.get('PYTHON_SERVICE_ARGUMENT','')
print('python Entered Upload Service, Args', ARG)
DATA=json.loads(ARG)
print('python "I Upload" service parsed args ---> ', DATA)

from android_notify import Notification
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService
# service.setAutoRestartService(True) find a way to continue download to use this
# And check if service is actually running after setAutoRestartService(True) because all logs actually stop

def done():
    print('done downloading')

try:
    n=Notification(
        id=100,
        title='Laner upload service',
        message='Please keep this running to avoid upload interruption')
    n.addButton('Cancel all',done)
    n.send(persistent=True,close_on_click=False)
except Exception as e:
    print("upload service python (initial notification error):",e)
    traceback.print_exc()

try:
    from utils.requests.async_request import AsyncRequest
    instance = AsyncRequest(notification_id=random.randint(1000,2000))
    instance.upload_file(file_path=DATA['file_path'], save_path=DATA['save_path'], success=done)
    print('python upload instance -101',instance)
    while instance.running:
        print('this is my upload service and its running')
        time.sleep(3)
    print('ending my upload service')
    service.stopSelf()

except Exception as e:
    print("upload service python - (upload error):", e)
    traceback.print_exc()

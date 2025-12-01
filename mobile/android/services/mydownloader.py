try:
    from utils.log_redirect import start_logging
    start_logging()
    print("Service Logging started. All console output will also be saved.")
except Exception as e:
    print("File Logger Failed",e)
    
print("Entered Service File...")
import time
from android_notify import Notification
from android_notify.config import get_python_activity_context
from jnius import autoclass


BuildVersion = autoclass("android.os.Build$VERSION")
ServiceInfo = autoclass("android.content.pm.ServiceInfo")
service = get_python_activity_context()
foreground_type= ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC if BuildVersion.SDK_INT >= 30 else 0

fmt = lambda s: f"{int(s//3600)}h {int((s%3600)//60)}m {int(s%60)}s"

n=Notification(title="Foreground Service Active", message="This service is running in the foreground")
builder=n.fill_args() # not using .send() allowing.startForeground() to send initial notification 
service.startForeground(n.id, builder.build(), foreground_type)


print("Foreground Service is alive. Entering main loop...")
n1 = Notification(title="Running for 0h 0m 0s")
n1.send()

start = time.time()
END_TIME = 6 * 3600
while True:
    elapsed = time.time() - start
    if elapsed >= END_TIME:
        n.updateTitle(f"Total runtime {fmt(elapsed)}")
        break
    n1.updateTitle(f"Running for {fmt(elapsed)}")
    time.sleep(2)

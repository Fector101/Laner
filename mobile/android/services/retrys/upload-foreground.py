import os
import threading
import time
import json
import traceback
from os import environ
from pythonosc import dispatcher, osc_server, udp_client
from android_notify import Notification
from jnius import autoclass
from utils.requests.async_request import AsyncRequest
from utils.log_redirect import start_logging

# Start logging
try:
    start_logging()
    print("📜 Upload Service Logging started.")
except Exception:
    pass

PythonService = autoclass('org.kivy.android.PythonService')
BuildVersion = autoclass("android.os.Build$VERSION")
ServiceInfo = autoclass("android.content.pm.ServiceInfo")
service = PythonService.mService

try:
    SERVICE_PORT = int(environ.get('PYTHON_SERVICE_ARGUMENT', '5010'))
except:
    SERVICE_PORT = 5010

APP_PORT = 5007
APP_IP = "127.0.0.1"

# ---- Notification ----
n = Notification(
    id=201,
    title='Upload Service',
    message='This allows background uploads. No activity for 30min will auto-stop.'
)
builder = n.start_building()

foreground_type = (
    ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
    if BuildVersion.SDK_INT >= 30 else 0
)

service.startForeground(n.id, builder.build(), foreground_type)
client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)


# ============================================================
#                     UPLOAD TASK
# ============================================================

class UploadTask:
    def __init__(self, task_id, file_path, upload_url):
        self.task_id = task_id
        self.file_path = file_path
        self.upload_url = upload_url
        self.instance = None
        self.status = "pending"
        self.last_activity = time.time()

    def start(self):
        try:
            self.status = "uploading"
            self.last_activity = time.time()

            self.instance = AsyncRequest(notification_id=self.task_id)

            self.instance.upload_file(
                file_path=self.file_path,
                upload_url=self.upload_url,
                success=self._on_success,
                #failure=self._on_error,
                #progress=self._on_progress
            )

        except Exception as e:
            self._on_error(str(e))

    def _on_progress(self, progress, sent, total):
        self.last_activity = time.time()
        client.send_message("/upload/progress",
                            [self.task_id, progress, sent, total])

    def _on_success(self):
        self.status = "completed"
        self.last_activity = time.time()
        client.send_message("/upload/complete",
                            [self.task_id, self.file_path])

    def _on_error(self, msg):
        self.status = "error"
        self.last_activity = time.time()
        client.send_message("/upload/error", [self.task_id, msg])

    def pause(self):
        if self.instance and hasattr(self.instance, 'pause'):
            self.instance.pause()
            self.status = "paused"
            self.last_activity = time.time()
            client.send_message("/upload/paused", [self.task_id])

    def resume(self):
        if self.instance and hasattr(self.instance, 'resume'):
            self.instance.resume()
            self.status = "uploading"
            self.last_activity = time.time()
            client.send_message("/upload/resumed", [self.task_id])

    def cancel(self):
        if self.instance and hasattr(self.instance, 'cancel'):
            self.instance.cancel()
        self.status = "cancelled"
        self.last_activity = time.time()
        client.send_message("/upload/cancelled", [self.task_id])


# ============================================================
#                     UPLOAD MANAGER
# ============================================================

class UploadManager:
    def __init__(self):
        self.tasks = {}
        self.last_activity = time.time()
        self.is_running = True
        self.last_mins_left = 0
        self._start_inactivity_check()

    def _start_inactivity_check(self):
        def check():
            while self.is_running:
                time.sleep(60)
                if not self.is_running:
                    break

                now = time.time()
                inactive = now - self.last_activity
                minutes = int(inactive // 60)
                left = max(0, 30 - minutes)

                if left != self.last_mins_left:
                    msg = (
                        f"Upload service running. Auto-stop in {left}min"
                        if left > 0 else
                        "Upload service - Shutting down..."
                    )
                    n.updateMessage(msg)

                self.last_mins_left = left

                active = any(
                    t.status in ["uploading", "pending"]
                    for t in self.tasks.values()
                )

                if not active and inactive > 1800:
                    self.stop_service()
                    break

        threading.Thread(target=check, daemon=True).start()

    def update_activity(self):
        self.last_activity = time.time()

    def generate_id(self, f, u):
        return hash(f"{f}_{u}_{time.time()}") % 1000000

    def start(self, file_path, upload_url):
        self.update_activity()

        task_id = self.generate_id(file_path, upload_url)
        task = UploadTask(task_id, file_path, upload_url)
        self.tasks[task_id] = task

        threading.Thread(target=task.start, daemon=True).start()
        client.send_message("/upload/started", [task_id])

    def pause(self, t):  self.tasks.get(t, None) and self.tasks[t].pause()
    def resume(self, t): self.tasks.get(t, None) and self.tasks[t].resume()
    def cancel(self, t): self.tasks.get(t, None) and self.tasks[t].cancel()

    def get_status(self, t):
        return self.tasks[t].status if t in self.tasks else "not_found"

    def list_tasks(self):
        return {tid: t.status for tid, t in self.tasks.items()}

    def stop_service(self):
        self.is_running = False
        for t in self.tasks.values():
            if t.status in ["uploading", "pending"]:
                t.cancel()

        try:
            service.stopSelf()
        except:
            pass


# ============================================================
#                     OSC HANDLERS
# ============================================================

manager = UploadManager()
n.addButton("Stop Service", lambda: manager.stop_service())
n.refresh()

disp = dispatcher.Dispatcher()
disp.map("/upload/start",  lambda a, f, u: manager.start(f, u))
disp.map("/upload/pause",  lambda a, t: manager.pause(t))
disp.map("/upload/resume", lambda a, t: manager.resume(t))
disp.map("/upload/cancel", lambda a, t: manager.cancel(t))
disp.map("/upload/status", lambda a, t:
         client.send_message("/upload/status", [t, manager.get_status(t)]))
disp.map("/upload/list", lambda a:
         client.send_message("/upload/list", [json.dumps(manager.list_tasks())]))
disp.map("/service/stop", lambda a: manager.stop_service())
disp.map("/service/keepalive",
         lambda a: (manager.update_activity(),
                    client.send_message("/service/keepalive", ["ack"])))

print(f"[Upload Service] Starting OSC server on port {SERVICE_PORT}")
server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)

try:
    server.serve_forever()
finally:
    manager.is_running = False

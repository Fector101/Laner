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

# ----------------------------
# Logging
# ----------------------------
try:
    start_logging()
    print("Combined Service Logging started.")
except Exception:
    traceback.print_exc()

PythonService = autoclass("org.kivy.android.PythonService")
BuildVersion = autoclass("android.os.Build$VERSION")
ServiceInfo = autoclass("android.content.pm.ServiceInfo")
service = PythonService.mService

try:
    SERVICE_PORT = int(environ.get("PYTHON_SERVICE_ARGUMENT", "5006"))
except:
    SERVICE_PORT = 5006

APP_PORT = 5007
APP_IP = "127.0.0.1"

# ----------------------------
# Notification
# ----------------------------
n = Notification(
    id=150,
    title="Transfer Service",
    message="Managing uploads/downloads. Auto-stop after 30min inactivity."
)

builder = n.start_building()
foreground_type = (
    ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
    if BuildVersion.SDK_INT >= 30 else 0
)

service.startForeground(n.id, builder.build(), foreground_type)

client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)


# ==================================================================
# TASK BASE CLASS (shared logic)
# ==================================================================

class BaseTask:
    def __init__(self, task_id):
        self.task_id = task_id
        self.instance = None
        self.status = "pending"
        self.last_activity = time.time()

    def _send(self, route, payload):
        client.send_message(route, payload)


# ==================================================================
# DOWNLOAD TASK
# ==================================================================

class DownloadTask(BaseTask):
    def __init__(self, task_id, url, dest):
        super().__init__(task_id)
        self.url = url
        self.dest = dest

    def start(self):
        try:
            self.status = "downloading"
            self.last_activity = time.time()

            self.instance = AsyncRequest(notification_id=self.task_id)

            self.instance.download_file(
                file_path=self.url,
                save_path=self.dest,
                success=self._on_success,
                #progress=self._on_progress,
                #failure=self._on_error
            )
        except Exception as e:
            self._on_error(str(e))

    def _on_progress(self, progress, downloaded, total):
        self.last_activity = time.time()
        self._send("/download/progress",
                   [self.task_id, progress, downloaded, total])

    def _on_success(self):
        self.status = "completed"
        self.last_activity = time.time()
        self._send("/download/complete", [self.task_id, self.dest])

    def _on_error(self, msg):
        self.status = "error"
        self.last_activity = time.time()
        self._send("/download/error", [self.task_id, msg])

    def pause(self):
        if self.instance and hasattr(self.instance, "pause"):
            self.instance.pause()
            self.status = "paused"
            self._send("/download/paused", [self.task_id])

    def resume(self):
        if self.instance and hasattr(self.instance, "resume"):
            self.instance.resume()
            self.status = "downloading"
            self._send("/download/resumed", [self.task_id])

    def cancel(self):
        if self.instance and hasattr(self.instance, "cancel"):
            self.instance.cancel()
        self.status = "cancelled"
        self._send("/download/cancelled", [self.task_id])


# ==================================================================
# UPLOAD TASK
# ==================================================================

class UploadTask(BaseTask):
    def __init__(self, task_id, file_path, upload_url):
        super().__init__(task_id)
        self.file_path = file_path
        self.upload_url = upload_url

    def start(self):
        try:
            self.status = "uploading"
            self.last_activity = time.time()

            self.instance = AsyncRequest(notification_id=self.task_id)

            self.instance.upload_file(
                file_path=self.file_path,
                upload_url=self.upload_url,
                success=self._on_success,
                #progress=self._on_progress,
                #failure=self._on_error
            )
        except Exception as e:
            self._on_error(str(e))

    def _on_progress(self, progress, sent, total):
        self.last_activity = time.time()
        self._send("/upload/progress",
                   [self.task_id, progress, sent, total])

    def _on_success(self):
        self.status = "completed"
        self.last_activity = time.time()
        self._send("/upload/complete", [self.task_id, self.file_path])

    def _on_error(self, msg):
        self.status = "error"
        self.last_activity = time.time()
        self._send("/upload/error", [self.task_id, msg])

    def pause(self):
        if self.instance and hasattr(self.instance, "pause"):
            self.instance.pause()
            self.status = "paused"
            self._send("/upload/paused", [self.task_id])

    def resume(self):
        if self.instance and hasattr(self.instance, "resume"):
            self.instance.resume()
            self.status = "uploading"
            self._send("/upload/resumed", [self.task_id])

    def cancel(self):
        if self.instance and hasattr(self.instance, "cancel"):
            self.instance.cancel()
        self.status = "cancelled"
        self._send("/upload/cancelled", [self.task_id])


# ==================================================================
# UNIFIED MANAGER
# ==================================================================

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.last_activity = time.time()
        self.is_running = True
        self.last_mins_left = 0

        self._start_inactivity_thread()

    def _start_inactivity_thread(self):
        def monitor():
            while self.is_running:
                time.sleep(60)
                now = time.time()
                inactive = now - self.last_activity

                mins = int(inactive // 60)
                left = max(0, 30 - mins)

                # update notification
                if left != self.last_mins_left:
                    msg = (
                        f"Service running. Auto-stop in {left}min"
                        if left > 0 else
                        "Service shutting down..."
                    )
                    n.updateMessage(msg)

                self.last_mins_left = left

                active = any(
                    t.status in ["downloading", "uploading", "pending"]
                    for t in self.tasks.values()
                )

                if not active and inactive > 1800:
                    self.stop_service()
                    break

        threading.Thread(target=monitor, daemon=True).start()

    def update_activity(self):
        self.last_activity = time.time()

    def _new_id(self, a, b):
        return hash(f"{a}_{b}_{time.time()}") % 1000000

    # ----- Download -----
    def start_download(self, url, dest):
        self.update_activity()
        tid = self._new_id(url, dest)
        task = DownloadTask(tid, url, dest)
        self.tasks[tid] = task
        threading.Thread(target=task.start, daemon=True).start()
        client.send_message("/download/started", [tid])

    # ----- Upload -----
    def start_upload(self, file_path, upload_url):
        self.update_activity()
        tid = self._new_id(file_path, upload_url)
        task = UploadTask(tid, file_path, upload_url)
        self.tasks[tid] = task
        threading.Thread(target=task.start, daemon=True).start()
        client.send_message("/upload/started", [tid])

    # shared
    def pause(self, t):
        self.update_activity()
        if t in self.tasks: self.tasks[t].pause()

    def resume(self, t):
        self.update_activity()
        if t in self.tasks: self.tasks[t].resume()

    def cancel(self, t):
        self.update_activity()
        if t in self.tasks: self.tasks[t].cancel()

    def status(self, t):
        return self.tasks[t].status if t in self.tasks else "not_found"

    def list_tasks(self):
        return {tid: t.status for tid, t in self.tasks.items()}

    def stop_service(self):
        self.is_running = False
        for t in self.tasks.values():
            if t.status in ["downloading", "uploading", "pending"]:
                t.cancel()
        try:
            service.stopSelf()
        except:
            pass


# ==================================================================
# OSC ROUTES
# ==================================================================

manager = TaskManager()
n.addButton("Stop Service", lambda: manager.stop_service())
n.refresh()

disp = dispatcher.Dispatcher()

# download routes
disp.map("/download/start", lambda a, url, dest: manager.start_download(url, dest))
disp.map("/download/pause", lambda a, t: manager.pause(t))
disp.map("/download/resume", lambda a, t: manager.resume(t))
disp.map("/download/cancel", lambda a, t: manager.cancel(t))
disp.map("/download/status",
         lambda a, t: client.send_message("/download/status", [t, manager.status(t)]))

# upload routes
disp.map("/upload/start", lambda a, f, u: manager.start_upload(f, u))
disp.map("/upload/pause", lambda a, t: manager.pause(t))
disp.map("/upload/resume", lambda a, t: manager.resume(t))
disp.map("/upload/cancel", lambda a, t: manager.cancel(t))
disp.map("/upload/status",
         lambda a, t: client.send_message("/upload/status", [t, manager.status(t)]))

# unified
disp.map("/tasks/list",
         lambda a: client.send_message("/tasks/list", [json.dumps(manager.list_tasks())]))

disp.map("/service/stop", lambda a: manager.stop_service())
disp.map("/service/keepalive",
         lambda a: (manager.update_activity(),
                    client.send_message("/service/keepalive", ["ack"])))

print(f"[Service] Running on port {SERVICE_PORT}")
server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)

try:
    server.serve_forever()
finally:
    manager.is_running = False

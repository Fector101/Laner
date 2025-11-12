import os
import threading
import time
import requests
from os import environ
import traceback
from pythonosc import dispatcher, osc_server, udp_client
from android_notify import Notification
from jnius import autoclass
from utils.helper import file_path_to_unique_int
# Start logging
try:
    from utils.log_redirect import start_logging
    start_logging()
    print("📜 Service Logging started. All console output will also be saved.")
except Exception as e:
    from utils.helper import log_error_to_file
    error_traceback = traceback.format_exc()
    log_error_to_file(error_traceback)
try:
    SERVICE_PORT = int(environ.get('PYTHON_SERVICE_ARGUMENT', '5006'))
except (TypeError, ValueError):
    SERVICE_PORT = 5006

print(f"[Service] Received value for port: {SERVICE_PORT}")
APP_PORT = 5007
APP_IP = "127.0.0.1"

client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)


def debug_notify(title, msg):
    """Show debug notification (optional)."""
    try:
        Notification(channel_name="debug",title=title, message=msg).send()
    except Exception as e:
        print(f"[DEBUG_NOTIFY_FAIL] {e}")



def stop_service():
    """Stops the running Android service safely."""
    try:
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        if service:
            service.stopSelf()
            Notification(title="Service", message="✅ Service stopped successfully.").send()
            print("✅ Service stopped successfully.")
        else:
            Notification(title="Service", message="⚠️ No active service instance found.").send()
            print("⚠️ No active service instance found.")
    except Exception as e:
        Notification(title="Service Error", message=str(e)).send()
        print("❌ Error while stopping service:", e)
        import traceback
        traceback.print_exc()

def get_chunk_size(file_size):
    # file_size in bytes
    if file_size < 10 * 1024 * 1024:  # < 10 MB
        return 256 * 1024             # 256 KB
    elif file_size < 100 * 1024 * 1024:  # < 100 MB
        return 1 * 1024 * 1024         # 1 MB
    else:
        return 4 * 1024 * 1024         # 4 MB


class DownloadTask(threading.Thread):
    def __init__(self, url, dest):
        super().__init__(daemon=True)
        self.url = url
        self.dest = dest
        self.task_id = file_path_to_unique_int(dest)
        self._paused = threading.Event()
        self._cancelled = threading.Event()
        self._last_progress = -1

        # ✅ Corrected: channel_name instead of channel
        self.notification = Notification(
            title="Downloading...",
            message="0% downloaded",
            channel_name="Downloads",
            id=self.task_id,
            progress_current_value=0,
            progress_max_value=100,
        )
        self.notification.send()

    def run(self):
        try:
            downloaded = 0
            if os.path.exists(self.dest):
                downloaded = os.path.getsize(self.dest)

            headers = {}
            if downloaded > 0:
                headers["Range"] = f"bytes={downloaded}-"
            headers["User-Agent"] = "LanerDownloader/1.0 (+https://github.com/Fector101)"

            try:
                import certifi
                verify_cert = certifi.where()
            except ImportError:
                verify_cert = False

            for attempt in range(3):
                try:
                    with requests.get(
                        self.url,
                        headers=headers,
                        stream=True,
                        timeout=(10, 30),
                        verify=verify_cert,
                    ) as r:
                        if r.status_code not in (200, 206):
                            if downloaded > 0 and r.status_code == 200:
                                downloaded = 0
                            else:
                                raise Exception(f"HTTP {r.status_code}")

                        total = int(r.headers.get("content-length", 0)) + downloaded
                        mode = "ab" if downloaded > 0 else "wb"

                        with open(self.dest, mode) as f:
                            chunk_size = get_chunk_size(total)
                            for chunk in r.iter_content(chunk_size):
                                if self._cancelled.is_set():
                                    raise Exception("Download cancelled")
                                while self._paused.is_set():
                                    time.sleep(0.3)
                                if not chunk:
                                    continue

                                f.write(chunk)
                                downloaded += len(chunk)
                                progress = int((downloaded / total) * 100)
                                if progress == self._last_progress:
                                    continue
                                self._last_progress = progress

                                message = f"{downloaded//1024}KB/{total//1024}KB"
                                self.notification.updateProgressBar(
                                    current_value=progress,
                                    message=message,
                                    title=f"Downloading... {progress}%"
                                )

                    self.notification.removeProgressBar("Download Complete", show_on_update=True)
                    client.send_message("/download/complete", [self.task_id, self.dest])
                    break
                except requests.exceptions.ConnectionError:
                    if attempt == 2:
                        raise
                    time.sleep(2)
        except Exception as e:
            self.notification.removeProgressBar(f"Failed: {e}", show_on_update=True)
            client.send_message("/download/error", [self.task_id, str(e)])

    def pause(self):
        self._paused.set()
        self.notification.removeProgressBar("Paused", show_on_update=True)

    def resume(self):
        if not self._paused.is_set():
            return
        self._paused.clear()
        self.notification = Notification(
            title="Resuming Download...",
            message="Resuming...",
            channel_name="Downloads",
            id=self.task_id,
            progress_current_value=0,
            progress_max_value=100,
        )
        self.notification.send()
        threading.Thread(target=self.run, daemon=True).start()

    def cancel(self):
        self._cancelled.set()
        self.notification.removeProgressBar("Cancelled", show_on_update=True)
        client.send_message("/download/cancelled", [self.task_id])


class DownloadManager:
    def __init__(self):
        self.tasks = {}

    def start(self, url, dest):
        task_id = file_path_to_unique_int(dest)
        if task_id in self.tasks:
            client.send_message("/download/error", [task_id, "Task already exists"])
            return
        task = DownloadTask(url, dest)
        self.tasks[task_id] = task
        task.start()

    def pause(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].pause()

    def resume(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].resume()

    def cancel(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            del self.tasks[task_id]


manager = DownloadManager()


# ---- OSC handlers ----
def osc_start(addr, url, dest):
    manager.start(url, dest)

def osc_pause(addr, task_id):
    manager.pause(task_id)

def osc_resume(addr, task_id):
    manager.resume(task_id)

def osc_cancel(addr, task_id):
    manager.cancel(task_id)

def osc_stop_service(addr):
    stop_service()


disp = dispatcher.Dispatcher()
disp.map("/download/start", osc_start)
disp.map("/download/pause", osc_pause)
disp.map("/download/resume", osc_resume)
disp.map("/download/cancel", osc_cancel)
disp.map("/service/stop", osc_stop_service)  # ✅ new route

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)
print(f"[Service] Listening on {SERVICE_PORT}")
server.serve_forever()

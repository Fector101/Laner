import os
import threading
import time
import requests
import hashlib
from pythonosc import dispatcher, osc_server, udp_client
from android_notify import Notification

SERVICE_PORT = 5006
APP_PORT = 5007
APP_IP = "127.0.0.1"

client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)

def debug_notify(title, msg):
    """Show quick debug notification (non-blocking)."""
    try:
        Notification(title=title, message=msg).send()
    except Exception as e:
        print(f"[DEBUG_NOTIFY_FAIL] {e}")

def string_to_int(input_string: str, max_value=2_147_483_647):
    hash_bytes = hashlib.sha256(input_string.encode()).digest()
    int_value = int.from_bytes(hash_bytes[:4], byteorder="big")
    return int_value % max_value


class DownloadTask(threading.Thread):
    def __init__(self, url, dest):
        super().__init__(daemon=True)
        self.url = url
        self.dest = dest
        self.task_id = string_to_int(dest)
        self._paused = threading.Event()
        self._cancelled = threading.Event()
        self._last_progress = -1

        debug_notify("Init", f"Task init for {os.path.basename(dest)}")

        try:
            self.notification = Notification(
                title="Downloading...",
                message="0% downloaded",
                channel="Downloads",
                id=self.task_id,
                progress_current_value=0,
                progress_max_value=100,
            )
            self.notification.send()
        except Exception as e:
            debug_notify("InitError", str(e))

    def run(self):
        try:
            debug_notify("Run Start", "Entered run()")

            downloaded = 0
            if os.path.exists(self.dest):
                debug_notify("File Exists", f"Resuming {self.dest}")
                downloaded = os.path.getsize(self.dest)
            else:
                debug_notify("File New", f"Starting new {self.dest}")

            headers = {}
            if downloaded > 0:
                headers["Range"] = f"bytes={downloaded}-"
            headers["User-Agent"] = "LanerDownloader/1.0 (+https://github.com/Fector101)"

            try:
                import certifi
                verify_cert = certifi.where()
                debug_notify("Certifi", "Using certifi for SSL")
            except ImportError:
                verify_cert = False
                debug_notify("SSL", "No certifi found (verify=False)")

            for attempt in range(3):
                debug_notify("Attempt", f"Attempt {attempt + 1}")
                try:
                    debug_notify("Request", "Starting GET request")
                    with requests.get(
                        self.url,
                        headers=headers,
                        stream=True,
                        timeout=(10, 30),
                        verify=verify_cert,
                    ) as r:
                        debug_notify("Response", f"HTTP {r.status_code}")

                        if r.status_code not in (200, 206):
                            if downloaded > 0 and r.status_code == 200:
                                downloaded = 0
                            else:
                                raise Exception(f"HTTP {r.status_code}")

                        total = int(r.headers.get("content-length", 0)) + downloaded
                        mode = "ab" if downloaded > 0 else "wb"
                        debug_notify("OpenFile", f"Opening {mode} file")

                        with open(self.dest, mode) as f:
                            for chunk in r.iter_content(1024 * 64):
                                if self._cancelled.is_set():
                                    debug_notify("Cancelled", "Download cancelled mid-loop")
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

                    debug_notify("Complete", "Removing progress bar")
                    self.notification.removeProgressBar("Download Complete", show_on_update=True)
                    client.send_message("/download/complete", [self.task_id, self.dest])
                    break
                except requests.exceptions.ConnectionError:
                    debug_notify("Retry", "Connection error, retrying...")
                    if attempt == 2:
                        raise
                    time.sleep(2)
        except Exception as e:
            debug_notify("Error", str(e))
            try:
                self.notification.removeProgressBar(f"Failed: {e}", show_on_update=True)
            except Exception:
                pass
            client.send_message("/download/error", [self.task_id, str(e)])

    def pause(self):
        self._paused.set()
        debug_notify("Pause", "Download paused")
        self.notification.removeProgressBar("Paused", show_on_update=True)

    def resume(self):
        if not self._paused.is_set():
            return
        self._paused.clear()
        debug_notify("Resume", "Resuming download")
        self.notification = Notification(
            title="Resuming Download...",
            message="Resuming...",
            channel="Downloads",
            id=self.task_id,
            progress_current_value=0,
            progress_max_value=100,
        )
        self.notification.send()
        threading.Thread(target=self.run, daemon=True).start()

    def cancel(self):
        self._cancelled.set()
        debug_notify("Cancel", "Download cancelled manually")
        self.notification.removeProgressBar("Cancelled", show_on_update=True)
        client.send_message("/download/cancelled", [self.task_id])


class DownloadManager:
    def __init__(self):
        debug_notify("Manager", "DownloadManager initialized")
        self.tasks = {}

    def start(self, url, dest):
        task_id = string_to_int(dest)
        if task_id in self.tasks:
            debug_notify("Start", "Task already exists")
            client.send_message("/download/error", [task_id, "Task already exists"])
            return
        debug_notify("Start", f"Creating new task for {os.path.basename(dest)}")
        task = DownloadTask(url, dest)
        self.tasks[task_id] = task
        task.start()

    def pause(self, task_id):
        debug_notify("PauseCmd", f"Pausing {task_id}")
        if task_id in self.tasks:
            self.tasks[task_id].pause()

    def resume(self, task_id):
        debug_notify("ResumeCmd", f"Resuming {task_id}")
        if task_id in self.tasks:
            self.tasks[task_id].resume()

    def cancel(self, task_id):
        debug_notify("CancelCmd", f"Cancelling {task_id}")
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            del self.tasks[task_id]


manager = DownloadManager()


# ---- OSC handlers ----
def osc_start(addr, url, dest):
    debug_notify("OSC", f"Start received for {os.path.basename(dest)}")
    manager.start(url, dest)

def osc_pause(addr, task_id):
    debug_notify("OSC", f"Pause received {task_id}")
    manager.pause(task_id)

def osc_resume(addr, task_id):
    debug_notify("OSC", f"Resume received {task_id}")
    manager.resume(task_id)

def osc_cancel(addr, task_id):
    debug_notify("OSC", f"Cancel received {task_id}")
    manager.cancel(task_id)


disp = dispatcher.Dispatcher()
disp.map("/download/start", osc_start)
disp.map("/download/pause", osc_pause)
disp.map("/download/resume", osc_resume)
disp.map("/download/cancel", osc_cancel)

try:
    debug_notify("Server", "Starting OSC UDP server")
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)
    debug_notify("Server", f"Listening on {SERVICE_PORT}")
    print(f"[Service] Listening on {SERVICE_PORT}")
    server.serve_forever()
except Exception as e:
    debug_notify("ServerError", str(e))

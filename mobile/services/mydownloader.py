import os
import threading
import time
import requests
from pythonosc import dispatcher, osc_server, udp_client
from android_notify import Notification

SERVICE_PORT = 5006
APP_PORT = 5007
APP_IP = "127.0.0.1"

client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)


class DownloadTask(threading.Thread):
    def __init__(self, url, dest, task_id):
        super().__init__()
        self.url = url
        self.dest = dest
        self.task_id = task_id
        self._paused = threading.Event()
        self._cancelled = threading.Event()
        self._paused.clear()
        self._cancelled.clear()

        # Initialize Android notification
        self.notification = Notification(
            title="Downloading...",
            message="0% downloaded",
            progress_current_value=0,
            progress_max_value=100
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

            for attempt in range(3):  # retry a few times
                try:
                    with requests.get(self.url, headers=headers, stream=True, timeout=(10, 30)) as r:
                        if r.status_code not in (200, 206):
                            if downloaded > 0 and r.status_code == 200:
                                # Server doesn't support resume
                                downloaded = 0
                            else:
                                raise Exception(f"HTTP {r.status_code}")

                        total = int(r.headers.get("content-length", 0)) + downloaded
                        mode = "ab" if downloaded > 0 else "wb"

                        with open(self.dest, mode) as f:
                            for chunk in r.iter_content(1024 * 64):
                                if self._cancelled.is_set():
                                    raise Exception("Download cancelled")
                                while self._paused.is_set():
                                    time.sleep(0.3)
                                if not chunk:
                                    continue
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress = int((downloaded / total) * 100)
                                message = f"{downloaded//1024}KB/{total//1024}KB"
                                self.notification.updateProgressBar(
                                    current_value=progress,
                                    message=message,
                                    title=f"Downloading... {progress}%"
                                )
                                client.send_message("/download/progress", [self.task_id, progress])

                        if downloaded >= total:
                            self.notification.removeProgressBar("Download Complete", show_on_update=True)
                            client.send_message("/download/complete", [self.task_id, self.dest])
                        else:
                            client.send_message("/download/paused", [self.task_id, downloaded])
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
        if self._paused.is_set():
            self._paused.clear()
            self.notification = Notification(
                title="Resuming Download...",
                message="Resuming...",
                progress_current_value=0,
                progress_max_value=100
            )
            self.notification.send()
            t = threading.Thread(target=self.run)
            t.start()

    def cancel(self):
        self._cancelled.set()
        self.notification.removeProgressBar("Cancelled", show_on_update=True)
        client.send_message("/download/cancelled", [self.task_id])


class DownloadManager:
    def __init__(self):
        self.tasks = {}

    def start(self, url, dest, task_id):
        if task_id in self.tasks:
            client.send_message("/download/error", [task_id, "Task already exists"])
            return
        task = DownloadTask(url, dest, task_id)
        self.tasks[task_id] = task
        task.start()

    def pause(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].pause()
            client.send_message("/download/paused", [task_id])

    def resume(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].resume()
            client.send_message("/download/resumed", [task_id])

    def cancel(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            del self.tasks[task_id]


manager = DownloadManager()


# OSC handlers
def osc_start(addr, url, dest, task_id):
    manager.start(url, dest, task_id)

def osc_pause(addr, task_id):
    manager.pause(task_id)

def osc_resume(addr, task_id):
    manager.resume(task_id)

def osc_cancel(addr, task_id):
    manager.cancel(task_id)


disp = dispatcher.Dispatcher()
disp.map("/download/start", osc_start)
disp.map("/download/pause", osc_pause)
disp.map("/download/resume", osc_resume)
disp.map("/download/cancel", osc_cancel)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)
print(f"[Service] Listening on {SERVICE_PORT}")
server.serve_forever()
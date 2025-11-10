import os
import threading
import requests
from pythonosc import dispatcher, osc_server, udp_client

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

    def run(self):
        try:
            # Check if resuming
            downloaded = 0
            if os.path.exists(self.dest):
                downloaded = os.path.getsize(self.dest)

            headers = {"Range": f"bytes={downloaded}-"} if downloaded > 0 else {}

            with requests.get(self.url, stream=True, headers=headers) as r:
                if r.status_code not in (200, 206):
                    raise Exception(f"Server doesn't support resume (status {r.status_code})")

                total = int(r.headers.get("content-length", 0)) + downloaded
                mode = "ab" if downloaded > 0 else "wb"

                with open(self.dest, mode) as f:
                    for chunk in r.iter_content(1024 * 64):
                        if self._cancelled.is_set():
                            break
                        while self._paused.is_set():
                            threading.Event().wait(0.2)
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = int((downloaded / total) * 100)
                            client.send_message("/download/progress", [self.task_id, progress])

                if not self._cancelled.is_set():
                    if downloaded >= total:
                        client.send_message("/download/complete", [self.task_id, self.dest])
                    else:
                        client.send_message("/download/paused", [self.task_id, downloaded])
        except Exception as e:
            client.send_message("/download/error", [self.task_id, str(e)])

    def pause(self):
        self._paused.set()

    def resume(self):
        if self._paused.is_set():
            self._paused.clear()
            # restart thread if needed
            if not self.is_alive():
                self.run_in_thread()

    def cancel(self):
        self._cancelled.set()

    def run_in_thread(self):
        t = threading.Thread(target=self.run)
        t.start()


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
            task = self.tasks[task_id]
            if not task.is_alive():
                new_task = DownloadTask(task.url, task.dest, task.task_id)
                self.tasks[task_id] = new_task
                new_task.start()
            else:
                task.resume()
            client.send_message("/download/resumed", [task_id])

    def cancel(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            client.send_message("/download/cancelled", [task_id])
            del self.tasks[task_id]


manager = DownloadManager()


# OSC command handlers
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
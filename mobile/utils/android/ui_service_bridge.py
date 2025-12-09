import threading
import traceback
from pythonosc import dispatcher, osc_server, udp_client
from android_notify import Notification


SERVICE_IP = "127.0.0.1"   # Localhost inside the Android process


# ======================================================================
#  UI LISTENER: RECEIVES EVENTS FROM THE SERVICE (DOWNLOAD + UPLOAD)
# ======================================================================

class UIServiceListener:
    def __init__(self, APP_PORT):
        self.disp = None
        self.APP_PORT = APP_PORT

    # -------------------------------------------------------------
    # SETUP DISPATCHER (register all OSC event handlers)
    # -------------------------------------------------------------
    def setup_dispatcher(self):
        self.disp = dispatcher.Dispatcher()

        # ----- DOWNLOAD EVENTS -----
        self.disp.map("/download/progress", self.on_dl_progress)
        self.disp.map("/download/complete", self.on_dl_complete)
        self.disp.map("/download/paused", self.on_dl_paused)
        self.disp.map("/download/resumed", self.on_dl_resumed)
        self.disp.map("/download/error", self.on_dl_error)
        self.disp.map("/download/cancelled", self.on_dl_cancelled)

        # ----- UPLOAD EVENTS -----
        self.disp.map("/upload/progress", self.on_ul_progress)
        self.disp.map("/upload/complete", self.on_ul_complete)
        self.disp.map("/upload/paused", self.on_ul_paused)
        self.disp.map("/upload/resumed", self.on_ul_resumed)
        self.disp.map("/upload/error", self.on_ul_error)
        self.disp.map("/upload/cancelled", self.on_ul_cancelled)

        # OPTIONAL: list of all tasks
        self.disp.map("/tasks/list", self.on_tasks_list)

    # -------------------------------------------------------------
    # START LISTENER THREAD
    # -------------------------------------------------------------
    def __listen(self):
        print("UI Listener → service port:", self.APP_PORT)

        server = osc_server.ThreadingOSCUDPServer(
            ("0.0.0.0", self.APP_PORT),
            self.disp
        )
        server.serve_forever()

    def start(self, *args):
        self.setup_dispatcher()
        try:
            threading.Thread(
                target=self.__listen,
                daemon=True,
                name="UIServiceListenerThread"
            ).start()
        except Exception:
            traceback.print_exc()

    # ============================================================
    # DOWNLOAD HANDLERS
    # ============================================================

    def on_dl_progress(self, addr, task_id, progress):
        print(f"[Download Progress] {task_id}: {progress}%")

    def on_dl_complete(self, addr, task_id, dest):
        print(f"[Download Complete] {task_id} saved → {dest}")

    def on_dl_paused(self, addr, task_id):
        print(f"[Download Paused] {task_id}")

    def on_dl_resumed(self, addr, task_id):
        print(f"[Download Resumed] {task_id}")

    def on_dl_error(self, addr, task_id, msg):
        print(f"[Download Error] {task_id}: {msg}")
        Notification(
            title=f"Download Error ({task_id})",
            message=str(msg)
        ).send()

    def on_dl_cancelled(self, addr, *args):
        print(f"[Download Cancelled]", args)

    # ============================================================
    # UPLOAD HANDLERS
    # ============================================================

    def on_ul_progress(self, addr, task_id, progress):
        print(f"[Upload Progress] {task_id}: {progress}%")

    def on_ul_complete(self, addr, task_id, file_path):
        print(f"[Upload Complete] {task_id} → {file_path}")

    def on_ul_paused(self, addr, task_id):
        print(f"[Upload Paused] {task_id}")

    def on_ul_resumed(self, addr, task_id):
        print(f"[Upload Resumed] {task_id}")

    def on_ul_error(self, addr, task_id, msg):
        print(f"[Upload Error] {task_id}: {msg}")
        Notification(
            title=f"Upload Error ({task_id})",
            message=str(msg)
        ).send()

    def on_ul_cancelled(self, addr, *args):
        print(f"[Upload Cancelled]", args)

    # ============================================================
    # TASK LIST HANDLER
    # ============================================================
    def on_tasks_list(self, addr, json_data):
        print("[Tasks List]", json_data)



# ======================================================================
#  UI MESSENGER: SENDS COMMANDS TO THE SERVICE (DOWNLOAD + UPLOAD)
# ======================================================================

class UIServiceMessenger:
    def __init__(self, service_port):
        self.client = None
        try:
            self.client = udp_client.SimpleUDPClient(SERVICE_IP, service_port)
            print(f"[Messenger] Connected to {SERVICE_IP}:{service_port}")
        except Exception as e:
            print("[Messenger Error] Could not connect:", e)
            traceback.print_exc()

    # Safe send
    def _send(self, path, args):
        if not self.client:
            print(f"[Messenger] Not connected — cannot send → {path}")
            return
        self.client.send_message(path, args)

    # ============================================================
    # DOWNLOAD COMMANDS
    # ============================================================

    def start_download(self, url, destination_path):
        self._send("/download/start", [url, destination_path])
        print(f"[DL Start] {url} → {destination_path}")

    def pause_download(self, task_id):
        self._send("/download/pause", [task_id])

    def resume_download(self, task_id):
        self._send("/download/resume", [task_id])

    def cancel_download(self, task_id):
        self._send("/download/cancel", [task_id])

    def get_download_status(self, task_id):
        self._send("/download/status", [task_id])

    # ============================================================
    # UPLOAD COMMANDS
    # ============================================================

    def start_upload(self, file_path, upload_url):
        self._send("/upload/start", [file_path, upload_url])
        print(f"[UL Start] {file_path} → {upload_url}")

    def pause_upload(self, task_id):
        self._send("/upload/pause", [task_id])

    def resume_upload(self, task_id):
        self._send("/upload/resume", [task_id])

    def cancel_upload(self, task_id):
        self._send("/upload/cancel", [task_id])

    def get_upload_status(self, task_id):
        self._send("/upload/status", [task_id])

    # ============================================================
    # SHARED COMMANDS
    # ============================================================

    def list_all_tasks(self):
        self._send("/tasks/list", [])
        print("[List Tasks] request sent")

    def stop_service(self):
        self._send("/service/stop", [])
        print("[Service Stop] request sent")

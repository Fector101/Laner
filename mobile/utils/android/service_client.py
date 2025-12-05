import threading
import traceback
from pythonosc import dispatcher, osc_server,udp_client
from android_notify import Notification


class UIServiceListener:
    def __init__(self,APP_PORT):
        self.disp = None
        self.APP_PORT=APP_PORT

    # === Dispatcher Setup ===
    def setup_dispatcher(self):
        self.disp = dispatcher.Dispatcher()
        self.disp.map("/download/progress", self.on_progress)
        self.disp.map("/download/complete", self.on_complete)
        self.disp.map("/download/paused", self.on_paused)
        self.disp.map("/download/resumed", self.on_resumed)
        self.disp.map("/download/error", self.on_error)
        self.disp.map("/download/cancelled", self.on_cancelled)

    # === OSC Server Listener ===
    def __listen(self):
        print("UI Listener",f"Listening to service on port {self.APP_PORT}")
        server = osc_server.ThreadingOSCUDPServer(
            ("0.0.0.0", self.APP_PORT),
            self.disp
        )
        server.serve_forever()

    # === Start Listener (e.g. from UI button) ===
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
        
    # === Log/Event Handlers ===
    def on_progress(self, addr, task_id, progress):
        print(f"[Progress] {progress}")

    def on_complete(self, addr, task_id, dest):
        print("[Complete]", dest)

    def on_paused(self, addr, task_id):
        print("[Paused]", addr)

    def on_resumed(self, addr, task_id):
        print("[Resumed]", addr)

    def on_error(self, addr, task_id, msg):
        Notification(
            title=f"Download Error ({task_id})",
            message=str(msg)
        ).send()
        
    def on_cancelled(self, address, *args):
        print("[Cancelled]", args)


SERVICE_IP = "127.0.0.1"  # Usually localhost inside the app


class UIServiceMessenger:
    def __init__(self,service_port):
        self.client = None
        try:
            self.client = udp_client.SimpleUDPClient(SERVICE_IP, service_port)
            print(f"[Messenger] Connected on {SERVICE_IP}:{service_port}")
        except Exception as e:
            print("Start service client error:", e)
            traceback.print_exc()

    # === Safe Sender ===
    def _send(self, path, args):
        if not self.client:
            print(f"[Messenger] Not connected — cannot send: {path}")
            return
        self.client.send_message(path, args)

    # === Download Control Commands ===
    def start_download(self, url, destination_path):
        self._send("/download/start", [url, destination_path])
        print(f"Sent to service Start: {url} → {destination_path}")

    def pause_download(self, task_id):
        self._send("/download/pause", [task_id])
        print(f"⏸️ Pause: {task_id}")

    def resume_download(self, task_id):
        self._send("/download/resume", [task_id])
        print(f"▶ Resume: {task_id}")

    def cancel_download(self, task_id):
        self._send("/download/cancel", [task_id])
        print(f"❌ Cancel: {task_id}")

    def get_download_status(self, task_id):
        self._send("/download/status", [task_id])
        print(f"📊 Status: {task_id}")

    def list_all_tasks(self):
        self._send("/download/list", [])
        print("📋 List all tasks")

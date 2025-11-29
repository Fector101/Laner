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
import random

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
n=Notification(id=101, title='Laner Download Service', message='Download service is running. No activity for 30min will auto-stop.')

client = udp_client.SimpleUDPClient(APP_IP, APP_PORT)

class DownloadTask:
    def __init__(self, task_id, url, dest):
        self.task_id = task_id
        self.url = url
        self.dest = dest
        self.instance = None
        self.status = "pending"  # pending, downloading, paused, completed, error, cancelled
        self.last_activity = time.time()

    def start(self):
        """Start the download using AsyncRequest"""
        try:
            self.status = "downloading"
            self.last_activity = time.time()
            
            self.instance = AsyncRequest(notification_id=self.task_id)
            self.instance.download_file(
                file_path=self.url,
                save_path=self.dest,
                success=self._on_success,
                #failure=self._on_error,
                #progress=self._on_progress
            )
            
        except Exception as e:
            self._on_error(str(e))

    def _on_progress(self, progress, downloaded, total):
        """Handle download progress updates - AsyncRequest handles notifications"""
        self.last_activity = time.time()
        # Send progress update to main app only - AsyncRequest handles notifications
        client.send_message("/download/progress", [self.task_id, progress, downloaded, total])

    def _on_success(self):
        """Handle successful download completion"""
        self.status = "completed"
        self.last_activity = time.time()
        client.send_message("/download/complete", [self.task_id, self.dest])

    def _on_error(self, error_msg):
        """Handle download errors"""
        self.status = "error"
        self.last_activity = time.time()
        client.send_message("/download/error", [self.task_id, str(error_msg)])

    def pause(self):
        """Pause the download"""
        if self.instance and hasattr(self.instance, 'pause'):
            self.instance.pause()
            self.status = "paused"
            self.last_activity = time.time()
            client.send_message("/download/paused", [self.task_id])

    def resume(self):
        """Resume the download"""
        if self.instance and hasattr(self.instance, 'resume'):
            self.instance.resume()
            self.status = "downloading"
            self.last_activity = time.time()
            client.send_message("/download/resumed", [self.task_id])

    def cancel(self):
        """Cancel the download"""
        if self.instance and hasattr(self.instance, 'cancel'):
            self.instance.cancel()
        self.status = "cancelled"
        self.last_activity = time.time()
        client.send_message("/download/cancelled", [self.task_id])


class DownloadManager:
    def __init__(self):
        self.tasks = {}
        self.last_activity = time.time()
        self.is_running = True
        self.last_mins_left=0
        
        # Start background thread to check for inactivity
        self._start_inactivity_check()

    def _start_inactivity_check(self):
        """Start background thread to check for inactivity"""
        def check_inactivity():
            while self.is_running:
                time.sleep(60)  # Check every minute
                if not self.is_running:
                    break
                    
                current_time = time.time()
                inactive_time = current_time - self.last_activity

                minutes_inactive = int(inactive_time // 60)
                minutes_left = max(0, 30 - minutes_inactive)
                if self.last_mins_left != minutes_left:
                    if minutes_left > 0:
                        message = f'Download service running. Auto-stop in {minutes_left}min'
                    else:
                        message = 'Download service - Shutting down...'
                    n.updateMessage(message)
                self.last_mins_left = minutes_left
                # Check if no active downloads and 30 minutes of inactivity
                active_downloads = any(task.status in ["downloading", "pending"] for task in self.tasks.values())
                
                if not active_downloads and inactive_time > 1800:  # 30 minutes
                    print("No activity for 30 minutes, shutting down service...")
                    self.stop_service()
                    break
        
        threading.Thread(target=check_inactivity, daemon=True).start()

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()

    def generate_task_id(self, url, dest):
        """Generate unique task ID"""
        return hash(f"{url}_{dest}_{time.time()}") % 1000000

    def start(self, url, dest):
        """Start a new download task"""
        self.update_activity()
        
        # Check if same file is already downloading
        for task_id, task in self.tasks.items():
            if task.dest == dest and task.status in ["downloading", "pending"]:
                client.send_message("/download/error", [task_id, "File already being downloaded"])
                return
        
        task_id = self.generate_task_id(url, dest)
        task = DownloadTask(task_id, url, dest)
        self.tasks[task_id] = task
        
        # Start download in separate thread
        threading.Thread(target=task.start, daemon=True).start()
        
        client.send_message("/download/started", [task_id])
        return task_id

    def pause(self, task_id):
        """Pause a download task"""
        self.update_activity()
        if task_id in self.tasks:
            self.tasks[task_id].pause()

    def resume(self, task_id):
        """Resume a download task"""
        self.update_activity()
        if task_id in self.tasks:
            self.tasks[task_id].resume()

    def cancel(self, task_id):
        """Cancel a download task"""
        self.update_activity()
        if task_id in self.tasks:
            self.tasks[task_id].cancel()

    def get_status(self, task_id):
        """Get status of a download task"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return "not_found"

    def list_tasks(self):
        """List all current tasks"""
        return {task_id: task.status for task_id, task in self.tasks.items()}

    def stop_service(self):
        """Stop the service safely"""
        self.is_running = False
        
        # Cancel all active downloads
        for task in self.tasks.values():
            if task.status in ["downloading", "pending"]:
                task.cancel()
        
        try:
            PythonService = autoclass('org.kivy.android.PythonService')
            service = PythonService.mService
            if service:
                service.stopSelf()
                print("✅ Service stopped due to inactivity.")
            else:
                print("⚠️ No active service instance found.")
        except Exception as e:
            print("❌ Error while stopping service:", e)
            traceback.print_exc()


# Initialize manager
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

def osc_status(addr, task_id):
    status = manager.get_status(task_id)
    client.send_message("/download/status", [task_id, status])

def osc_list_tasks(addr):
    tasks = manager.list_tasks()
    client.send_message("/download/list", [json.dumps(tasks)])

def osc_stop_service(addr):
    manager.stop_service()

def osc_keep_alive(addr):
    """Reset inactivity timer"""
    manager.update_activity()
    client.send_message("/service/keepalive", ["ack"])

# Setup OSC server
disp = dispatcher.Dispatcher()
disp.map("/download/start", osc_start)
disp.map("/download/pause", osc_pause)
disp.map("/download/resume", osc_resume)
disp.map("/download/cancel", osc_cancel)
disp.map("/download/status", osc_status)
disp.map("/download/list", osc_list_tasks)
disp.map("/service/stop", osc_stop_service)
disp.map("/service/keepalive", osc_keep_alive)  # For main app to reset inactivity timer

# Create persistent service notification (not download progress)
try:
    n.addButton('Stop Service', lambda: manager.stop_service())
    n.send(persistent=True, close_on_click=False)
    print("📱 Service notification created")
except Exception as e:
    print("Service notification error:", e)

print(f"[Service] Starting OSC server on port {SERVICE_PORT}")
server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", SERVICE_PORT), disp)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Service interrupted")
finally:
    manager.is_running = False

import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, start_app):
        self.start_app = start_app
        self.process = None
        self.restart_app()

    def restart_app(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(['python', 'main.py'])  # your main Kivy file

    def on_modified(self, event):
        if event.src_path.endswith('.py') or event.src_path.endswith('.kv'):
            print(f"\nDetected change in: {event.src_path}\nRestarting app...")
            self.restart_app()

if __name__ == '__main__':
    path = '.'  # your project directory
    handler = ReloadHandler(start_app=True)
    observer = Observer()
    observer.schedule(handler, path=path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
            handler.process.wait()
    observer.join()

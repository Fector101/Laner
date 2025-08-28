import sys, traceback, os

if __name__ == 'config':
    from helper import getAppFolder
else:
    from workers.helper import getAppFolder

import builtins
import inspect
import os

def custom_print(*args, **kwargs):
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    builtins._print(f"[{filename}]", *args, **kwargs)

# Backup original
builtins._print = builtins.print
builtins.print = custom_print

# Now all prints will include file name
# print("This will include the filename.")

def create_preview_folder():
    """Creates a folder for preview images if it doesn't exist."""
    preview_folder = os.path.join(getAppFolder(), 'preview-imgs')
    os.makedirs(preview_folder, exist_ok=True)
    return preview_folder

create_preview_folder()

# Global exception handler to catch all unhandled exceptions
def global_exception_handler(exc_type, exc_value, exc_traceback):
    # Default traceback print
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    # Custom line after every exception
    print(f'------------------------{exc_type.__name__} Log end------------------------')

# Set the global exception handler
sys.excepthook = global_exception_handler

# Custom exception handler for threading
# This will catch exceptions in threads and print them
import threading

def thread_exception_handler(args):
    traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
    print(f'------------------------Thread Exception ({args.exc_type.__name__}) Log end------------------------')

threading.excepthook = thread_exception_handler

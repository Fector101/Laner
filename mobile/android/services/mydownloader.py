from jnius import autoclass
try:
    from utils.log_redirect import start_logging
    start_logging()
    print("📜 Service Logging started. All console output will also be saved.")
except Exception as e:
    print("File Logger Failed")

try:
    # First try: direct Android constant
    foreground_type = autoclass(
        "android.content.pm.ServiceInfo"
    ).FOREGROUND_SERVICE_TYPE_DATA_SYNC
    print("[foreground] Using ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC")

except Exception as e:
    print("[foreground error] Using ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC",e)
    try:
        # Second try: PythonService fallback
        foreground_type = autoclass(
            "org.kivy.android.PythonService"
        ).mService.FOREGROUND_SERVICE_TYPE_DATA_SYNC
        print("[foreground] Using PythonService.FOREGROUND_SERVICE_TYPE_DATA_SYNC")

    except Exception as a:
        # Final fallback
        foreground_type = None
        print("[foreground error] Using PythonService.FOREGROUND_SERVICE_TYPE_DATA_SYNC",a)
        print("[foreground] No valid constant found — using startForeground() without type")


from android_notify import Notification
n=Notification(title="working")
n.from_foreground_service=True
builder=n.fill_args()
notification=builder.build()
# Final call
if foreground_type:
    service.startForeground(1, notification, foreground_type)
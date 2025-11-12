# I Remember this running for long without requesting unlimited battery access
# But now it only runs for roughly 60 seconds before stopping

from jnius import autoclass
print("Entered Sendnoti Service is running...")

# Android classes
Context = autoclass('android.content.Context')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationBuilder = autoclass('android.app.Notification$Builder')
AndroidString = autoclass('java.lang.String')

# Constants
channel_id = "download_channel"
channel_name = "Download Notifications"

# Initialize NotificationManager
service = autoclass('org.kivy.android.PythonService').mService
context = service.getApplication().getApplicationContext()
notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)

# Create Notification Channel (required for Android 8.0+)
if notification_manager.getNotificationChannel(channel_id) is None:
    channel = NotificationChannel(
        channel_id,
        AndroidString(channel_name),
        NotificationManager.IMPORTANCE_LOW,
    )
    notification_manager.createNotificationChannel(channel)

# Create the Notification Builder
builder = NotificationBuilder(context, channel_id)
builder.setContentTitle(AndroidString("Downloading..."))
builder.setSmallIcon(autoclass("android.R$drawable").ic_menu_save)
builder.setProgress(100, 0, False)  # Set initial progress

# Display the notification
notification_id = 10101
notification_manager.notify(notification_id, builder.build())




# # Simulate Download Progress
import time
for progress in range(0, 101, 10):  # Increment progress in steps of 10%
    time.sleep(5)  # Simulate time taken for download
    builder.setProgress(100, progress, False)
    builder.setContentText(AndroidString(f"{progress}% downloaded"))
    notification_manager.notify(notification_id, builder.build())

# Finish Notification
builder.setContentText(AndroidString("Download complete!"))
builder.setProgress(0, 0, False)  # Remove the progress bar
notification_manager.notify(notification_id, builder.build())

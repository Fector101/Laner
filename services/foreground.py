# from jnius import autoclass

# # Android classes
# Context = autoclass('android.content.Context')
# NotificationManager = autoclass('android.app.NotificationManager')
# NotificationChannel = autoclass('android.app.NotificationChannel')
# NotificationBuilder = autoclass('android.app.Notification$Builder')
# AndroidString = autoclass('java.lang.String')

# # Constants
# channel_id = "download_channel"
# channel_name = "Download Notifications"

# # Initialize NotificationManager
# service = autoclass('org.kivy.android.PythonService').mService
# context = service.getApplication().getApplicationContext()
# notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)

# # Create Notification Channel (required for Android 8.0+)
# if notification_manager.getNotificationChannel(channel_id) is None:
#     channel = NotificationChannel(
#         channel_id,
#         AndroidString(channel_name),
#         NotificationManager.IMPORTANCE_LOW,
#     )
#     notification_manager.createNotificationChannel(channel)

# # Create the Notification Builder
# builder = NotificationBuilder(context, channel_id)
# builder.setContentTitle(AndroidString("Downloading..."))
# builder.setSmallIcon(autoclass("android.R$drawable").ic_menu_save)
# builder.setProgress(100, 0, False)  # Set initial progress

# # Display the notification
# notification_id = 1
# notification_manager.notify(notification_id, builder.build())


print("Entered Service is running...")


# # Simulate Download Progress
# import time
# for progress in range(0, 101, 10):  # Increment progress in steps of 10%
#     time.sleep(1)  # Simulate time taken for download
#     builder.setProgress(100, progress, False)
#     builder.setContentText(AndroidString(f"{progress}% downloaded"))
#     notification_manager.notify(notification_id, builder.build())

# # Finish Notification
# builder.setContentText(AndroidString("Download complete!"))
# builder.setProgress(0, 0, False)  # Remove the progress bar
# notification_manager.notify(notification_id, builder.build())




# from jnius import autoclass
# import time


# PythonService = autoclass('org.kivy.android.PythonService')
# PythonService.mService.setAutoRestartService(True)

# while True:
#     print('this is my service and its running')
#     time.sleep(3)



try:
    from jnius import autoclass, cast
    from time import sleep

    # Android Classes
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
    Build = autoclass('android.os.Build')
    Service = autoclass('android.app.Service')

    # Constants
    SERVICE_CHANNEL = "python_foreground_service"
    SERVICE_NAME = "PythonBackgroundService"

    def create_notification(context):
        """ Create a foreground notification """
        if Build.VERSION.SDK_INT >= 26:  # Android 8.0 (API Level 26)
            channel = NotificationChannel(
                SERVICE_CHANNEL,
                "Python Foreground Service",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
            manager.createNotificationChannel(channel)

        builder = NotificationCompat.Builder(context, SERVICE_CHANNEL)
        builder.setContentTitle("Background Service")
        builder.setContentText("Python service is running in the background")
        builder.setSmallIcon(17301642)  # Default Android icon

        return builder.build()

    activity = PythonActivity.mActivity
    context = cast('android.content.Context', activity)
    notification = create_notification(context)
    
        
    # Keep the Service Alive
    while True:
        print("Service is running...")
        sleep(3)
except Exception as e:
    print("Error foreground file: ",e)
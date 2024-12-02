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



# import jnius
# Context = jnius.autoclass('android.content.Context')
# Intent = jnius.autoclass('android.content.Intent')
# PendingIntent = jnius.autoclass('android.app.PendingIntent')
# AndroidString = jnius.autoclass('java.lang.String')
# NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
# Notification = jnius.autoclass('android.app.Notification')
# PythonActivity = jnius.autoclass('org.kivy.android' + '.PythonActivity')
# service = jnius.autoclass('org.kivy.android.PythonService').mService

# notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)
# app_context = service.getApplication().getApplicationContext()


# notification_builder = NotificationBuilder(app_context)
# title = AndroidString("EzTunes".encode('utf-8'))
# message = AndroidString("Ready to play music.".encode('utf-8'))
# notification_builder.setContentTitle(title)
# notification_builder.setContentText(message)

# notification_intent = Intent(app_context, PythonActivity)
# notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
# notification_intent.setAction(Intent.ACTION_MAIN)
# notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)

# intent = PendingIntent.getActivity(service, 0, notification_intent,PendingIntent.FLAG_IMMUTABLE)
# notification_builder.setContentIntent(intent)
# Drawable = jnius.autoclass("android.R$drawable")
# icon = getattr(Drawable, 'ic_menu_info_details',None)
# notification_builder.setSmallIcon(icon)
# notification_builder.setAutoCancel(True)

# new_notification = notification_builder.getNotification()
# # try:
# #     service.startForeground(1, new_notification, service.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK)
# # except Exception as e:
# #     print(e,'----IT has failed!!!')

# try:
#     service.startForeground(1, new_notification,1)
# except Exception as e:
#     print(f"Error starting foreground service: {e}")

# # service.startForeground(1, new_notification)
# # app_class = service.getApplication().getClass()
# # PendingIntent pendingIntent = PendingIntent.getActivity(
#     # getApplicationContext(),
# #         REQUEST_CODE, intent,
# #         /* flags */ PendingIntent.FLAG_IMMUTABLE);
# # print(service,"||", code,"||" notification_intent,'|||', 0,'|||',PendingIntent.FLAG_IMMUTABLE)
# # print(service,"||", 0,"||", notification_intent,'|||','|||',PendingIntent.FLAG_IMMUTABLE)
# #Below sends the notification to the notification bar; nice but not a foreground service.
# # notification_service.notify(0, new_notification)

# # if notification_builder.VERSION.SDK_INT >= 34:

#     # service.startForeground(1,new_notification)





from jnius import autoclass
import time


PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)

while True:
    print('this is my service and its running')
    time.sleep(5)

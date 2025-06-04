# Worked as expect service type
import jnius,random
print('---------------------****---------------------',random.randint(100,200),'---------------------****---------------------')
Context = jnius.autoclass('android.content.Context')
Intent = jnius.autoclass('android.content.Intent')
PendingIntent = jnius.autoclass('android.app.PendingIntent')
AndroidString = jnius.autoclass('java.lang.String')
NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
Notification = jnius.autoclass('android.app.Notification')
service = jnius.autoclass('org.kivy.android.PythonService').mService
PythonActivity = jnius.autoclass('org.kivy.android' + '.PythonActivity')
BuildVersion = jnius.autoclass('android.os.Build$VERSION')

notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)
app_context = service.getApplication().getApplicationContext()
notification_builder = NotificationBuilder(app_context)
title = AndroidString("EzTunes".encode('utf-8'))
message = AndroidString("Ready to play music.".encode('utf-8'))

app_class = service.getApplication().getClass()
print('app_class: ',app_class)

notification_intent = Intent(app_context, PythonActivity)
notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
notification_intent.setAction(Intent.ACTION_MAIN)
notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
intent = PendingIntent.getActivity(service, 0, notification_intent,PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT)
notification_builder.setContentTitle(title)
notification_builder.setContentText(message)
notification_builder.setContentIntent(intent)
icon = app_context.getApplicationInfo().icon
notification_builder.setSmallIcon(icon)
notification_builder.setAutoCancel(True)

new_notification = notification_builder.getNotification()
# Failed to run foreground service required type
# service.startForeground(1, new_notification,service.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
# service.startForeground(1, new_notification)


# DeepSeek didn't run
# from jnius import autoclass, cast
# from android.content import Intent, Context
# from android.app import Service, PendingIntent
# from android.os import Build, IBinder
# from android.graphics import BitmapFactory
# from android import mActivity
#
# # Java classes
# PythonService = autoclass('org.kivy.android.PythonService')
# NotificationBuilder = autoclass('android.app.Notification$Builder')
# NotificationManager = autoclass('android.app.NotificationManager')
# NotificationChannel = autoclass('android.app.NotificationChannel')
# String = autoclass('java.lang.String')
#
# # Channel ID (required for Android 8+)
# CHANNEL_ID = "data_sync_channel"
# CHANNEL_NAME = "Data Sync Service"
#
# class DataSyncService(Service):
#     def onBind(self, intent):
#         return None
#
#     def onStartCommand(self, intent, flags, startId):
#         self.start_foreground()
#         return Service.START_STICKY
#
#     def start_foreground(self):
#         # Create notification channel (Android 8+)
#         if Build.VERSION.SDK_INT >= 26:
#             channel = NotificationChannel(
#                 CHANNEL_ID,
#                 String(CHANNEL_NAME),
#                 NotificationManager.IMPORTANCE_LOW
#             )
#             manager = mActivity.getSystemService(Context.NOTIFICATION_SERVICE)
#             manager.createNotificationChannel(channel)
#
#         # Create an explicit intent for the notification
#         intent = Intent(mActivity, mActivity.getClass())
#         pending_intent = PendingIntent.getActivity(
#             mActivity, 0, intent, PendingIntent.FLAG_IMMUTABLE
#         )
#
#         # Build the notification
#         notification = (
#             NotificationBuilder(mActivity, CHANNEL_ID)
#             .setContentTitle("Data Sync Running")
#             .setContentText("Syncing data in the background...")
#             .setSmallIcon(mActivity.getApplicationInfo().icon)
#             .setContentIntent(pending_intent)
#             .build()
#         )
#
#         # Start foreground service (with type)
#         if Build.VERSION.SDK_INT >= 29:
#             self.startForeground(1, notification, Service.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
#         else:
#             self.startForeground(1, notification)
#
# # Export the service for Android
# service = DataSyncService()
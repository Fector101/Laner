from jnius import autoclass, cast
import os

print("Entered Sendnoti Service is running... python")

def is_service_context():
    return "PYTHON_SERVICE_ARGUMENT" in os.environ

PythonService = autoclass("org.kivy.android.PythonService")

activity = cast("android.app.Service", PythonService.mService)
AndroidString = autoclass("java.lang.String")
Context = autoclass("android.content.Context")
Environment = autoclass("android.os.Environment")
Intent = autoclass("android.content.Intent")
NotificationBuilder = autoclass("android.app.Notification$Builder")
NotificationManager = autoclass("android.app.NotificationManager")
PendingIntent = autoclass("android.app.PendingIntent")
PythonActivity = autoclass("org.kivy.android.PythonActivity")
Notification = autoclass(u'android.app.Notification')
service = PythonService.mService
Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))
app_context = service.getApplication().getApplicationContext()

ANDROID_VERSION = autoclass("android.os.Build$VERSION")
SDK_INT = ANDROID_VERSION.SDK_INT

if SDK_INT >= 26:
    NotificationChannel = autoclass("android.app.NotificationChannel")
    notification_service = cast(NotificationManager, activity.getSystemService(Context.NOTIFICATION_SERVICE))
    channel_id = activity.getPackageName()
    app_channel = NotificationChannel(channel_id, "Kolibri Background Server", NotificationManager.IMPORTANCE_DEFAULT)
    notification_service.createNotificationChannel(app_channel)
    notification_builder = NotificationBuilder(app_context, channel_id)
else:
    notification_builder = NotificationBuilder(app_context)

notification_builder.setContentTitle(AndroidString('title'))
notification_builder.setContentText(AndroidString('message'))
notification_intent = Intent(app_context, PythonActivity)
notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
notification_intent.setAction(Intent.ACTION_MAIN)
notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
intent = PendingIntent.getActivity(
    app_context, 0,
    notification_intent, PendingIntent.FLAG_IMMUTABLE if SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT
    )
notification_builder.setContentIntent(intent)
notification_builder.setCategory(Notification.CATEGORY_SERVICE)
notification_builder.setSmallIcon(app_context.getApplicationInfo().icon)
notification_builder.setOngoing(True)
notification_builder.setAutoCancel(False)


# s=autoclass('android.app.ServiceInfo') # Error no such class
# service.startForeground(1, notification_builder.getNotification(),s.dataSync)
notification_service.notify(100, notification_builder.getNotification())

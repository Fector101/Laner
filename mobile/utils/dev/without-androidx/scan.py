from jnius import autoclass

PythonActivity = autoclass("org.kivy.android.PythonActivity")
context = PythonActivity.mActivity

Notification = autoclass("android.app.Notification")
NotificationManager = autoclass("android.app.NotificationManager")
NotificationChannel = autoclass("android.app.NotificationChannel")
NotificationBuilder = autoclass("android.app.Notification$Builder")
PendingIntent = autoclass("android.app.PendingIntent")
Intent = autoclass("android.content.Intent")
RingtoneManager = autoclass("android.media.RingtoneManager")

# Create channel
channel_id = "default_channel"
nm = context.getSystemService(context.NOTIFICATION_SERVICE)
try:
    channel = NotificationChannel(channel_id, "Default Channel", NotificationManager.IMPORTANCE_DEFAULT)
    nm.createNotificationChannel(channel)
except Exception:
    pass

# Intent for notification tap
intent = Intent(context, PythonActivity)
intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP)
pending_intent = PendingIntent.getActivity(
    context, 0, intent,
    PendingIntent.FLAG_UPDATE_CURRENT | getattr(PendingIntent, "FLAG_IMMUTABLE", 0)
)

# Build the notification
builder = NotificationBuilder(context, channel_id)
builder.setContentTitle("Hello!")
builder.setContentText("This is a notification.")
builder.setSmallIcon(context.getApplicationInfo().icon)
builder.setContentIntent(pending_intent)
builder.setAutoCancel(True)
builder.setDefaults(Notification.DEFAULT_ALL)  # ✅ Correct
builder.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))

# Show it
notification = builder.build()
nm.notify(1, notification)
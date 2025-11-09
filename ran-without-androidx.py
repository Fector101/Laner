import kivy
from kivy.app import App
from kivy.uix.label import Label
from jnius import autoclass


from kivy.utils import platform


def show_notification(title="Notification", message="This is a notification."):
    """
    Show an Android notification (Android 12+ / API 31+ compatible) using pyjnius, no AndroidX.
    """
    if platform != "android":
        print("Not running on Android — notification skipped.")
        return

    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity

    # Java classes
    Notification = autoclass("android.app.Notification")
    NotificationManager = autoclass("android.app.NotificationManager")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    PendingIntent = autoclass("android.app.PendingIntent")
    Intent = autoclass("android.content.Intent")
    RingtoneManager = autoclass("android.media.RingtoneManager")

    # Correct Builder for Android 12+ / Pydroid
    NotificationBuilder = autoclass("android.app.Notification$Builder")

    # Intent to open the app
    intent = Intent(context, PythonActivity)
    intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP)

    pending_intent = PendingIntent.getActivity(
        context, 0, intent,
        PendingIntent.FLAG_UPDATE_CURRENT | getattr(PendingIntent, "FLAG_IMMUTABLE", 0)
    )

    # NotificationManager
    nm = context.getSystemService(context.NOTIFICATION_SERVICE)

    # Channel ID (Android 8+)
    channel_id = "default_channel"
    try:
        importance = NotificationManager.IMPORTANCE_DEFAULT
        channel = NotificationChannel(channel_id, "Default Channel", importance)
        nm.createNotificationChannel(channel)
    except Exception:
        pass  # ignore on older devices

    # Build notification
    builder = NotificationBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentText(message)
    builder.setSmallIcon(context.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setAutoCancel(True)

    # Optional sound
    sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
    builder.setSound(sound_uri)

    # Show notification
    notification = builder.build()
    nm.notify(1, notification)

PythonActivity = autoclass('org.kivy.android.PythonActivity')
show_notification()
#from android_notify import Notification
#Notification.logs=1
#Notification().send()
class MyApp(App):
    def build(self):
        return Label(text=str(type(PythonActivity)))


if __name__=="__main__":
    MyApp().run()
    
    
    



import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
from jnius import autoclass

def show_notification(title="Notification", message="This is a notification.", style="default"):
    """
    Show an Android notification (Android 12+ / API 31+) using pyjnius.
    Supports simple style testing.
    """
    if platform != "android":
        print("Not running on Android — notification skipped.")
        return

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity

    Notification = autoclass("android.app.Notification")
    NotificationManager = autoclass("android.app.NotificationManager")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    PendingIntent = autoclass("android.app.PendingIntent")
    Intent = autoclass("android.content.Intent")
    RingtoneManager = autoclass("android.media.RingtoneManager")
    NotificationBuilder = autoclass("android.app.Notification$Builder")
    System = autoclass("java.lang.System")

    # Intent to open the app
    intent = Intent(context, PythonActivity)
    intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP)
    pending_intent = PendingIntent.getActivity(
        context, 0, intent,
        PendingIntent.FLAG_UPDATE_CURRENT | getattr(PendingIntent, "FLAG_IMMUTABLE", 0)
    )

    nm = context.getSystemService(context.NOTIFICATION_SERVICE)
    channel_id = "default_channel"

    try:
        importance = NotificationManager.IMPORTANCE_DEFAULT
        channel = NotificationChannel(channel_id, "Default Channel", importance)
        nm.createNotificationChannel(channel)
    except Exception:
        pass

    # Build notification
    builder = NotificationBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentIntent(pending_intent)
    builder.setAutoCancel(True)

    # Style variations
    if style == "default":
        builder.setContentText(message)
    elif style == "bigtext":
        BigTextStyle = autoclass("android.app.Notification$BigTextStyle")
        big = BigTextStyle(builder)
        big.bigText(message + " " + message + " " + message)
    elif style == "inbox":
        InboxStyle = autoclass("android.app.Notification$InboxStyle")
        inbox = InboxStyle(builder)
        for i in range(5):
            inbox.addLine(f"Line {i+1}")
    elif style == "sound":
        sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        builder.setContentText(message + " 🔔")
        builder.setSound(sound_uri)

    builder.setSmallIcon(context.getApplicationInfo().icon)
    notification = builder.build()
    nm.notify(System.currentTimeMillis() % 10000, notification)  # unique ID per notification

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        buttons = [
            ("Default", "default"),
            ("Big Text", "bigtext"),
            ("Inbox", "inbox"),
            ("Sound", "sound")
        ]
        for text, style in buttons:
            btn = Button(text=text, size_hint=(1, 0.25))
            btn.bind(on_release=lambda inst, s=style: show_notification(title=f"{text} Notification", message="This is a test", style=s))
            layout.add_widget(btn)
        return layout

if __name__ == "__main__":
    MyApp().run()
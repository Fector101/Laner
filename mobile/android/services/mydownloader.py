import jnius
try:
    from utils.log_redirect import start_logging
    start_logging()
    print("📜 Service Logging started. All console output will also be saved.")
except Exception as e:
    print("File Logger Failed")

print("🔥 Starting foreground notification setup...")

# --- base java classes ---
try:
    Context = jnius.autoclass('android.content.Context')
    Intent = jnius.autoclass('android.content.Intent')
    PendingIntent = jnius.autoclass('android.app.PendingIntent')
    AndroidString = jnius.autoclass('java.lang.String')
    NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
    Notification = jnius.autoclass('android.app.Notification')
    NotificationChannel = jnius.autoclass('android.app.NotificationChannel')
    NotificationManager = jnius.autoclass('android.app.NotificationManager')
    BuildVersion = jnius.autoclass("android.os.Build$VERSION")
    ServiceInfo = jnius.autoclass("android.content.pm.ServiceInfo")
    print("✅ Java classes loaded")
except Exception as e:
    print("❌ ERROR loading Java classes:", e)
    raise

try:
    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    PythonService = jnius.autoclass('org.kivy.android.PythonService')
    service = PythonService.mService
    print("🟢 Service instance loaded:", service)
except Exception as e:
    print("❌ ERROR loading PythonService:", e)
    raise

app_context = service.getApplication().getApplicationContext()
notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)

print("🟢 Context initialized:", app_context)
print("🟢 NotificationManager:", notification_service)

# ============================================================
# 1️⃣ CREATE THE CHANNEL (Android 8+)
# ============================================================

channel_id = "foreground_channel"
channel_name = "Foreground Service"

try:
    if BuildVersion.SDK_INT >= 26:
        print(f"📡 Android version >= 26 → Creating NotificationChannel: {channel_id}")

        importance = NotificationManager.IMPORTANCE_HIGH
        channel = NotificationChannel(channel_id, channel_name, importance)

        notification_service.createNotificationChannel(channel)
        print("✅ NotificationChannel created!")

        notification_builder = NotificationBuilder(app_context, channel_id)
        print("🛠 Builder created WITH channel ID")
    else:
        print("📡 Android < 26 → No channel required")
        notification_builder = NotificationBuilder(app_context)
        print("🛠 Builder created WITHOUT channel ID")
except Exception as e:
    print("❌ ERROR creating NotificationChannel or Builder:", e)
    raise

# ============================================================
# 2️⃣ SET NORMAL NOTIFICATION FIELDS
# ============================================================

try:
    print("📝 Setting notification content...")

    title = AndroidString("EzTunes".encode('utf-8'))
    message = AndroidString("Ready to play music.".encode('utf-8'))

    notification_intent = Intent(app_context, PythonActivity)
    notification_intent.setFlags(
        Intent.FLAG_ACTIVITY_CLEAR_TOP |
        Intent.FLAG_ACTIVITY_SINGLE_TOP |
        Intent.FLAG_ACTIVITY_NEW_TASK
    )
    notification_intent.setAction(Intent.ACTION_MAIN)
    notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
    
    PendingIntentFlags = jnius.autoclass("android.app.PendingIntent")
    FLAG_IMMUTABLE = PendingIntentFlags.FLAG_IMMUTABLE

    intent = PendingIntent.getActivity(service, 0, notification_intent, FLAG_IMMUTABLE)
    print("🟢 PendingIntent created")

    notification_builder.setContentTitle(title)
    notification_builder.setContentText(message)
    notification_builder.setContentIntent(intent)

    Drawable = jnius.autoclass("{}.R$drawable".format(service.getPackageName()))
    icon = getattr(Drawable, 'icon')
    notification_builder.setSmallIcon(icon)

    print(f"🟢 Small icon set: {icon}")

    notification_builder.setAutoCancel(True)

except Exception as e:
    print("❌ ERROR setting notification fields:", e)
    raise

# ============================================================
# 3️⃣ BUILD NOTIFICATION
# ============================================================
try:
    new_notification = notification_builder.build()
    print("✅ Notification BUILT successfully!")
except Exception as e:
    print("❌ ERROR building notification:", e)
    raise

# ============================================================
# 4️⃣ START FOREGROUND SERVICE
# ============================================================

try:
    if BuildVersion.SDK_INT >= 30:
        foreground_type = ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
        print("📡 Using FOREGROUND_SERVICE_TYPE_DATA_SYNC")
    else:
        foreground_type = 0
        print("📡 Using legacy foreground type = 0")

    print("🚀 Starting foreground service...")
    service.startForeground(1, new_notification, foreground_type)
    print("🟢 Foreground service STARTED successfully!")
except Exception as e:
    print("❌ ERROR starting foreground service:", e)
    raise
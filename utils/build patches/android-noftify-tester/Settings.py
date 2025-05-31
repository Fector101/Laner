import random
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast

def clear_cache():
    # try:
    #     show_custom_layout_notification()
    # except Exception as e:
    #     print("Color Expectation 1: ",e)
    #     traceback.print_exc()

    try:
        show_custom_notification("Hi", " Fabian", "You have 2 new messages")
    except Exception as e:
        print("Color Expectation 2: ",e)
        traceback.print_exc()

    # try:
    #     show_spannable_notification()
    # except Exception as e:
    #     print("Color Expectation 3: ",e)
    #     traceback.print_exc()
    # self.open_folder(instance)

    # Cache clearing implementation

    # pass

@run_on_ui_thread
def show_spannable_notification():
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity

    # Required Java classes
    SpannableString = autoclass('android.text.SpannableString')
    ForegroundColorSpan = autoclass('android.text.style.ForegroundColorSpan')
    Spanned = autoclass('android.text.Spanned')

    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    Build_VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
    Color = autoclass('android.graphics.Color')

    channel_id = "color_channel"
    channel_name = "Color Notifications"

    # Create NotificationChannel for Android 8+
    if Build_VERSION.SDK_INT >= Build_VERSION_CODES.O:
        channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
        manager = context.getSystemService(NotificationManager)
        manager.createNotificationChannel(channel)

    # Create SpannableString and apply spans
    return
    title_text = SpannableString("Hello Fabian")
    title_text.setSpan(ForegroundColorSpan(Color.RED), 0, 5, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
    title_text.setSpan(ForegroundColorSpan(Color.BLUE), 6, 12, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)\
        .setSmallIcon(autoclass("android.R$drawable").ic_menu_save)\
        .setContentTitle(cast('java.lang.CharSequence', title_text))\
        .setContentText("This is a dynamic color notification")\
        .setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)

    notification = builder.build()
    # NotificationManagerCompat.from_(context).notify(1, notification)
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    manager = cast(NotificationManagerCompat, notification_service)
    manager.notify(1082, notification)

# @run_on_ui_thread
# def show_custom_notification(title1, title2, message):
#     PythonActivity = autoclass('org.kivy.android.PythonActivity')
#     context = PythonActivity.mActivity
#     NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
#     NotificationManager = autoclass('android.app.NotificationManager')
#     NotificationChannel = autoclass('android.app.NotificationChannel')
#     RemoteViews = autoclass('android.widget.RemoteViews')
#
#     # Defaults
#     notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
#     notification_manager = cast(NotificationManager, notification_service)
#     channel = NotificationChannel('default_channel', 'default_channel', NotificationManager.IMPORTANCE_DEFAULT)
#     if notification_manager.getNotificationChannel('default_channel') is None:
#         notification_manager.createNotificationChannel(channel)
#
#
#     builder = NotificationCompatBuilder(context, 'default_channel')
#     builder.setSmallIcon(context.getApplicationInfo().icon)
#
#     # Create RemoteViews
#     resources = context.getResources()
#     package_name = context.getPackageName()

#     ids
#     small = resources.getIdentifier("small", "layout", package_name)
#     large = resources.getIdentifier("large", "layout", package_name)
#
#     notificationLayout = RemoteViews(package_name, small)
#     notificationLayoutExpanded = RemoteViews(package_name, large)
#     print('small: ',small,'big: ',large, 'notificationLayout: ',notificationLayout, 'notificationLayoutExpanded: ',notificationLayoutExpanded)
#
#     builder.setStyle(autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')())
#     builder.setCustomContentView(notificationLayout)
#     builder.setCustomBigContentView(notificationLayoutExpanded)
#     builder.setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)
#     notification_manager.notify(2351, builder.build())

# @run_on_ui_thread
def show_custom_layout_notification():
    # Java context
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity

    # Load required Java classes
    # LayoutInflater = autoclass('android.view.LayoutInflater')
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
    NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    Build_VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
    R = autoclass('android.R')

    # Create NotificationChannel (Android 8+)
    channel_id = "custom_channel"
    channel_name = "Custom Layout Notifications"

    if Build_VERSION.SDK_INT >= Build_VERSION_CODES.O:
        channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
        notification_manager = context.getSystemService(NotificationManager)
        notification_manager.createNotificationChannel(channel)

    # Inflate custom view from XML
    inflater = context.getSystemService(context.LAYOUT_INFLATER_SERVICE)
    layout = inflater.inflate(
        context.getResources().getIdentifier("custom_colored_title", "layout", context.getPackageName()),
        None
    )

    # Set the content title programmatically (optional)
    title_part1 = layout.findViewById(
        context.getResources().getIdentifier("title_part1", "id", context.getPackageName()))
    title_part2 = layout.findViewById(
        context.getResources().getIdentifier("title_part2", "id", context.getPackageName()))

    # title_part1.setText("Hello")
    # title_part2.setText(" Fabian")

    # .setSmallIcon(R.drawable.ic_dialog_info) \
        # Build and show notification
    builder = NotificationCompatBuilder(context, channel_id) \
        .setSmallIcon(context.getApplicationInfo().icon) \
        .setCustomContentView(layout) \
        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
    notification = builder.build()
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    manager = cast(NotificationManagerCompat, notification_service)
    # NotificationManagerCompat.from_(context).notify(1, )
    manager.notify(251, notification)
    print('sent /////////////////////////////////////////////////')


@run_on_ui_thread
def show_custom_notification(title1, title2, message):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationManager = autoclass('android.app.NotificationManager')
    RemoteViews = autoclass('android.widget.RemoteViews')
    NotificationChannel = autoclass('android.app.NotificationChannel')

    # Defaults
    notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
    notification_manager = cast(NotificationManager, notification_service)
    channel_id='default_channel1'
    channel_name='Default Channel 1'
    channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_HIGH)
    if notification_manager.getNotificationChannel(channel_id) is None:
        notification_manager.createNotificationChannel(channel)

    builder = NotificationCompatBuilder(context, channel_id)
    builder.setSmallIcon(context.getApplicationInfo().icon)

    # Create RemoteViews
    resources = context.getResources()
    package_name = context.getPackageName()

    layout_id = resources.getIdentifier("custom_colored_onepart_title", "layout", package_name)
    title_part1_id = resources.getIdentifier("title_part1", "id", package_name)
    title_part2_id = resources.getIdentifier("title_part2", "id", package_name)
    message_id = resources.getIdentifier("message", "id", package_name)
    print('layout_id: ',layout_id, 'title_part1_id: ',title_part1_id,'title_part2_id: ',title_part2_id,'message_id: ',message_id)

    notificationLayout = RemoteViews(package_name, layout_id)

    # Dynamically set texts
    notificationLayout.setTextViewText(title_part1_id, title1)
    notificationLayout.setTextViewText(title_part2_id, title2)
    notificationLayout.setTextViewText(message_id, message)

    # print('notificationLayout: ',notificationLayout)

    builder.setStyle(autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')())
    builder.setCustomContentView(notificationLayout)
    builder.setPriority(autoclass('androidx.core.app.NotificationCompat').PRIORITY_DEFAULT)
    notification_manager.notify(2351+random.randint(0,100), builder.build())

    # notificationLayoutExpanded = RemoteViews(package_name, big)
    # builder.setCustomBigContentView(notificationLayoutExpanded)

from jnius import autoclass
import random
import os

def get_image_uri(relative_path):
    """
    Get the absolute URI for an image in the assets folder.
    :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
    :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
    """
    from android.storage import app_storage_path # type: ignore
    # print("app_storage_path()",app_storage_path())

    output_path = os.path.join(app_storage_path(),'app', relative_path)
    # print(output_path,'output_path')  # /data/user/0/org.laner.lan_ft/files/app/assets/imgs/icon.png

    Uri = autoclass('android.net.Uri')
    return Uri.parse(f"file://{output_path}")

# # Example usage
# image_uri = get_image_uri("imgs/icon.png")
# print(image_uri)

def send_notification(title, message, style=None, img_path=None, channel_id="default_channel"):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: Style of the notification ('big_text', 'big_picture', 'inbox').
    :param image: Image URL or drawable for 'big_picture' style.
    :param channel_id: Notification channel ID.
    """
    # TODO check if running on android short circuit and return message if not
    print('My running....')
    # Get the required Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
    NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
    NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')

    # Get the app's context and notification manager
    context = PythonActivity.mActivity
    notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)

    # Notification Channel (Required for Android 8.0+)
    if notification_manager.getNotificationChannel(channel_id) is None:
        channel = NotificationChannel(
            channel_id,
            "Default Channel",
            NotificationManager.IMPORTANCE_DEFAULT
        )
        notification_manager.createNotificationChannel(channel)

    # Build the notification
    builder = NotificationCompatBuilder(context, channel_id)
    builder.setContentTitle(title)
    builder.setContentText(message)
    builder.setSmallIcon(context.getApplicationInfo().icon)

    
    # Get Image
    img=img_path
    if img_path:
        try:
            img = get_image_uri(img_path)
        except Exception as e:
            print('Failed getting Image path',e)
    
    # Apply styles
    if style == "big_text":
        big_text_style = NotificationCompatBigTextStyle()
        big_text_style.bigText(message)
        builder.setStyle(big_text_style)
    elif style == "big_picture" and img_path:
        try:
            bitmap = BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img))
            builder.setLargeIcon(bitmap)
            big_picture_style = NotificationCompatBigPictureStyle()
            big_picture_style.bigPicture(bitmap).bigLargeIcon(None)
            # big_picture_style.bigLargeIcon(bitmap) # This just changes dropdown app icon
            
            builder.setStyle(big_picture_style)
        except Exception as e:
            print('Failed Adding Bitmap...', e)
    elif style == "inbox":
        inbox_style = NotificationCompatInboxStyle()
        for line in message.split("\n"):
            inbox_style.addLine(line)
        builder.setStyle(inbox_style)

    # Show the notification
    notification_manager.notify(random.randint(0, 100), builder.build())

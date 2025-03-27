print('\nStarting test101 ----------------------------------')
from android_notify import Notification, NotificationStyles
from kivy.clock import Clock
import traceback
Notification.logs=1
import time

try:
    notification = Notification(
        title="Hello",
        # logs=False,
        message="This is a basic notification.",style=''
    )
    notification.send()
    print("test101 passed basic style")
except Exception as e:
    print('test101 Failed Basic Noti',e)
    traceback.print_exc()

print('\nStarting updating Title Notification test101 ----------------------------------')
time.sleep(1)

try:
    notification = Notification(
        title="Failed Test Title didn't change",
        message="Failed Test Title didn't change"
    )
    notification.send()
    notification.updateTitle('New Title')
    print("test101 passed updateTitle")
except Exception as e:
    print('test101 Failed updateTitle',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting updating Message Notification test101 ----------------------------------')

try:
    notification = Notification(
        title="Failed Test Message didn't change",
        message="Failed Test Message didn't change"
    )
    notification.send()
    notification.updateMessage('New Message')
    print("test101 passed updateMessage")
except Exception as e:
    print('test101 Failed updateMessage',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting PROGRESS Style Notification test101 ----------------------------------')

try:
    progress = 0

    noti_progress = Notification(
        title="Downloading...", message="0% downloaded",
        style= NotificationStyles.PROGRESS,
        progress_current_value=0.1,progress_max_value=100
        )
    noti_progress.send()
    print("test101 progress passed")

    def update_progress(dt):
        global progress
        progress = min(progress + 10, 100)
        if progress == 90:
            noti_progress.showInfiniteProgressBar()
            print("test101 passed infinite progress bar")
        else:
            noti_progress.updateProgressBar(progress, f"{progress}% downloaded")

        def removeBar(dt):
            noti_progress.removeProgressBar(message='Test for new PB Msg',title="Download Complete removed progress")
            print("test101 passed removed progress bar")

        if progress >= 100: # Stops when reaching 100%
            Clock.schedule_once(removeBar,5)
        return progress < 100  # Stops when reaching 100%

    Clock.schedule_interval(update_progress, 30*1)
except Exception as e:
    traceback.print_exc()
    print('test101 Failed Progress Noti',e)


time.sleep(1)
print('\nStarting BIG_PICTURE Style Notification test101 ----------------------------------')


try:
    notification = Notification(
        title='Picture Alert!',
        message='This notification includes an image.',
        style=NotificationStyles.BIG_PICTURE,
        big_picture_path="assets/imgs/profile.jpg"
    )
    notification.send()
    print("test101 big picture passed")
except Exception as e:
    print('test101 Failed big_picture Noti',e)
    traceback.print_exc()
    
time.sleep(1)
print('\nStarting LARGE_ICON Style Notification test101 ----------------------------------')
    

try:
    notification = Notification(
        title="FabianDev_",
        message="A twitter about some programming stuff",
        style=NotificationStyles.LARGE_ICON,
        large_icon_path="assets/imgs/profile.jpg"
    )

    notification.send()
    print("test101 large icon passed")
except Exception as e:
    print('test101 Failed large_icon Noti',e)
    traceback.print_exc()
    
time.sleep(1)
print('\nStarting channel_name Notification test101 ----------------------------------')

try:
    notification = Notification(
        title="Download finished",
        message="How to Catch a Fish.mp4",
        channel_name="Download Notifications",  # Will create User-visible name "Download Notifications"
        channel_id="downloads_notifications"  # Optional: specify custom channel 
    )
    notification.send()
    print("test101 passed channel creating test")
except Exception as e:
    print('test101 Failed channel creating test',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting channel_id auto fill Notification test101 ----------------------------------')

try:
    notification = Notification(
        title="Channel Creation finished",
        message="How to Catch a Fish.mp4",
        channel_name="Python Stuff" # Will create User-visible name "Download Notifications"
    
    )
    notification.send()
    print("test101 passed channel creating without ID test")
except Exception as e:
    print('test101 Failed channel creating without',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting Callback Notification test101 ----------------------------------')

try:
    def doSomething():
        print("test101 android-notify printed to Debug Console")

    Notification(title="Hello", message="This is a basic notification.",callback=doSomething).send()
    print("test101 passed attaching function")
except Exception as e:
    print('test101 Failed attaching function',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting identifer Notification test101 ----------------------------------')

try:
    notify = Notification(title="Change Page", message="Click to change App page.", identifer='change_app_page')
    notify.send()
    print("test101 passed attaching identifier")
except Exception as e:
    print('test101 Failed attaching identifier',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting identifer1 Notification test101 ----------------------------------')

try:
    notify1 = Notification(title="Change Colour", message="Click to change App Colour", identifer='change_app_color')
    notify1.send()
    print("test101 passed attaching identifier 1")
except Exception as e:
    print('test101 Failed attaching identifier1',e)
    traceback.print_exc()

time.sleep(1)
print('\nStarting app_icon Notification test101 ----------------------------------')
try:
    Notification(app_icon="assets/imgs/imgx.png",title="Custom Icon",message="Also persist notification test").send(persistent=True)
    print('test101 Custom Successfull')
except Exception as e:
    print('test101 Custom Icon Failed: ',e)
    traceback.print_exc()
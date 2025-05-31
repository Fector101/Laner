"""Android-Notify Tester"""
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from  imports import *
import os.path
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.metrics import sp
from kivy.clock import Clock

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton
import traceback
from kivy.utils import platform # OS
from kivy.core.window import Window

from android_notify import Notification,NotificationStyles,send_notification,NotificationHandler
from typing import Optional

print('deleted channels no: ',Notification.deleteAllChannel())
print('created on enter channel: ',Notification.createChannel('start_id','start','create when entered app'))
print('canceled all notify\'s: ',Notification.cancelAll())
# from utils.helper import makeDownloadFolder

if platform != 'android':
    Window.left=550
    Window.top=0

Notification.logs = True
Builder.load_string("""
<MDTextButton>:
    adaptive_width:True
    MDButtonText:
        id:text_id
        text: root.text
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

<MyMDDropDownItem>:
    id:container
    pos_hint: {"center_x": .5, "center_y": .5}
    MDDropDownItemText:
        id: drop_text
        text: container.text

""")

def createAllRequiredFilesAndFillDefault():
    #/storage/emulated/0/Download/Laner/
    # Create the folder if it doesn't exist
    folder_path = makeDownloadFolder()

    # Create the files with default content
    file_paths = {
        't.txt': 'Test Title',
        'm.txt': 'Test Message',
        'text_lines.txt': 'Test Dance101 Another thing101 last thing',
        'img.txt': '/storage/emulated/0/Download/test.jpg',
        'img1.txt': '/storage/emulated/0/Download/test1.jpg',
        'c.txt': 'Test Channel Name',
        'cd.txt': 'Test Channel Description',
        'icon.txt': '/storage/emulated/0/Download/icon.png'
    }

    for file_name, content in file_paths.items():
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
createAllRequiredFilesAndFillDefault()            

class MyMDDropDownItem(MDDropDownItem):
    text=StringProperty('')
    pass

class AndroidNotifyTester:
    def __init__(self,title='',message=''):
        self.title=title
        self.message=message
        self.progress = 0
        self.notification:Optional[Notification]=None
    def progressBar(self):
        self.notification=Notification(
            title="Downloading...", message="0% downloaded",
            # style=NotificationStyles.PROGRESS,
            progress_current_value=10, progress_max_value=100
        )
        self.notification.send()
        # Clock.schedule_interval(update_progress, 3)# doesn't work for some reason
        Clock.schedule_interval(lambda x: self.update_progress(), 3)

    def update_progress(self):
        self.progress = min(self.progress + 10, 100)
        if self.progress == 90:
            self.notification.showInfiniteProgressBar()
            print("test101 passed infinite progress bar")
        else:
            self.notification.updateProgressBar(self.progress, f"{self.progress}% downloaded")
        def removeBar(_):
            self.notification.removeProgressBar(message='Test for new PB Msg',
                                                title="Download Complete removed progress")
            print("test101 passed removed progress bar")

        if self.progress >= 100:  # Stops when reaching 100%
            Clock.schedule_once(removeBar, 5)
        return self.progress < 100  # Stops when reaching 100%

    def withCallback(self):
        self.notification=Notification(
            title="With Callback", message="This is a basic notification.",
            callback=self.doing_thing
        ).send()
    def persistent(self,title,message):
        Notification(title=title,message=message+' persist').send(persistent=True)
    def withCustomId(self):
        self.notification = Notification(
            title="Custom id", message="Click to change App page.",
            name='change_app_page'
        ).send()
    @staticmethod
    def doing_thing():
        print('Notification clicked Doing thing...')
    def name_attr_big_picture(self, path):
        notify=Notification(
            title=self.title,
            message=self.message,
            name='fabian'
        )
        notify.setBigPicture(path)
        notify.send()
    def channel_name(self,channel_name):
        Notification(
            title=title,
            message=message,
            channel_name=channel_name
        ).send()
    def appIcon(self,path):
        n=Notification(title=self.title,message=self.message)
        n.setSmallIcon(path)
        n.send()
    def appIcon1(self,path):
        Notification(title=self.title,message=self.message,app_icon=path).send()


class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_height = "Custom"
        self.theme_width = "Custom"

class CustomInput(MDBoxLayout):
    text=StringProperty('')
    placeholder=StringProperty('')
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.adaptive_height=True
        self.spacing=13
        self.orientation='vertical'
        self.add_widget(MDLabel(text=self.text,adaptive_width=1,pos_hint={'center_x': .5,'center_y': .5}))
        self.input_widget=MDTextField(text=self.placeholder,pos_hint={'center_x': .5,'center_y': .5}, size_hint=[.8, None], height=sp(60))
        self.add_widget(self.input_widget)

class Laner(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = None
        self.screen = None
        self.run_btn = None
        self.advance_menu_drop_down = None
        self.simple_drop_down = None
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "White"
        self.last_changed_dropdown_widget_text=''
        self.saved_notifications=[]
        self.test_no=0

    def build(self):
        self.title = 'AN-Tester'
        self.screen = MDScreen()
        self.layout =  MDBoxLayout(
            adaptive_height=True,
            orientation='vertical',
            spacing=sp(30),
            pos_hint={'center_y': .5}
        )
        # self.layout.md_bg_color=[1,1,0,1]

        msg=MDLabel(markup=True,text='Use files: t.txt -- title  m.txt -- message\n img.txt -- bigpicture  img1.txt -- largeimg (contains path)\n c.txt -- channel name cd.txt -- channel desc\n icon.txt -- notify icon in Downloads/Laner folder',halign='center',text_color=[0,0.8,0,1])
        msg.padding = [0,0,0,'100sp']
        self.layout.add_widget(msg)

        self.simple_drop_down=MyMDDropDownItem(text='simple',on_release=self.simple_menu)
        self.last_changed_dropdown_widget_text='simple'

        self.advance_menu_drop_down=MyMDDropDownItem(text='no title nd message',on_release=self.advance_menu)

        self.layout.add_widget(self.simple_drop_down)
        self.layout.add_widget(self.advance_menu_drop_down)

        self.run_btn=MDTextButton(text='Send',size=[sp(100),sp(30)],on_release=self.use_android_notify,pos_hint={'center_x': .5})

        self.layout.add_widget(self.run_btn)
        self.screen.add_widget(self.layout)

        return self.screen

    def on_start(self):...

    def on_stop(self):
        print("stopped---------------------")

    def on_pause(self):
        print("on_pause---------------------")
        return True

    def on_resume(self):
        notify_id = NotificationHandler.get_name()
        print('package returned name:',notify_id)
        if notify_id == 'change_app_page':
            # Code to change Screen
            pass
        elif notify_id == 'change_app_color':
            self.layout.md_bg_color = [1, 0, 1, 1]
            # Code to change Screen Color
            pass

    def use_android_notify(self,widget=None):
        self.test_no+=1
        print('\nNew +++++++++++++++++++++++++++++++++ test_no: ',self.test_no)
        download_folder_path = makeDownloadFolder()
        channel_name_path=os.path.join(download_folder_path,'c.txt')
        channel_desc_path=os.path.join(download_folder_path,'cd.txt')

        with open(os.path.join(download_folder_path,'t.txt'), "r", encoding="utf-8") as f:
            title = f.read()
        with open(os.path.join(download_folder_path,'m.txt'), "r", encoding="utf-8") as f:
            message = f.read()
            print('sight: ',message)

        # app icon path
        with open(os.path.join(download_folder_path,'icon.txt'), "r", encoding="utf-8") as f:
            app_icon_path = f.read()

        # big picture path
        with open(os.path.join(download_folder_path,'img.txt'), "r", encoding="utf-8") as f:
            big_img_path= f.read()

        # large icon path
        with open(os.path.join(download_folder_path,'img1.txt'), "r", encoding="utf-8") as f:
            large_icon_path= f.read()

        # inbox text path
        with open(os.path.join(download_folder_path,'text_lines.txt'), "r", encoding="utf-8") as f:
            inbox_msg= f.read()

        style=self.last_changed_dropdown_widget_text

        print('style ',style)
        # style=self.drop_down.ids.drop_text.text

        print('title: ',title, ',message: ',message,',style: ',style)
        try:
            match style:
                case 'simple':
                    def p ():
                        print('Python Stuff Pytho4wf')
                    # 1. Simple notification
                    notification = Notification(
                        title=title,
                        message=message,
                        callback=p
                    )
                    notification.send()
                    self.saved_notifications.append(notification)
                case "progress":
                    # 2. Progress-Bar notification
                    AndroidNotifyTester().progressBar()
                case "big picture with custom id":
                    AndroidNotifyTester(title=title,message=message).name_attr_big_picture(path=big_img_path)
                case "inbox":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title=title,
                        message=message,
                        lines_txt='Line 1\nLine 2\nLine 3',
                        style='inbox'
                    )
                    notification.send()
                    self.saved_notifications.append(notification)
                case "inbox frm file message":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title=title,
                        message=message,
                        lines_txt=inbox_msg.replace('101','\n'),
                        style='inbox'
                    )
                    notification.send()
                    self.saved_notifications.append(notification)
                case "inbox frm method addLine":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title="5 New mails from Frank",
                        message="Check them out",
                    )
                    notification.addLine("Re: Planning")
                    notification.addLine("Delivery on its way")
                    notification.addLine("Follow-up")
                    notification.send()
                    self.saved_notifications.append(notification)
                case "inbox frm method setLines":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title=title,
                        message=message,
                    )
                    lines = inbox_msg.split('101')
                    print('passing this lines: ',lines)
                    notification.setLines(lines)
                    notification.send()
                    self.saved_notifications.append(notification)
                case "large_icon":
                    # 5. Large Icon Image notification
                    notify=Notification(
                        title=title,
                        message=message
                    )
                    notify.setLargeIcon(large_icon_path)
                    notify.send()
                    self.saved_notifications.append(notify)
                case "big_text":
                    # 7. Big text notification (Will Display as simple text if Device doesn't support)
                    notification = Notification(
                        title="Article",
                        message="History of Lorem Ipsum"
                    )
                    notification.setBigText("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever")
                    notification.send()
                    self.saved_notifications.append(notification)
                case "no title nd message":
                    notification = Notification(title='',message='')
                    notification.send()
                    self.saved_notifications.append(notification)
                case "btns":
                    notification = Notification(title=title, message=message)
                    def playVideo():
                        print('Playing Video')

                    def turnOffNoti():
                        print('Please Turn OFf Noti')

                    def watchLater():
                        print('Add to Watch Later')

                    notification.addButton(text="Play",on_release=playVideo)
                    notification.addButton(text="Turn Off",on_release=turnOffNoti)
                    notification.addButton(text="Watch Later",on_release=watchLater)
                    notification.send()
                    self.saved_notifications.append(notification)
                case "btns with large icon":
                    # 6. Notification with Buttons
                    notification = Notification(
                        title=title,
                        message=message
                    )
                    notification.setLargeIcon(large_icon_path)
                    def playVideo():
                        print('Playing Video')

                    def turnOffNoti():
                        print('Please Turn OFf Noti')

                    def watchLater():
                        print('Add to Watch Later')
                    self.saved_notifications.append(notification)
                    notification.addButton(text="Play",on_release=playVideo)
                    notification.addButton(text="Turn Off",on_release=turnOffNoti)
                    notification.addButton(text="Watch Later",on_release=watchLater)
                    notification.send()
                case "big_picture":
                    notify = Notification(
                        title=title,
                        message=message
                    )
                    notify.setBigPicture(big_img_path)
                    self.saved_notifications.append(notify)
                    notify.send()
                case "both_imgs":
                    notification = Notification(
                        title=title,
                        message=message
                    )
                    notification.setLargeIcon(large_icon_path)
                    notification.setBigPicture(big_img_path)
                    notification.send()

                case "custom_icon":
                    AndroidNotifyTester(title=title,message=message).appIcon(app_icon_path)
                case 'custom_icon with arg':
                    AndroidNotifyTester(title=title,message=message).appIcon(app_icon_path)
                case "test title & message update 3s":
                    notification = Notification(
                        title="Failed Test Title didn't change",
                        message="Failed Test Title didn't change"
                    )
                    self.saved_notifications.append(notification)
                    notification.send()
                    def update_title_nd_msg(noti):
                        noti.updateTitle('New Title')
                        noti.updateMessage('New Message')
                    Clock.schedule_once(lambda dt: update_title_nd_msg(notification),3)
                case "Download Channel":
                    notify=Notification(
                        title="Download finished",
                        message="How to Catch a Fish.mp4",
                        channel_name="Download Notifications",  # Will create User-visible name "Download Notifications"
                        channel_id="downloads_notifications"  # Optional: specify custom channel
                    )
                    notify.send()
                    self.saved_notifications.append(notify)
                case "Channel generating id":
                    with open(channel_name_path, "r", encoding="utf-8") as f:
                        channel_name__ = f.read()
                    notify = Notification(
                        title="Channel Creation finished",
                        message="How to Catch a Fish.mp4",
                        channel_name=channel_name__
                    )
                    notify.send()
                    self.saved_notifications.append(notify)
                case 'With name':
                    AndroidNotifyTester().withCustomId()
                case 'With Callback':
                    AndroidNotifyTester().withCallback()
                case 'Custom Channel name':
                    with open(channel_name_path, "r", encoding="utf-8") as f:
                        channel_name__ = f.read()
                    AndroidNotifyTester(title,message).channel_name(channel_name__)
                case "Cancel All":
                    Notification.cancelAll()
                case "Cancel each with loop":
                    for each in self.saved_notifications:
                        each.cancel()
                    self.saved_notifications=[]
                case "Create Channel Method checking id lifespan":
                    # This is basically checking if the same id is being used throughout init to send method
                    with open(channel_name_path, "r", encoding="utf-8") as f:
                        channel_name__ = f.read()

                    with open(channel_desc_path, "r", encoding="utf-8") as f:
                        channel_desc = f.read()

                    channel_id=channel_name__.strip().replace(' ','_')
                    print(channel_id,' ++++ channel id')
                    n=Notification(title='default id with channel desc',message=message,channel_id=channel_id)
                    _=n.createChannel(name=channel_name__, id=channel_id, description=channel_desc)
                    print('returned before send method channel id',_)
                    n.send()
                    print('returned after send method channel id',n.channel_id)
                case "Create Channel Method send two with same ids":
                    # basically checking using same channel id for two notifications
                    with open(channel_name_path, "r", encoding="utf-8") as f:
                        channel_name__ = f.read()

                    with open(channel_desc_path, "r", encoding="utf-8") as f:
                        channel_desc = f.read()

                    # way to use for docs
                    # create cha_id variable and use in different instances create a separate section for channels in site-overview
                    # cha_id ='blah blah'
                    channel_id=channel_name__.strip().replace(' ','_')
                    n = Notification(
                            title='same id passed in only channel name',
                            message="created with one id that was created from channel name",
                            channel_id=channel_id
                    )
                    n.createChannel(id=channel_id,name=channel_name__, description=channel_desc)
                    n.send()

                    n = Notification(
                        title=f'sent with return id: {channel_id}',
                        message="created with one id that was created from channel name", channel_id=channel_id
                    )
                    n.send()

                case "persistent":
                    AndroidNotifyTester().persistent(title,message)
                case "get_active_notifications android6+":
                    Notification().get_active_notifications()
        except Exception as e:
            print('Exception name: ', e)
            print(traceback.format_exc())

    def simple_menu(self, item):
        def menu_btn_callback(text_item):
            self.last_changed_dropdown_widget_text = text_item
            item.ids.drop_text.text = text_item
            self.use_android_notify()
        components=[
                'simple',
                'progress',
                'big_picture',
                'inbox',
                'inbox frm file message',
                'inbox frm method addLine',
                'inbox frm method setLines',
                'large_icon',
                'big_text',
                'btns',
                'both_imgs',
                'custom_icon',
                'custom_icon with arg',
            ]

        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: menu_btn_callback(x),
            } for i in components
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def advance_menu(self,item):

        def menu_btn_callback(text_item):
            self.last_changed_dropdown_widget_text = text_item
            item.ids.drop_text.text = text_item
            self.use_android_notify()
        advanced = [
            'no title nd message',
            'btns with large icon',
            'big picture with custom id',
            "test title & message update 3s",
            "Download Channel",
            "Channel generating id",
            'With name',
            "With Callback",
            "Custom Channel name",
            "Cancel each with loop",
            "Cancel All",
            "Create Channel Method checking id lifespan",
            "Create Channel Method send two with same ids",
            "persistent",
            "get_active_notifications android6+",
        ]
        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: menu_btn_callback(x),
            } for i in advanced
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

if __name__ == '__main__':
    Laner().run()

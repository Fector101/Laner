"""Android-Notify Tester"""


from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.metrics import sp
from kivy.clock import Clock

import time

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton
from jnius import autoclass,cast

from android_notify import Notification,NotificationStyles,send_notification,DataStuff,notificationHandler

Notification.logs = 1
Builder.load_string("""
<MDTextButton>:
    adaptive_width:True
    MDButtonText:
        id:text_id
        text: root.text
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
""")

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

from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
from android.broadcast import BroadcastReceiver
class BecomingNoisyListener:
    def __init__(self, callback):
        # Defaults to NOT listening. Must call start()
        self._br = BroadcastReceiver(self._on_broadcast, actions=["headset_plug"])
        self._callback = callback

    def start(self):
        self._br.start()

    def stop(self):
        self._br.stop()

    def _on_broadcast(self, context, intent):
        extras = intent.getExtras()
        headset_state = bool(extras.get("state"))
        self._callback(headset_state)

class Laner(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "White"
         

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
        self.ids = {}
        input_ids=["style","title", "message", "bigimgpath", "largeiconpath"]
        titles=["Style:","Title:", "Message:", "Big Img path:", "Large Icon path:"]
        placeholders=["","My Title", "Some Message", "assets/icons/might/applications-python.png", "assets/icons/py.png"]

        for i in range(len(titles)):
            widget=CustomInput(text=titles[i],placeholder=placeholders[i])
            self.ids[input_ids[i]]=widget.input_widget
            self.layout.add_widget(widget)

        self.text_input=MDTextButton(text='Send',size=[sp(100),sp(30)],on_release=self.use_android_notify,pos_hint={'center_x': .5})
        self.layout.add_widget(self.text_input)
        self.screen.add_widget(self.layout)

        self.br = BroadcastReceiver(self.on_broadcast, actions=['headset_plug'])


        return self.screen

    def on_broadcast(self, context,intent):
        print('SOme data ',intent)
        extras = intent.getExtras()
        try:
            head_state = bool(extras.get('state'))
            print(head_state)
        except Exception as e:
            print('addeefedv',e)

    def on_new_intent(self, intent):
        data = intent.getData() # perform operations on intent data
        print("New Intent....", data)
        
    def on_start(self):
        current_activity = PythonActivity.mActivity
        self.br.start()

        # register_receiver(current_activity)
    def on_stop(self):
        print("stopped---------------------")
        self.br.stop()
    def on_pause(self):
        print("on_pause---------------------")
        # self.br.stop()
        return True
    def on_resume(self):
        try:...
            # self.br.start()
        except Exception as e:
            print(e,'101010101010')

        print("Resume----------------")
        try:
            Log = autoclass('android.util.Log')
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = cast('android.content.Context', PythonActivity.mActivity)
            Intent = autoclass('android.content.Intent')
            intent = Intent(context, PythonActivity)
            intent_action = intent.getAction()
            extras = intent.getExtras()
            print("NotificationDebug", f"Action: {intent_action}, Extras: {extras}")
            Log.d("NotificationDebug", f"Action: {intent_action}, Extras: {extras}")
        except Exception as e:
            print(e,'GPT')
        # from jnius import cast
        # from jnius import autoclass

        # # import the needed Java class
        # PythonActivity = autoclass('org.kivy.android.PythonActivity')
        # Intent = autoclass('android.content.Intent')
        # Uri = autoclass('android.net.Uri')

        # # create the intent
        # intent = Intent()
        # intent.setAction(Intent.ACTION_VIEW)
        # intent.setData(Uri.parse('http://kivy.org'))

        # # PythonActivity.mActivity is the instance of the current Activity
        # # BUT, startActivity is a method from the Activity class, not from our
        # # PythonActivity.
        # # We need to cast our class into an activity and use it
        # currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        # currentActivity.startActivity(intent)
        self.handle_intent()

    # def on_new_intent(self, intent):
    #     print("New Intent....")
    #     self.handle_intent(intent)

    def handle_intent(self, intent=None):
        try:
            # try:
            #     PythonActivity = autoclass('org.kivy.android.PythonActivity')
            #     currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            #     context = cast('android.content.Context', currentActivity.getApplicationContext())
            #     print('Stack overflow',context)
            # except Exception as e:
            #     print('Error in casting context:', e)
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity

            intent = context.getIntent()
            print("ID data:", intent.getIntExtra("notification_id", -1))
            print("extra data:", intent.getExtra("notification_id"))
            action = intent.getAction()
            print("Action:", action)

            # try:
            #     if action and action.startswith("android.intent.action.ACTION_"):
            #         button_id = intent.getIntExtra("button_id", -1)
            #         print("Button ID:", button_id)
            #         if button_id != -1:
            #             print(f"Button with ID {button_id} clicked")
            #             if button_id in Notification.btns_box:
            #                 Notification.btns_box[button_id]()
            #             else:
            #                 print(f"No handler for button ID {button_id}")
            # except Exception as e:
            #     print('Error in button handling:', e)

            try:
                print("gtgeer --> ", intent.getStringExtra("notification_id"))
            except Exception as e:
                print('didnt gpt 11', e)

            try:
                print("getExtra1 --> ", intent.getExtra("notification_id"))
                print("getExtra1 --> ", intent.getExtra("notification_id"))
            except Exception as e:
                print('didnt work 11', e)

            extras = intent.getExtras()
            if extras:
                try:
                    print("getExtras Cyper--> ", extras.getInt("notification_id"))
                    print("getStringExtra -->", extras.getString("notification_id"))
                except Exception as e:
                    print('Error accessing extras:', e)
            
            notificationHandler(context)

        except Exception as e:
            print('Error in handle_intent:', e)
        # notificationHandler(context)
    def use_android_notify(self,widget):

        style=self.ids['style'].text
        title=self.ids['title'].text
        message=self.ids['message'].text
        big_img_path=self.ids['bigimgpath'].text
        large_icon_path=self.ids['largeiconpath'].text
        # print('title: ',title, ',meassage: ',message,',style: ',style)
        try:
            match style:
                case "":
                    # 1. Simple notification
                    notification = Notification(
                        title=title,
                        message=message,
                        br=self.br
                    )
                    notification.send()
            
                case "progress":
                    # 2. Progress-Bar notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="progress",
                        progress_max_value=100,
                        progress_current_value=0
                    )
                    notification.send()
                    Clock.schedule_once(lambda dt: notification.updateProgressBar(30, "30% downloaded"), 6)
                    Clock.schedule_once(lambda dt: notification.removeProgressBar(message=message), 6)
                case "big_picture":
                    # 3. Big Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="big_picture",
                        big_picture_path=big_img_path
                    )
                    notification.send()
                case "inbox":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title=title,
                        message=message,
                        style='inbox'
                    )
                    notification.send()
                case "large_icon":
                    # 5. Large Icon Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="large_icon",
                        large_icon_path=large_icon_path
                    )
                    notification.send()
                case "big_text":
                    # 7. Big text notification (Will Display as simple text if Device dosen't support)
                    notification = Notification(
                        title=title,
                        message=message,
                        style="big_text"
                    )
                    notification.send()
                case "gpt":
                    # 6. Notification with Buttons
                    DataStuff()
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
                case "btnsi":
                    # 6. Notification with Buttons
                    notification = Notification(
                        title=title,
                        message=message,
                        style="large_icon",
                        large_icon_path=large_icon_path
                    )
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
                case "1":
                    Notification(
                        title="New Photo",
                        message="Check out this image",
                        style=NotificationStyles.BIG_PICTURE,
                        big_picture_path=big_img_path
                    ).send()
                case "both_imgs":
                    # 5. Large Icon Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="both_imgs",
                        large_icon_path=large_icon_path,
                        big_picture_path=big_img_path
                    )
                    notification.send()
        except Exception as e:
            print(e, "Package Error 101")
    def on_new_intent(self, intent):
        print("New Intent....")
        self.handle_intent(intent)

if __name__ == '__main__':
    Laner().run()
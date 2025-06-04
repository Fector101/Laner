from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.uix.list import MDListItem,MDListItemTrailingIcon, MDListItemHeadlineText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
# from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarSupportingText,MDSnackbarButtonContainer,MDSnackbarActionButton,MDSnackbarActionButtonText,MDSnackbarCloseButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogSupportingText,MDDialogContentContainer
from kivy.properties import StringProperty, ObjectProperty, Clock
from kivymd.uix.widget import MDWidget
from kivy.metrics import sp

from .templates import MDTextButton
from utils import Settings

from kivy.utils import platform
if platform == 'android':
    from kivymd.toast import toast


class PopupScreen:
    """call close method in child class to close popup"""
    def __init__(self,close_btn_callback=None,bottom_navigation_bar=None):
        self.close_btn_callback=close_btn_callback
        # setting `self.parent=None` here because of pycharm
        self.parent=None # parent DisplayFolderScreen Class
        self.bottom_navigation_bar=bottom_navigation_bar

    def close(self,widget=None):
        if self.close_btn_callback:
            self.close_btn_callback()
        self.parent.current_popup=None
        self.parent.enable_click()
        self.parent.remove_widget(self)
        if self.bottom_navigation_bar:
            self.bottom_navigation_bar.open()

    def on_parent(self,instance,parent):
        # This will call when widget is mounted and removed
        if parent: # when unmounted parent = None
            print(self)
            parent.disable_click(popup=self)
        if self.bottom_navigation_bar:
            self.bottom_navigation_bar.close()


class PopupDialog(MDWidget):
    caption=StringProperty()
    sub_caption=StringProperty()
    cancel_txt=StringProperty()
    confirm_txt=StringProperty()
    failedCallBack=ObjectProperty()
    successCallBack=ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color=self.theme_cls.backgroundColor
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Laner",
                markup=True,
                halign="left",
            ),
            
            MDDialogContentContainer(
            MDDialogSupportingText(
                text=self.caption,
                # halign="left",
            ),
            MDDialogSupportingText(
                text=self.sub_caption,
                # halign="left",
            ),
            orientation='vertical',
            ),
            
            MDDialogButtonContainer(
                Widget(),
                self._button(txt=self.cancel_txt,on_release=lambda x:self.cancel()),
                self._button(txt=self.confirm_txt,on_release=lambda x:self.ok()),
                spacing="8dp",
            ),
        )
        self.dialog.open()
        self.dialog.update_width()
    def _button(self,txt,on_release):
        return MDButton(MDButtonText(text=txt),
                    style="text",
                    on_release=on_release,
                )
    def ok(self):
        self.successCallBack()
        self.close()
    def cancel(self):
        self.failedCallBack()
        self.close()
        
    def close(self):
        self.dialog.dismiss()


class Snackbar(MDWidget):
    # h1=StringProperty()
    # caption=StringProperty()
    # cancel_txt=StringProperty()
    # confirm_txt=StringProperty('')
    # failedCallBack=ObjectProperty()
    # successCallBack=ObjectProperty()
    # font_size=sp(16)
    def __init__(self,h1,confirm_txt='',font_size=sp(16), **kwargs):
        super().__init__(**kwargs)
        self.snackbar = MDSnackbar(
            MDSnackbarSupportingText(
                text=h1,
                font_size=font_size,
                theme_text_color="Custom",
                text_color=(0, 40/255, 0, 1)
            ),
            
            y=sp(80),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            padding=[0,0,sp(5),0],
            background_color=(.85, .95, .88, .9)
        )
        buttons_container = MDSnackbarButtonContainer(pos_hint={"center_y": 0.5})
        if confirm_txt:
            buttons_container.add_widget(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text=confirm_txt,
                        theme_text_color="Custom",
                        text_color=(0, 40/255, 0, 1)
                    ),
                    # on_release=lambda x: self.snackbar.dismiss()
                )
            )
        buttons_container.add_widget(
            MDSnackbarCloseButton(
                icon="close",
                theme_icon_color="Custom",
                icon_color=(0.2, 40/255, 0.3, 1),
                on_release=lambda x: self.snackbar.dismiss()
            )
        )
        self.snackbar.add_widget(buttons_container)
        self.snackbar.open()

class MYMDListItemTrailingIcon(ButtonBehavior,MDListItemTrailingIcon):
    pass

class BookMarkedFolders(MDBoxLayout):
    """
    State attr managed if it's open for other widgets
    """
    def __init__(self,width,x,y,**kwargs):
        super().__init__(**kwargs)
        self.app=MDApp.get_running_app()

        self.state = False
        self.orientation='vertical'
        self.md_bg_color=[.21, 0.21, .31, 1]
        self.size_hint_x = None
        self.width = width
        self.pos = [x, y]
        self.adaptive_height=True
        self.max_height = Window.height/2
        self.refresh()

    def adjust_height(self,children_len):

        if children_len*40 > self.max_height:
            self.adaptive_height=False
            self.size_hint_y=None
            self.height = sp(self.max_height)
        elif children_len == 0:
            self.height = 40
        else:
            self.adaptive_height = True



    def refresh(self):
        self.clear_widgets()
        marked_folders = Settings().get_with_two_keys(key="bookmark_paths", sub_key='paths') or []
        each: str
        layout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for each in marked_folders:
            if len(marked_folders) * 40 >= self.max_height:
                # Make sure the height is such that there is something to scroll.
                btn = self.button(text=each)
                layout.add_widget(btn)
            else:
                self.add_widget(self.button(each))

        if len(marked_folders) *40 > self.max_height:
            root = ScrollView(size_hint=(1, None), size=(Window.width, self.max_height))
            root.add_widget(layout)
            self.add_widget(root)
        self.adjust_height(len(marked_folders))

    def on_parent(self,instance,parent):
        if parent: # when unmounted parent = None
            self.state= True
        else:
            self.state = False
        self.refresh()

    def button(self,text):
        icon = MYMDListItemTrailingIcon(
                icon="trash-can-outline",
            )
        icon.on_release=lambda : self.removePathFromBookMarks(text)
        item = MDListItem(

            MDListItemHeadlineText(
                text=text,
                shorten_from='left',
            ), icon,
        )
        item.on_release=lambda :self.openPath(text)
        return item

    def openPath(self,text):
        self.app.my_screen_manager.current_screen.set_folder(path=text,add_to_history=True)
        self.close()

    def removePathFromBookMarks(self,text):
        res=Settings().remove_frm_list_with_two_keys('bookmark_paths', 'paths', text)
        toast(res['msg'])
        self.refresh()
        # if not Settings().get_with_two_keys(key="bookmark_paths", sub_key='paths'):
        #     self.close()

    def close(self,widget=None):
        self.state=False
        self.parent.remove_widget(self)

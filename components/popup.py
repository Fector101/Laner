from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarSupportingText,MDSnackbarButtonContainer,MDSnackbarActionButton,MDSnackbarActionButtonText,MDSnackbarCloseButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogSupportingText,MDDialogContentContainer
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.widget import MDWidget
from kivy.metrics import sp


class PopupScreen:
    def __init__(self,close_btn_callback,bottom_navigation_bar):
        self.close_btn_callback=close_btn_callback
        # Setting `self.parent=None` here cause of pycharm
        self.parent=None # parent DisplayFolderScreen Class
        self.bottom_navigation_bar=bottom_navigation_bar

    def close(self,widget=None):

        self.close_btn_callback()
        self.parent.enable_click()
        self.parent.remove_widget(self)
        self.bottom_navigation_bar.open()

    def on_parent(self,instance,parent):
        # This will call when widget is mounted and removed
        if parent: # when unmounted parent = None
            parent.disable_click(popup=self)
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
        
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarSupportingText,MDSnackbarButtonContainer,MDSnackbarActionButton,MDSnackbarActionButtonText,MDSnackbarCloseButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogSupportingText
from kivy.properties import ( StringProperty, ObjectProperty)
from kivymd.uix.widget import MDWidget
from kivy.metrics import dp,sp

class PopupDialog(MDWidget):
    h1=StringProperty()
    caption=StringProperty()
    cancel_txt=StringProperty()
    confirm_txt=StringProperty()
    failedCallBack=ObjectProperty()
    successCallBack=ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color=self.theme_cls.backgroundColor
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=self.h1,
                markup=True,
                halign="left",
            ),
            MDDialogSupportingText(
                text=self.caption,
                halign="left",
            ),
            MDDialogButtonContainer(
                Widget(),
                self._button(txt=self.cancel_txt,on_release=lambda x:self.cancel()),
                self._button(txt=self.confirm_txt,on_release=lambda x:self.ok()),
                spacing="8dp",
            ),
        )
        # self.dialog.adaptive_size=True
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
    h1=StringProperty()
    # caption=StringProperty()
    # cancel_txt=StringProperty()
    confirm_txt=StringProperty('')
    # failedCallBack=ObjectProperty()
    # successCallBack=ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snackbar = MDSnackbar(
            MDSnackbarSupportingText(
                text=self.h1 or "Saved",
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
        if self.confirm_txt:
            buttons_container.add_widget(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text=self.confirm_txt,
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
        
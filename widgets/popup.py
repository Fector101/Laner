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
                halign="left",
            ),
            MDDialogSupportingText(
                text=self.caption,
                halign="left",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text=self.cancel_txt),
                    style="text",
                    on_release=lambda x: self.cancel(),
                ),
                MDButton(
                    MDButtonText(text=self.confirm_txt),
                    style="text",
                    on_release=lambda x: self.ok(),
                ),
                spacing="8dp",
                
            ),
        )
        self.dialog.open()
        self.dialog.update_width()

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
            MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text=self.confirm_txt,
                        theme_text_color="Custom",
                        text_color=(0, 40/255, 0, 1)
                    ),
                        # theme_bg_color="Custom",
                    
                        # md_bg_color=
                ),
                MDSnackbarCloseButton(
                    icon="close",
                    # theme_text_color="Custom",
                    theme_icon_color="Custom",
                    icon_color=(0.2, 40/255, 0.3, 1),
                    on_release=lambda _:self.snackbar.dismiss()
                ),
                pos_hint={"center_y": 0.5}
            ),
            y=sp(80),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            background_color=(.85, .95, .88, .9)
        )
        self.snackbar.open()

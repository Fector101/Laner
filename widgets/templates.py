import os
import asynckivy

from kivy.properties import BooleanProperty,StringProperty
from kivy.metrics import dp,sp
from kivy.lang import Builder
from kivymd.uix.bottomsheet.bottomsheet import MDBottomSheet,MDBottomSheetDragHandle,MDBottomSheetDragHandleTitle,MDBottomSheetDragHandleButton
from kivymd.uix.button import MDButton, MDButtonText,MDButtonIcon,MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from widgets.popup import PopupDialog,Snackbar
from workers.helper import getAppFolder

with open(os.path.join(getAppFolder(),"widgets","templates.kv"), encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="MyBtmSheet.kv")



class TypeMapElement(MDBoxLayout):
    selected = BooleanProperty(False)
    icon = StringProperty()
    title = StringProperty()
    
    def set_active_element(self, instance, type_map):
        # print(self.parent.children, instance, type_map)
        for element in self.parent.children:
            if instance == element:
                element.selected = True
                self.current_map = type_map
            else:
                element.selected = False

class MyBtmSheet(MDBottomSheet):
    sheet_type="standard"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super(MyBtmSheet,self).__init__(**kwargs)
        self.size_hint_y=None
        self.height=sp(170)
        
        self.drag_sheet= MDBottomSheetDragHandle(
                            
                            
                            # drag_handle_color= "grey"
                            )
        self.drag_sheet.add_widget(
            MDBottomSheetDragHandleTitle(
                # text= "Select type map",
                pos_hint= {"center_y": .5}
            )
        )
        self.drag_sheet.add_widget(
            MDBottomSheetDragHandleButton(
                               icon= "close",
                               ripple_effect= False,
                               on_release= lambda x: self.set_state("toggle")
                               )
        )

        self.content = MDBoxLayout(padding=[0, 0, 0, "16dp"])
        self.add_widget(self.drag_sheet)
        self.add_widget(self.content)
        self.enable_swiping=0
        # self.generate_content()
        # self.set_state('close')
        # self.on_open=asynckivy.start(self.generate_content())
        
    async def generate_content(self):        
        
        icons = {
            "Download": "download",
            "Open with": "apps",
            "Share": "share",
        }
        map_sources = {
        "street": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "sputnik": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        }
        # await asynckivy.sleep(0)
        # print("test----|",self,'|||',self.content)
        # print(self.content.children)
        if not self.children:
            for i, title in enumerate(icons.keys()):
                await asynckivy.sleep(0)
                self.content.add_widget(
                    TypeMapElement(
                        title=title.capitalize(),
                        icon=icons[title],
                        selected=not i,
                    )
                )
    def on_touch_move(self, touch):
        if self.enable_swiping:
            if self.status == "opened" and abs(touch.y - touch.oy) > self.swipe_distance:
                self.status = "closing_with_swipe"

        if self.status == "closing_with_swipe":
            self.open_progress = max(
                min(
                    self.open_progress
                    + (touch.dy if self.anchor == "left" else -touch.dy)
                    / self.height,
                    1,
                ),
                0,
            )
            return True
        return super().on_touch_move(touch)
    def on_close(self, *args):
        self.enable_swiping=0
        return super().on_close(*args)
        

class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    # text_widget = ObjectProperty() # for on_text if statement to work
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.text = self.text
        self.theme_height = "Custom"
        self.theme_width = "Custom"
    
class CustomDropDown(MDBoxLayout):
    title = StringProperty("Advanced Options")
    
    is_open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.not_keeps_sake=[]

    def toggle_dropdown(self):
        if self.is_open:
            self.ids.dropdown_content.clear_widgets()
        else:
            for each in self.not_keeps_sake:
                self.ids.dropdown_content.add_widget(each)
            
        self.is_open = not self.is_open

    def add_widget(self, widget, index=0, canvas=None):
        if self.ids and 'dropdown_content' in self.ids:
            self.not_keeps_sake.append(widget)
            if self.is_open:
                self.ids.dropdown_content.add_widget(widget)
        else:
            super().add_widget(widget, index=index, canvas=canvas)        
            
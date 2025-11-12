import os
import asynckivy

from kivy.properties import BooleanProperty,StringProperty,ObjectProperty
from kivy.metrics import dp,sp
from kivy.lang import Builder
from kivymd.uix.bottomsheet.bottomsheet import MDBottomSheet,MDBottomSheetDragHandle,MDBottomSheetDragHandleTitle,MDBottomSheetDragHandleButton
from kivymd.uix.button import MDButton, MDButtonText,MDButtonIcon,MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import platform # OS

from utils.helper import getAppFolder

with open(os.path.join(getAppFolder(),"ui","components","templates.kv"), encoding="utf-8") as kv_file:
    Builder.load_string(kv_file.read(), filename="MyBtmSheet.kv")


from kivymd.uix.list import MDListItem, MDListItemHeadlineText
class TypeMapElement(MDBoxLayout):
    selected = BooleanProperty(False)
    icon = StringProperty()
    title = StringProperty()
    func = ObjectProperty()
    def on_touch_up(self,touch):
        self.parent.parent.hide(False) # Closes MDBOttomSheet
        return super().on_touch_up(touch)
        
class MyBtmSheet(MDBottomSheet):
    sheet_type="standard"
    items=[]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super(MyBtmSheet,self).__init__(**kwargs)
        self.size_hint_y=None
        self.height=sp(410 if platform == 'android' else 340)
        self.drag_sheet= MDBottomSheetDragHandle(
                                                    # drag_handle_color= "grey" 
                                                 )
        self.sheet_title = MDBottomSheetDragHandleTitle(
                text= "Passed_in_Selected_File/Folder_Name",
                pos_hint= {"center_y": .5},
                adaptive_height=True,
                shorten_from='right',
                shorten=True,
                
            )
        self.drag_sheet.add_widget(self.sheet_title)
        self.drag_sheet.add_widget(
            MDBottomSheetDragHandleButton(
                               icon= "close",
                               ripple_effect= False,
                               on_release= lambda x: self.set_state("close")
                               )
        )

        self.content = MDBoxLayout(padding=[0, 0, 0, 0 ],orientation="vertical")
        self.add_widget(self.drag_sheet)
        self.add_widget(self.content)
        self.enable_swiping=0
        # self.set_state('close')
        
        self.bind(on_open=self.generate_content)
    
    def generate_content(self,arg):
        
        # {
        #     "Preview": "eye",
        #     "Download": "download",
        #     "Open with": "apps",
        #     "Share": "share",
        # }
        # await asynckivy.sleep(0)
        # print("test----|",self,'|||',self.content)
        # print(self.children)
        if self.children:
            for each_item in self.items:
                self.content.add_widget(
                    TypeMapElement(
                        title=each_item['title'].capitalize(),
                        icon=each_item['icon'],
                        func=each_item['function']
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
        # return super().on_touch_move(touch)
    def on_close(self, *args):
        self.enable_swiping=0
        return super().on_close(*args)
    def show(self,file_name,items_object:dict):
        self.content.clear_widgets()
        self.items=items_object
        self.sheet_title.text=file_name
        self.enable_swiping=True
        self.set_state("toggle")
    def hide(self,animation=True):
        self.set_state('close',animation=animation)
        
class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    # text_widget = ObjectProperty() # for on_text if statement to work

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.text = self.text
        # print(self.adaptive_width)
        self.theme_height = "Custom"
        self.theme_width = "Primary" if self.adaptive_width else "Custom"
    
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

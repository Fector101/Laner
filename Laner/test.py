from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

KV = '''
MDScreen:

    MDRaisedButton:
        id: button
        text: "Press me"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.menu_open()
'''


class Test(MDApp):
    def menu_open(self):
        menu_items = [
            {
                "text": f"Item {i}",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        MDDropdownMenu(
            caller=self.root.ids.button, items=menu_items
        ).open()

    def menu_callback(self, text_item):
        print(text_item)

    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)
     
    def renderPath(self):
        list_of_path_info=self.current_dir_info
        import time
        start_timer=time.time()
        
        self.screen_scroll_box.clear_widgets() # If Widget not already added it won't cause can error
        
        elapsed_timer=time.time() - start_timer
        print(f'Done in {elapsed_timer} seconds --1')
        def myFormat(text:str):
            if len(text) > 20:
                return text[0:18] + '...'
            return text.capitalize()
        
        self.cur_dir_elements = MyScrollBox_ChildernContainer(cols=4, spacing=18, size_hint_y=None,padding=dp(10))
        # Make sure the height is such that there is something to scroll.
        self.cur_dir_elements.bind(minimum_height=self.cur_dir_elements.setter('height'))
        
        start_timer=time.time()
        
        for each in list_of_path_info:# ("elevated", "filled", "outlined"):
              
            self.cur_dir_elements.add_widget(
                MyCard(
                    MDRelativeLayout(
                        FitImage(
                        source=each['icon'],
                        size_hint=[.9,.7],
                        fit_mode='contain',  #['scale-down', 'fill', 'contain', 'cover']
                        mipmap=True,
                        pos_hint={"top":1},
                        radius=(dp(5),dp(5),0,0),
                        
                        
                    ),
                        MDButton(
                            MDButtonIcon(
                                icon="download",
                                pos_hint={'x':.19,'y':.17},
                                theme_icon_color="Custom",
                                icon_color=[1,1,1,1],
                            ),
                            theme_bg_color= "Custom",
                            theme_height= "Custom",
                            theme_width= "Custom",
                            radius='15sp',
                            size_hint= [None, None],
                            width= '32sp',
                            height='32sp',
                            md_bg_color=[.7,.6,.9,1],
                            pos_hint={"top": .979, "right": .97},
                        ),
                        MDLabel(
                            text=myFormat(each['name']),
                            # shorten_from='center',
                            font_size='11sp',
                            theme_font_size= "Custom",
                            text_color=[1,1,1,1],
                            height='40sp',
                            size_hint=[1,None]
                        ),
                        md_bg_color=[0,0,0,0]
                    ),
                    style='filled',
                    size_hint=(.5, None),
                    height='140sp',
                    radius=dp(5),theme_bg_color="Custom",
                    md_bg_color=[1,0,0,0],
                    # TODO attach on_release outside add_widget so i can add event only when it's a folder not a file,
                    # (i.e TODO Create a custom CARD Class or find a where to add label id and use that Card.ids.label_id.on_release = function)
                    on_release=lambda item_self_prop__,current_file_path=each['path']: self.setPath(current_file_path)
                )
            )
        elapsed_timer=time.time() - start_timer
        print(f'Done in {elapsed_timer} seconds --2')
        
        self.screen_scroll_box.add_widget(self.cur_dir_elements)
        
        # self.layout.remove_widget(self.screen_scroll_box)
        # self.layout.add_widget(self.screen_scroll_box)
        

Test().run()






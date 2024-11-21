from kivymd.app import MDApp
from webview import WebView
from kivy.lang.builder import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen

Builder.load_string("""
<MyWebView>
    MDFlatButton:
        text: "Push"
        pos_hint: {"center_x": .5, "center_y": .4}
        on_press: root.Push()
""")

class MyWebView(MDScreen):
    def Push(self):
        WebView("https://www.google.com")


class MyWebApp(MDApp):
    def build(self):
        return MyWebView()


if __name__ == '__main__':
    MyWebApp().run()
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty, StringProperty

Builder.load_string('''
<StatefulLabel>:
    active: stored_state.active
    CheckBox:
        id: stored_state
        active: root.active
        on_release: root.store_checkbox_state()
    Label:
        text: root.text
    Label:
        id: generate_state
        text: root.generated_state_text

<RV>:
    viewclass: 'StatefulLabel'
    RecycleBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
''')

class StatefulLabel(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    generated_state_text = StringProperty()
    active = BooleanProperty()
    index = 0

    '''
    To change a viewclass' state as the data assigned to it changes,
    overload the refresh_view_attrs function (inherited from
    RecycleDataViewBehavior)
    '''
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        if data['text'] == '0':
            self.generated_state_text = "is zero"
        elif int(data['text']) % 2 == 1:
            self.generated_state_text = "is odd"
        else:
            self.generated_state_text = "is even"
        super(StatefulLabel, self).refresh_view_attrs(rv, index, data)

    '''
    To keep state changes in the viewclass with associated data,
    they can be explicitly stored in the RecycleView's data object
    '''
    def store_checkbox_state(self):
        rv = App.get_running_app().rv
        rv.data[self.index]['active'] = self.active

class RV(RecycleView, App):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x), 'active': False} for x in range(100)]
        App.get_running_app().rv = self

    def build(self):
        return self

if __name__ == '__main__':
    RV().run()

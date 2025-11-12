# Werid typing for autocomplete
from ui.components import BottomNavigationBar
from ui.components.templates import MyBtmSheet
from utils import Settings


# Avoiding Circular Import Error
class Laner:
    bottom_navigation_bar=BottomNavigationBar
    btm_sheet = MyBtmSheet
    settings = Settings

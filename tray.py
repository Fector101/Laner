import threading
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

# from workers.helper import getAppFolder

app = QApplication([]) 
app.setQuitOnLastWindowClosed(False) 

# Adding an icon 
import os
icon_path="./icon.png"#os.path.join(getAppFolder(),"assets","imgs","icon.png") 
print(icon_path)
print(os.getcwd())
icon = QIcon(icon_path)
print(icon)
# Adding item on the menu bar 
tray = QSystemTrayIcon() 
tray.setIcon(icon) 
tray.setVisible(True) 

# Creating the options 
menu = QMenu() 
option1 = QAction("Quick Connect") 
option2 = QAction("Show Code") 
def startApp():
    from desktop_version import FileShareApp
    FileShareApp().run()
    
    
    
option2.triggered.connect(startApp) 
option3 = QAction("End Connection") 
menu.addAction(option1) 
menu.addAction(option2) 
menu.addAction(option3)

# To quit the app 
quit = QAction("Quit") 
quit.triggered.connect(app.quit) 
menu.addAction(quit) 

# Adding options to the System Tray 
tray.setContextMenu(menu) 




if __name__ == '__main__':
    # server_thread = threading.Thread(target=startApp)
    # server_thread.daemon = True
    # server_thread.start()
    app.exec_()
    
# from desktop_version import windowShow
# # from desktop_version import FileShareApp,windowShow
# def start():
#     windowShow()    
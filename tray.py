import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction

# You'll need to define the showApp function first
def showApp():
    # Add code to show your main window
    # For example, if you have a main window called 'window':
    window.show()

# Create the application
app = QApplication([])
app.setQuitOnLastWindowClosed(False)

# Path to your icon
icon_path = "./icon.png"

# Create the system tray icon
tray = QSystemTrayIcon()
tray.setIcon(QIcon(icon_path))
tray.setVisible(True)

# Create the menu
menu = QMenu()

# Add menu options
option1 = QAction("Quick Connect", parent=menu)
option2 = QAction("Show Code", parent=menu)
option2.triggered.connect(showApp)  # Connect to show app function
option3 = QAction("End Connection", parent=menu)

# Add actions to menu
menu.addAction(option1)
menu.addAction(option2)
menu.addAction(option3)

# Add quit option
quit_action = QAction("Quit", parent=menu)
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)

# Set context menu for tray
tray.setContextMenu(menu)

# Create your main window (this is an example, replace with your actual window)
from PyQt5.QtWidgets import QMainWindow
window = QMainWindow()
window.setWindowTitle("Your App")

# Fix indentation and add main block
if __name__ == '__main__':
    app.exec_()
    
#     # server_thread = threading.Thread(target=app.exec_)
#     # server_thread.daemon = True
#     # server_thread.start()
#     # startApp()
    
#     # server_thread = threading.Thread(target=startApp)
#     # server_thread.daemon = True
#     # server_thread.start()
    
# # from desktop_version import windowShow
# # # from desktop_version import FileShareApp,windowShow
# # def start():
# #     windowShow()    


# def startApp():
#     from desktop_version import FileShareApp,Window
#     sFileShareApp().run()
    
    
# def showApp():
#     from desktop_version import Window
#     Window.show()
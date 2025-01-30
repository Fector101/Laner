from jnius import autoclass
print("Button Service is running... python")

# Android classes
Context = autoclass('android.content.Context')
AndroidString = autoclass('java.lang.String')
service = autoclass('org.kivy.android.PythonService').mService
context = service.getApplication().getApplicationContext()

# Get Action
intent = service.getIntent()
action = intent.getAction()
print("Action: ", action)


service.stopForeground()

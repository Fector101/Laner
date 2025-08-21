from kivy.utils import platform # OS
from kivy.clock import Clock

class Intent:
    def __init__(self,context,activity='old'):
        pass
    def setData(uri_parsed):
        pass

class MActivity:
    def getPackageName(self):
        return 'package:org.laner.lan_ft'
    def startActivity(self,intent:Intent):
        pass
class Environment:
    def isExternalStorageManager(self):
        return True
class Uri:
    def parse(self,package_name):
        return ''    

if platform == 'android':
    from android import mActivity
    from android import api_version  # type: ignore
    from jnius import autoclass
    from kivymd.toast import toast
    from android.permissions import request_permissions, Permission,check_permission
    from android.storage import app_storage_path, primary_external_storage_path
    Environment = autoclass('android.os.Environment')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
else:
    mActivity=MActivity()
    app_storage_path=''
    primary_external_storage_path=''
    

# def requestMultiplePermissions():
#
# 	print('Asking permission...')
# 	def check_permissions(permissions):
# 		for permission in permissions:
# 			if check_permission(permission) != True:
# 				return False
# 		return True
#
#
# 	def request_all_permission():
# 		def on_permissions_result(permissions, grants):
# 			print('What grants is ---->',grants)
# 			if Permission.POST_NOTIFICATIONS in permissions and not grants[permissions.index(Permission.POST_NOTIFICATIONS)]:
# 				print("Notification permission denied")
# 			storage_permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
# 			request_permissions(storage_permissions, on_storage_permissions_result)
#
#         # Request notification permission first
# 		request_permissions([Permission.POST_NOTIFICATIONS], on_permissions_result)
#
# 	try:
# 		request_all_permission()
# 	except Exception as e:
# 		print(f"Failed to request permissions: {e}")

class PermissionHandler:
    def __init__(self):
        # Check if any permission is denied and show a prompt with info for the user to allow or cancel.
        pass
    
    def requestStorageAccess(self):
        """Requests access to storage.  
        - If Android 11+, requests 'All Files Access'.  
        - Otherwise, requests storage read and write permissions.
        """
        if api_version >= 30:
            self.requestAllFilesAccess()
        else:
            self.requestReadWriteAccess()
            
    def requestAllFilesAccess(self):
        """Requests 'All Files Access' permission for Android 11+"""
        if not Environment.isExternalStorageManager():
            try:
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                print(f"package:{mActivity.getPackageName()}")
                intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}"))
                Clock.schedule_once(lambda dt: mActivity.startActivity(intent), 2)
            except Exception as e:
                print('PermissionHandler.requestAllFilesAccess --> ', e)
                Clock.schedule_once(lambda dt: toast("Failed to request storage permissions"), 2)

    def requestReadWriteAccess(self):
        """Requests storage read and write permissions."""
        permission_fail_msgs = {
            Permission.READ_EXTERNAL_STORAGE: "Rejected access to Read Storage",
            Permission.WRITE_EXTERNAL_STORAGE: "Rejected access to Write Storage"
        }
        storage_permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
        request_permissions(storage_permissions, lambda p, g: self.handlePermissionResult(p, g, permission_fail_msgs))
        print("Storage permissions not called Android < 11 | Feature not available 101")

    def handlePermissionResult(self, permissions: list, grants: list, fail_msgs: dict):
        """
        Handles the result of a permission request.

        Args:
            permissions (list): List of requested permissions.
            grants (list): List of granted permissions.
            fail_msgs (dict): Dictionary mapping permissions to failure messages.
        """
        for permission in permissions:
            if permission not in grants:
                txt = fail_msgs.get(permission, "Permission denied")
                Clock.schedule_once(lambda dt: toast(txt), 2)

    def requestNotificationAccess(self):
        """Requests notification permission."""
        request_permissions([Permission.POST_NOTIFICATIONS], lambda p, g: self.handlePermissionResult(p, g, {'POST_NOTIFICATIONS': 'Rejected access to notifications'}))

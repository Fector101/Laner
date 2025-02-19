# import os
# import requests
# import traceback
# from android_notify import Notification, NotificationStyles
# # Notification
# def download_file(self, file_path,save_path,success,failed=None):
#     try:
#         url = f"http://{self.get_server_ip()}:{self.get_port_number()}/{file_path}"

#         response = requests.get(url)
#         file_name = os.path.basename(save_path)
#         print("This is file name: ", file_name)
#         print("This is save_path: ", save_path)
#         with open(save_path, "wb") as file:
#             file.write(response.content)
#         self.on_ui_thread(success)
#     except Exception as e:
#         print("Error Download Service error-type: ",e)
#         traceback.print_exc()
#         self.on_ui_thread(failed)
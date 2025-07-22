"""
# This script extracts the icon from an executable file (EXE) and saves it as a PNG image.
# It uses the icoextract library to handle the extraction.
# icoextract dependencies: pefile
"""
import os, traceback,sys

from icoextract import IconExtractor
from PIL import Image

if __name__=='executable' or __name__=='__main__':
    from testing.helper import gen_unique_filname, getAppFolder,urlSafePath
    from testing.sword import NetworkManager,NetworkConfig
    from os.path import join as _joinPath

else:
    from workers.helper import gen_unique_filname, _joinPath, getAppFolder,urlSafePath
    from workers.sword import NetworkManager,NetworkConfig

# Global exception handler to catch all unhandled exceptions
def global_exception_handler(exc_type, exc_value, exc_traceback):
    # Default traceback print
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    # Custom line after every exception
    print(f'------------------------{exc_type.__name__} Log end------------------------')

# Set the global exception handler
sys.excepthook = global_exception_handler

# Custom exception for icon extraction errors
# This will be raised if the icon extraction fails for any reason
class IconExtractionError(Exception):
    """Custom exception for icon extraction errors."""
    def __init__(self, message,*args):
        super().__init__(message)
        print(f'\n------------------------{self.__class__.__name__} Log start------------------------')
        self.message = message
        # self.args = args # don’t need self.args = args — super().__init__() already stores the message in .args.


class ExecutableIconExtractor:
    """Class to handle extraction of icons from executable files."""
    
    

    def __init__(self, exe_path: str, server_ip: str=NetworkConfig.server_ip,port: int=NetworkConfig.port):
        self.__preview_folder = os.path.join(getAppFolder(), 'preview-imgs')
        self.__exe_path = exe_path
        self.__icon_path = self.__get_extracted_icon_path()
        self.exe_icon_url = f"http://{server_ip}:{port}/{urlSafePath(self.__icon_path)}"
        self.__extract()
        
    def __extract(self):
        """Extracts the icon from the executable and saves it as a PNG."""
        try:
            # test throwing error
            extractor = IconExtractor(self.__exe_path)
            
            # Get the largest available icon (returns BytesIO)
            icon_data = extractor.get_icon()
            
            # Convert BytesIO to PIL Image
            icon = Image.open(icon_data)
            
            # Save as PNG
            icon.save(self.__icon_path, format='PNG')
            # print(f"Icon extracted and saved to {self.__icon_path}")

        except FileNotFoundError as e:
            raise IconExtractionError(f"{e}\n---->[Executable file not found: {self.__exe_path}]<----") from None
        except OSError as e:
            traceback.print_exc()
            raise IconExtractionError(f"Error saving icon: {e}") from None
        except Exception as e:
            print(f"Error extracting icon: {e}")
            traceback.print_exc()
            raise IconExtractionError(f"Unexpected error: {e}") from None

    def __get_extracted_icon_path(self):
        """Generates a unique file name for the extracted icon."""
        new_file_name = gen_unique_filname(self.__exe_path) + '.jpg'
        new_img_path = _joinPath(self.__preview_folder, new_file_name)
        return new_img_path
    
    
if __name__ == '__main__':
    exe_path = r"C:\Users\hp\Desktop\Linux\my_code\Laner\workers\thumbnails\laner.exe"
    server_ip = NetworkManager().get_server_ip()  # Replace with actual server IP if needed
    # print(f"Server IP: {server_ip}")
    extractor = ExecutableIconExtractor(exe_path, server_ip,8000)
    # print(extractor.exe_icon_url)
    print(f"Icon URL: {extractor.exe_icon_url}")

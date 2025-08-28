"""
This script extracts the icon from an executable file (EXE) and saves it as a PNG image.  
It uses the icoextract library to handle the extraction.  
icoextract dependencies: pefile
"""
import traceback,threading

Image=IconExtractor=None
try:
    from PIL import Image
except ImportError:
    print("-- run pip install pillow")

try:
    from icoextract import IconExtractor
except ImportError:
    print("-- run pip install icoextract")

if not Image:
    raise ImportError('executable.py missing pillow')

if not IconExtractor:
    raise ImportError('executable.py missing icoextract')

if __name__ in ['thumbnails.executable','executable','__main__']:
    from .testing.sword import NetworkManager,NetworkConfig
    from .base import BaseGen,BaseGenException
else:
    from workers.sword import NetworkManager,NetworkConfig
    from workers.thumbnails.base import BaseGen,BaseGenException


class IconExtractionError(Exception, BaseGenException):
    """Custom exception for icon extraction errors."""
    # Custom exception for icon extraction errors
    # This will be raised if the icon extraction fails for any reason
    thumbnail_path = ''
    def __init__(self, message):
        self.getfailSafeImg()
        super().__init__(message)
        print(f'\n------------------------{self.__class__.__name__} Log start------------------------')
        self.message = message
        # self.args = args # don’t need self.args = args — super().__init__() already stores the message in .args.


class ExecutableIconExtractor(BaseGen):
    """Class to handle extraction of icons from executable files."""
    def __init__(self, exe_path: str, server_ip: str=NetworkConfig.server_ip,port: int=NetworkConfig.port,_thread=True):
        super().__init__(server_ip=server_ip, server_port=port)
        self._item_path = exe_path
        IconExtractionError.thumbnail_path = self.thumbnail_path
        if _thread:
            threading.Thread(
                        target=self.__extract,
                        daemon=True
                    ).start()
        else:
            self.__extract()
    @property
    def item_path(self):
        """Path to the executable file."""
        return self._item_path
    @property
    def img_format(self):
        """Returns the image format."""
        # Overriding super class property
        return 'png'
    
    def __extract(self):
        """Extracts the icon from the executable and saves it as a PNG."""
        try:
            extractor = IconExtractor(self.item_path)
            icon_data = extractor.get_icon() # Get the largest available icon (returns BytesIO)

            icon = Image.open(icon_data) # Convert BytesIO to PIL Image
            if icon.mode != 'RGBA':
                icon = icon.convert("RGBA")  # Ensure PNG compatibility
            icon.save(self.thumbnail_path, format='PNG', optimize=True)
            # print(f"Icon extracted and saved to {self.thumbnail_path}")

        except FileNotFoundError as e:
            raise IconExtractionError(f"{e}\n---->[Executable file not found: {self.item_path}]<----") from None
        except OSError as e:
            traceback.print_exc()
            raise IconExtractionError(f"Error saving icon: {e}") from None
        except Exception as e:
            print(f"Error extracting icon: {e}")
            traceback.print_exc()
            raise IconExtractionError(f"Unexpected errorx: {e}\nExe File: {self.item_path}") from None
    
    
if __name__ == '__main__':
    exe_path = r"C:\Users\hp\Desktop\Linux\my_code\Laner\workers\thumbnails\laner.exe" # og:6.21kb optimize.png:5.86kb
    server_ip = NetworkManager().get_server_ip()  # Replace with actual server IP if needed
    # print(f"Server IP: {server_ip}")
    extractor = ExecutableIconExtractor(exe_path, server_ip,NetworkConfig.port,_thread=False)
    print(f"Icon URL: {extractor.thumbnail_url}")

import traceback, threading
import PIL
from PIL import Image
try:
    import cairosvg
except ImportError:
    print("-- run pip install cairosvg")
    #print('Check cairosvg repo issuses section for how to fix or downloaad and install <link>')

if __name__ in ['thumbnails.image','image','__main__']:
    from .base import BaseGen,BaseGenException
    from .testing.sword import NetworkManager,NetworkConfig
else:
    from workers.thumbnails.base import BaseGen,BaseGenException
    from workers.sword import NetworkConfig

# thumbnail_path for BaseGenException is been implemented by BaseGen
class JPEGWorker(BaseGen,BaseGenException):
    """Worker class to convert images to JPEG format."""
    
    def __init__(self,img_path:str,server_ip:str,_thread=True):
        self.server_ip = server_ip
        self.server_port=NetworkConfig.port
        self.inputted_img_path = img_path
        self.__quality = 80
        if _thread:
            threading.Thread(
                        target=self.genrateJPEG,
                        daemon=True
                    ).start()
        else:
            self.genrateJPEG()
            
    @property
    def item_path(self):
        """Path to the executable file."""
        return self.inputted_img_path

    @property
    def img_format(self):
        """Returns the image format."""
        # Overriding super class property
        return 'jpg'
    
    def is_svg(self):
        return self.inputted_img_path.lower().endswith('.svg')

    def genrateJPEG(self):
        try:
            if self.is_svg():
                self.genPNG_from_SVG()
                
            im = Image.open(self.inputted_img_path)
            rgb_im = im.convert("RGB")
            rgb_im.save(self.thumbnail_path, format='JPEG', quality=self.__quality)

        except PIL.UnidentifiedImageError:
            print(f'Failed getting JPEG {self.inputted_img_path} <-----------------------------------------')
            print('Fail safe image path: ',self.thumbnail_path)
            self.getfailSafeImg()
        except Exception as e:
            print('Unplanned Error at JPEGWorker Class: ',e)
            traceback.print_exc()
        #TODO Probalbly catch all errors

    def genPNG_from_SVG(self):
        """Get png for jpg form svg :)
            Sets `self.inputted_img_path` parameter
        """
        self.__quality=100
        try:
            cairosvg.svg2png(url=self.inputted_img_path,write_to=self.thumbnail_path,output_width=1000,output_height=1000)
            self.inputted_img_path=self.thumbnail_path
        except Exception as e:
            print('Failed to convert SVG: ',e)
            self.getfailSafeImg()
            return
        

if __name__ == '__main__':
    server_ip = NetworkManager().get_server_ip()  # Replace with actual server IP if needed
    img_path=r'C:\Users\hp\Desktop\Linux\my_code\Laner\workers\thumbnails\icon.png' # og: 1.68mb formatted.png:1.68mb, formatted.jpg:379kb
    r=JPEGWorker(img_path,server_ip,_thread=False)
    print(r.thumbnail_url)

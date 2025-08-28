import traceback, threading


Image=cairosvg=None
try:
    import cairosvg
except ImportError:
    print('No svg previews')
    print("-- run pip install cairosvg")
    #print('Check cairosvg repo issuses section for how to fix or downloaad and install <link>')
except Exception as e:
    print("SVG Preview Issue Visit page https://github.com/Kozea/CairoSVG/issues/388")
    print('In dev mode for SVG Preview download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe')

try:
    import PIL
    from PIL import Image
except ImportError:
    print("-- run pip install pillow")
except Exception as e:
    print("Exception occurred while import from pillow", e)


if not Image:
    raise ImportError('image.py missing pillow')


if __name__ in ['thumbnails.image','image','__main__']:
    from base import BaseGen,BaseGenException
    from testing.sword import NetworkManager,NetworkConfig
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
            if not cairosvg:
                self.getfailSafeImg()
                return
            cairosvg.svg2png(url=self.inputted_img_path,write_to=self.thumbnail_path,output_width=1000,output_height=1000)
            self.inputted_img_path=self.thumbnail_path
        except Exception as e:
            print('Failed to convert SVG: ',e)
            self.getfailSafeImg()
            return
        

if __name__ == '__main__':
    server_ip = NetworkManager().get_server_ip()  # Replace with actual server IP if needed
    img_path=r'C:\Users\Blossom Restore\Downloads\Laner-desktop\assets\imgs\image.png' # og: 1.68mb formatted.png:1.68mb, formatted.jpg:379kb
    r=JPEGWorker(img_path,server_ip,_thread=False)
    print(r.thumbnail_url)

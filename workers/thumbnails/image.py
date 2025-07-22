import os, traceback, threading
from pathlib import Path
import PIL
from PIL import Image
try:
    import cairosvg
except:
    print('Check cairosvg repo issuses section for how to fix or downloaad and install <link>')

if __name__=='image' or __name__=='__main__':
    from helper import gen_unique_filname, _joinPath, getAppFolder, getUserPCName
else:
    from workers.helper import gen_unique_filname, _joinPath, getAppFolder, getUserPCName



class JPEGWorker:
        
    # TODO Make an init file or config file for app for things like this
    preview_folder = os.path.join(getAppFolder(), 'preview-imgs')
    def __init__(self,img_path:str,server_ip:str):
        self.server_ip = server_ip
        self.img_path = img_path

        os.makedirs(self.preview_folder,exist_ok=True)
        
        threading.Thread(
                        target=self.genrateJPEG,
                        daemon=True
                    ).start()
        
    def getJPEG_URL(self):
        """Returns JPG path while waiting for server"""
        new_file_name = gen_unique_filname(self.img_path) + '.jpg'
        new_img_path = _joinPath(self.preview_folder,new_file_name)
        return f"http://{self.server_ip}:8000/{new_img_path}"

    def is_svg(self):
        return self.img_path.lower().endswith('.svg')
        # with open("image.svg", "r") as f:
        #     header = f.read(100).lower()
        #
        # if "<svg" in header:
        #     print("It's an SVG file.")
    def genrateJPEG(self):
        # print('gotten img path ',self.img_path)
        new_file_name = gen_unique_filname(self.img_path) + '.jpg'
        new_img_path = _joinPath(self.preview_folder,new_file_name)
        # new_img_url=self.getJPEG_URL() # For debugging image server is path

        try:
            quality = 90
            if self.is_svg():
                converted_svg_file_path = _joinPath(self.preview_folder,Path(self.img_path).stem+'.png')
                print('converted_svg_file_path: ',converted_svg_file_path)
                # self.preview_folder, os.path.basename(
                try:
                    cairosvg.svg2png(url=self.img_path,write_to=converted_svg_file_path,output_width=1000,output_height=1000)
                    self.img_path=converted_svg_file_path
                    quality=100
                except Exception as e:
                    print('Failed to convert SVG: ',e)

            im = Image.open(self.img_path)
            rgb_im = im.convert("RGB")
            rgb_im.save(new_img_path, quality=quality)
            # print('new_file_name ',new_file_name)
            # print('new_img_url ',new_img_url) #For debugging
        except PIL.UnidentifiedImageError:
            im = Image.open(_joinPath(getAppFolder(),'assets','imgs','image.png'))
            rgb_im = im.convert("RGB")
            rgb_im.save(new_img_path, quality=60)
            
            print(f'Failed getting JPEG {self.img_path} <-----------------------------------------')
            return "assets/icons/image.png"
        except Exception as e:
            print('Unplanned Error at JPEGWorker Class: ',e)
            traceback.print_exc()
        #TODO Probalbly catch all errors

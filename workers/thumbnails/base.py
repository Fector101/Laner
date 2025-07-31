from abc import ABC, abstractmethod
import os
from typing import LiteralString
from PIL import Image

if __name__ in ['thumbnails.base','base','__main__']:
    from .testing.helper import gen_unique_filname, getAppFolder, urlSafePath,removeFirstDot,_joinPath
    from .testing.sword import NetworkConfig
else:
    from workers.helper import gen_unique_filname, _joinPath, getAppFolder, urlSafePath, removeFirstDot
    from workers.sword import NetworkConfig

def use_pc_for_static(img_file_name):
    return f"http://{NetworkConfig.server_ip}:{NetworkConfig.port}/{urlSafePath(_joinPath(getAppFolder(),"assets","imgs",img_file_name))}"

class BaseGenException(ABC):
    """Handles Creating Failed Img  
    Needs `thumbnail_path`
    Handles creating Fail safe img 
    """
    @property
    @abstractmethod
    def thumbnail_path(self):
        """Path to the thumbnail image."""
        # Children classes must implement this property.
        pass

    def getfailSafeImg(self):
        """Returns a fail-safe image Path."""
        # The Placeholder image is used when the original image cannot be processed.
        # And is gotten from the assets folder.
        # if not self.main_to_display_path:
        getfailSafeImg(self.thumbnail_path,'BaseGenException')


def getfailSafeImg(thumbnail_path,_abs_class,default_img_name='image.png'):
    """Returns a fail-safe image Path."""
    # The Placeholder image is used when the original image cannot be processed.
    # And is gotten from the assets folder.
    # if not self.main_to_display_path:
    try:
        if os.path.exists(thumbnail_path):
            return
        img = Image.open(_joinPath(getAppFolder(),'assets','imgs',default_img_name))
        if img.mode != 'RGBA':
            img = img.convert("RGBA")
        img.save(thumbnail_path, quality=60)
        
    except Exception as e:
        print('Error getting fall back:',e)
        print(f'-------Error from {_abs_class}--------')

class BaseGen(ABC):
    """Base class for thumbnail generation.  
    Needs `item_path`  
    Handles creating `thumbnail_url`, `thumbnail_path`  
    also `preview_folder` if need be and returing path
    """
    thumbnail_folder = 'preview-imgs'
    def __init__(self, server_ip: str=NetworkConfig.server_ip, server_port: int=NetworkConfig.port):
        """Initializes the BaseGen class."""
        # No path or specfic argument class recives should be formatted in the init block, Beacuse in VideoGen i change dymically
        self.server_ip = server_ip
        self.server_port = server_port
        self.create_preview_folder()

    @property
    @abstractmethod
    def item_path(self):
        """Path to the item being processed."""
        # Children classes must implement this property.
        pass

    @property
    def img_format(self):
        """Returns the image format."""
        # Default image format is PNG, but can be overridden by subclasses.
        return 'jpg'
    
    @property
    def preview_folder(self):
        """Creates preview folder

        Returns: path to the preview folder."""
        return self.create_preview_folder()
    
    def create_preview_folder(self):
        """Creates a folder for preview images if it doesn't exist."""
        preview_folder__ = _joinPath(getAppFolder(), self.thumbnail_folder)
        if not os.path.exists(preview_folder__):
            print('Creating preview folder from thumbnail.base.BaseGen: ', preview_folder__)
            os.makedirs(preview_folder__, exist_ok=True)
        return preview_folder__
    
    @property
    def thumbnail_url(self):
        """Returns the URL for the thumbnail image."""
        return f"http://{self.server_ip}:{self.server_port}/{urlSafePath(removeFirstDot(self.thumbnail_path))}"
    
    @property
    def thumbnail_path(self) -> LiteralString | str | bytes:
        """Joins preview folder with unique file name for path
        Returns the path to the thumbnail image.
        """
        return thumbnail_path_logic(self.item_path,self.img_format,self.preview_folder,_abs_class='BaseGen')#new_img_path

def thumbnail_path_logic(file_full_path,img_format,preview_folder,_abs_class):
    if not file_full_path:
        print(f'No actual value for `self.item_path` in {_abs_class}, probarly an empty string: {file_full_path}')
        raise ValueError('No actual value for `self.item_path` in BaseGen')

    new_file_name = gen_unique_filname(file_full_path) + '.' + img_format
    return _joinPath(preview_folder, new_file_name)

class DocExtractorABS(ABC):
    """ Requires `extract`, `default_img_name` and `thumbnail_path`
    Adds Order to Document Extactors and also 
    
    """
    @abstractmethod
    def extract(self,item_path,thumbnail_path,config):
        """Does extraction."""
        # Children classes must implement this property.
        pass

    @property
    @abstractmethod
    def default_img_name(self):
        return 'image.png'
    
    @property
    def thumbnail_path(self):
        """Path to the thumbnail being processed."""
        pass

    def getfailSafeImg(self):
        """Returns a fail-safe image Path."""
        # The Placeholder image is used when the original image cannot be processed.
        # And is gotten from the assets folder.
        # if not self.main_to_display_path:
        getfailSafeImg(self.thumbnail_path,'DocExtractorABS',self.default_img_name)



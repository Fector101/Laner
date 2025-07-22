from abc import ABC, abstractmethod
import os
from PIL import Image


if __name__=='base' or __name__=='__main__':
    from testing.helper import gen_unique_filname, getAppFolder, urlSafePath
    from os.path import join as _joinPath
    from testing.sword import NetworkConfig
else:
    from workers.helper import gen_unique_filname, _joinPath, getAppFolder, urlSafePath
    from workers.sword import NetworkConfig

class BaseGenException(ABC):
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
        try:
            img = Image.open(_joinPath(getAppFolder(),'assets','imgs','image.png'))
            if img.mode != 'RGBA':
                img = img.convert("RGBA")
            img.save(self.thumbnail_path, quality=60)
            
        except Exception as e:
            print('Error getting fall back:',e)
            print(f'-------Error from BaseGenException--------')

class BaseGen(ABC):
    """Base class for thumbnail generation."""
    def __init__(self, server_ip: str=NetworkConfig.server_ip, server_port: int=NetworkConfig.port):
        """Initializes the BaseGen class."""
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
        return 'png'
    @property
    def preview_folder(self):
        """Returns the path to the preview folder."""
        return self.create_preview_folder()
    
    def create_preview_folder(self):
        """Creates a folder for preview images if it doesn't exist."""
        preview_folder__ = os.path.join(getAppFolder(), 'preview-imgs')
        if not os.path.exists(preview_folder__):
            print('Creating preview folder from thumbnail.base.BaseGen: ', preview_folder__)
            os.makedirs(preview_folder__, exist_ok=True)
        return preview_folder__
    
    @property
    def thumbnail_url(self):
        """Returns the URL for the thumbnail image."""
        return f"http://{self.server_ip}:{self.server_port}/{urlSafePath(self.thumbnail_path)}"
    
    @property
    def thumbnail_path(self):
        """Joins preview folder with unique file name for path
        Returns the path to the thumbnail image.
        """
        new_file_name = gen_unique_filname(self.item_path) + '.' + self.img_format
        new_img_path = _joinPath(self.preview_folder, new_file_name)
        return new_img_path
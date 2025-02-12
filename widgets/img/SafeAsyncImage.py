from kivy.uix.image import AsyncImage
    
class SafeAsyncImage(AsyncImage):
    mipmap= True
     
    def on_error(self,*args):
        print(f"Failed to load image 101: {self.source}")
        self.source='assets/icons/image.png'

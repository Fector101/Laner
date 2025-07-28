import os
if __name__=='__main__':
    # For Tests
    from testing.sword import NetworkConfig
    from testing.helper import getAppFolder, urlSafePath,_joinPath, getFileExtension
else:
    from workers.helper import getAppFolder, urlSafePath, _joinPath, getFileExtension
    from workers.sword import NetworkConfig

from .video import VideoThumbnailExtractor #, generateThumbnails
from .image import JPEGWorker
from .executable import ExecutableIconExtractor
        
# File Type Definitions
MY_OWNED_ICONS = ['.py', '.js', '.css', '.html', '.json', '.deb', '.md', '.sql', '.java']
ZIP_FORMATS = ['.zip', '.7z', '.tar', '.bzip2', '.gzip', '.xz', '.lz4', '.zstd', '.bz2', '.gz']
VIDEO_FORMATS = ('.mkv', '.mp4', '.avi', '.mov')
AUDIO_FORMATS = ('.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac', '.wma', '.aiff', '.opus')
PICTURE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif','.svg','.ico')
SPECIAL_FOLDERS = ['home', 'pictures', 'templates', 'videos', 'documents', 'music', 'favorites', 'share', 'downloads']
SUBTITLE_EXTENSIONS = (
    # Plain Text Subtitle Formats
    ".srt", ".sub", ".sbv", ".smi", ".rt", ".ttml", ".xml", ".vtt", ".lrc", ".stl",

    # Image-Based Subtitle Formats
    ".sub", ".idx", ".sup", ".pgs",

    # Proprietary / Professional Formats
    ".stl", ".cap", ".890", ".pac", ".dci", ".xml", ".fab",

    # Subtitles for Closed Captions
    ".scc", ".mcc", ".dfxp", ".imsc",

    # Other Subtitle Formats
    ".jss", ".ssa", ".ass", ".usf", ".aqt", ".pjs", ".bas"
)
EXECUTABLE_FORMATS = ('.exe','.dll','.mun')#, '.msi', '.bat', '.cmd', '.sh', '.run')

# icon can be a placeholder while thumbnail is been genrated or owned icons
def get_icon_for_file(path,video_paths:list=[]) -> tuple[str, str]:
    """Returns appropriate icon and thumbnail based on file type.
    And adds more paths to video_paths if need be
    """
    
    is_dir = os.path.isdir(path)
    ext = getFileExtension(path).lower()
    if is_dir:
        name:str = os.path.basename(os.path.normpath(path))
        return (f"assets/icons/folders/{name.lower()}.png" if name.lower() in SPECIAL_FOLDERS else "assets/icons/folders/folder.png", '')
    elif ext in MY_OWNED_ICONS:
        return (f"assets/icons/{ext[1:]}.png", '')
    elif ext in ZIP_FORMATS:
        return ("assets/icons/packed.png", '')
    elif ext in VIDEO_FORMATS:
        video_paths.append(path)
        instance = VideoThumbnailExtractor([path],server_ip=NetworkConfig.server_ip,server_port=NetworkConfig.port)
        return ("assets/icons/video.png", instance.thumbnail_url)
    elif ext in SUBTITLE_EXTENSIONS:
        return ("assets/icons/subtitle.png", '')
    elif ext in AUDIO_FORMATS:
        return ("assets/icons/audio.png", '')
    elif ext in PICTURE_FORMATS:
        instance = JPEGWorker(path,NetworkConfig.server_ip)
        return ("assets/icons/image.png", instance.thumbnail_url)
    elif ext in EXECUTABLE_FORMATS:
        instance = ExecutableIconExtractor(path, NetworkConfig.server_ip, NetworkConfig.port)
        pl_url = (f"http://{NetworkConfig.server_ip}:{NetworkConfig.port}/{urlSafePath(_joinPath(getAppFolder(),"assets","imgs","executable.png"))}")
        return (pl_url, instance.thumbnail_url)
        
    return ("assets/icons/file.png", '')

import os

if __name__=='thumbnails':
    # For Tests
    from .testing.sword import NetworkConfig
    from .testing.helper import getAppFolder, urlSafePath,_joinPath, getFileExtension
else:
    from workers.helper import getAppFolder, urlSafePath, _joinPath, getFileExtension
    from workers.sword import NetworkConfig

from .base import use_pc_for_static
from .video import VideoThumbnailExtractor #, generateThumbnails
from .image import JPEGWorker
from .executable import ExecutableIconExtractor
# from .document import DocumentIconExtractor
from .doc import DocumentIconExtractor
from itertools import chain



# File Type Definitions
# WARNING If tuple contains only one item ` '' in tuple ` will return `True`
MY_OWNED_ICONS = ('.py', '.js', '.css', '.html', '.json', '.deb', '.md', '.sql', '.java')
ZIP_FORMATS = ('.zip', '.7z', '.tar', '.bzip2', '.gzip', '.xz', '.lz4', '.zstd', '.bz2', '.gz')
VIDEO_FORMATS = ('.mkv', '.mp4', '.avi', '.mov')
AUDIO_FORMATS = ('.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac', '.wma', '.aiff', '.opus')
PICTURE_FORMATS = ('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif','.svg','.ico')
SPECIAL_FOLDERS = {'home', 'pictures', 'templates', 'videos', 'documents', 'music', 'favorites', 'share', 'downloads'}
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
DOCUMENT_EXTENSIONS = (".pdf",'.docx',".doc") #,".docx",".ppt",".pptx",".xls",".xlsx",".odt",".ods",".odp",".rtf",".csv",".tsv")
COMBINED_EXTENSIONS = set(chain(
    MY_OWNED_ICONS, ZIP_FORMATS, VIDEO_FORMATS,
    SUBTITLE_EXTENSIONS, AUDIO_FORMATS,
    PICTURE_FORMATS, EXECUTABLE_FORMATS,
    DOCUMENT_EXTENSIONS
))


# icon can be a placeholder while thumbnail is been genrated or owned icons
def get_icon_for_file(path, is_dir,name,video_paths=None) -> tuple[str, str]:
    """Returns appropriate icon and thumbnail based on file type.
    And adds more paths to video_paths if need be
    """

    if video_paths is None:
        video_paths = []

    if is_dir:
        return f"assets/icons/folders/{name.lower()}.png" if name.lower() in SPECIAL_FOLDERS else "assets/icons/folders/folder.png", ''

    ext = os.path.splitext(path)[1].lower()

    if ext not in COMBINED_EXTENSIONS:
        return "assets/icons/file.png", ''

    if ext in MY_OWNED_ICONS:
        return f"assets/icons/{ext[1:]}.png", ''
    if ext in ZIP_FORMATS:
        return "assets/icons/packed.png", ''
    if ext in VIDEO_FORMATS:
        video_paths.append(path)
        # instance = VideoThumbnailExtractor(path,server_ip=NetworkConfig.server_ip,server_port=NetworkConfig.port)
        return "assets/icons/video.png", VideoThumbnailExtractor(path,server_ip=NetworkConfig.server_ip,server_port=NetworkConfig.port).thumbnail_url
    if ext in SUBTITLE_EXTENSIONS:
        return "assets/icons/subtitle.png", ''
    if ext in AUDIO_FORMATS:
        return "assets/icons/audio.png", ''
    if ext in PICTURE_FORMATS:
        instance = JPEGWorker(path,NetworkConfig.server_ip)
        return "assets/icons/image.png", instance.thumbnail_url
    if ext in EXECUTABLE_FORMATS:
        instance = ExecutableIconExtractor(path, NetworkConfig.server_ip, NetworkConfig.port)
        return use_pc_for_static("executable.png"), instance.thumbnail_url
    if ext in DOCUMENT_EXTENSIONS:
        if ext == '.pdf':

            # Add document to processing queue
            # Create extractor instance
            extractor = DocumentIconExtractor()
            extractor.add_document(path)
        # instance = DocumentIconExtractor(doc_path=path, server_ip=NetworkConfig.server_ip, server_port=NetworkConfig.port)
        # instance.documents_collection = path
            return extractor.pc_static_img, extractor.thumbnail_url
        return "assets/icons/file.png", ''

    return "assets/icons/file.png", ''


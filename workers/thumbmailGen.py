import cv2
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def generate_thumbnail(video_path, output_path, time=1.0):
    """
    Generate a thumbnail from a single video.

    :param video_path: Path to the input video.
    :param output_path: Path to save the thumbnail.
    :param time: Time (in seconds) to capture the thumbnail frame.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    success, frame = cap.read()
    if success:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        # cv2.imwrite(output_path, frame)
        cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY,10])
        # print(f"Thumbnail saved at {output_path}")
    else:
        print(f"Failed to capture frame for {video_path}")

    cap.release()

def generateThumbnails(video_paths, output_dir, time=1.0, max_threads=4):
    """
    Generate thumbnails from multiple videos in parallel.

    :param video_paths: List of video file paths.
    :param output_dir: Directory to save all thumbnails.
    :param time: Time (in seconds) to capture the thumbnail frame.
    :param max_threads: Maximum number of threads to use for parallel processing.
    """
    def process_video(video_path):
        video_name = Path(video_path).stem
        output_path = f"{output_dir}/{video_name}_thumbnail.jpg"
        generate_thumbnail(video_path, output_path, time)

    with ThreadPoolExecutor(max_threads) as executor:
        executor.map(process_video, video_paths)

# Example usage
# if __name__ == "__main__":
    
#     video_directory = "/home/fabian/Videos/I Probarly don't know this Stuff - (The Complete 2021 Web Development Bootcamp)/33. React.js/"
#     # video_directory = os.path.join("/home","fabian","Videos","I Probarly don't know this Stuff - (The Complete 2021 Web Development Bootcamp)","25. SQL")
#     output_directory = './lab'
    
#     video_files = video_files = [
#         os.path.join(video_directory, f) 
#         for f in os.listdir(video_directory) 
#         if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))
#     ]
#     print(len(video_files))
#     generateThumbnails(video_files, output_directory, max_threads=8)

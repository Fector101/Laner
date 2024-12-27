import cv2
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from workers.helper import gen_unique_filname


def add_black_and_white_boxes(image):
    """
    Add alternating black-and-white boxes at the left and right sides of the image.

    :param image: A Pillow Image object.
    :return: Modified image with decorations.
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size
    def convert_dec_rgb(dec=0.2):
        return int(255*dec)
    my_black_color=(convert_dec_rgb(),convert_dec_rgb(),convert_dec_rgb())
    my_white_color=(205,205,205)
    
    # Define box size
    box_width = width // 15  # Width of each box
    box_height = height // 10  # Height of each box

    # Adding boxes on the left side
    for i in range(0, height, box_height):
        color = my_white_color if (i // box_height) % 2 == 0 else my_black_color
        draw.rectangle([(0, i), (box_width, i + box_height)], fill=color)

    # Adding boxes on the right side
    for i in range(0, height, box_height):
        color = my_white_color if (i // box_height) % 2 == 0 else my_black_color
        draw.rectangle([(width - box_width, i), (width, i + box_height)], fill=color)

    return image

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
        
        # Convert the frame to RGB (required for Pillow)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)

        # Add overlay decorations
        image_with_overlay = add_black_and_white_boxes(image)

        # Save the thumbnail with decorations
        image_with_overlay.save(output_path, "JPEG", quality=10)
        # cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY,10])
        # print(f"Thumbnail saved at {output_path}")
    else:
        print(f"Failed to capture frame for {video_path}")

    cap.release()
    
# generate_thumbnail("/home/fabian/Videos/I Probarly don't know this Stuff - (The Complete 2021 Web Development Bootcamp)/22. EJS/group .mp4/10. Understanding Node Module Exports How to Pass Functions and Data between Files.mp4",'stan/tets.jpg')

def generateThumbnails(video_paths, output_dir, time=1.0, max_threads=4):
    """
    Generate thumbnails from multiple videos in parallel.

    :param video_paths: List of video file paths.
    :param output_dir: Directory to save all thumbnails.
    :param time: Time (in seconds) to capture the thumbnail frame.
    :param max_threads: Maximum number of threads to use for parallel processing.
    """
    def process_video(video_path:str):
        # video_name = Path(video_path).stem
        # thumbnail_name = base64.urlsafe_b64encode(video_path.encode('utf-8')).decode()
        thumbnail_name = gen_unique_filname(video_path)
        print(video_path,'|||',thumbnail_name)
        
        output_path = f"{output_dir}/{thumbnail_name}.jpg"
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

import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail_with_overlay(video_path, output_path, time=1.0, quality=75):
    """
    Generate a thumbnail from a single video and add overlay decorations.

    :param video_path: Path to the input video.
    :param output_path: Path to save the thumbnail.
    :param time: Time (in seconds) to capture the thumbnail frame.
    :param quality: Quality of the saved thumbnail (1-100, for JPEG format).
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file: {video_path}")

        # Calculate the frame number for the given time
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the specific frame
        success, frame = cap.read()
        if success:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Convert the frame to RGB (required for Pillow)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            # Add overlay decorations
            image_with_overlay = add_overlay_decorations(image)

            # Save the thumbnail with decorations
            image_with_overlay.save(output_path, "JPEG", quality=quality)
            print(f"Thumbnail with overlay saved at {output_path}")
        else:
            print(f"Failed to capture frame at {time}s for video: {video_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Release the video capture object
        cap.release()

def add_overlay_decorations(image):
    """
    Add overlay decorations (e.g., tape signs) to the image.

    :param image: A Pillow Image object.
    :return: Modified image with decorations.
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Add tape decorations
    tape_width = width // 10
    tape_height = height // 8
    tape_color = (255, 223, 0)  # Yellow tape

    # Left tape
    draw.rectangle([(0, 0), (tape_width, tape_height)], fill=tape_color)
    draw.text((10, 10), "Tape", fill="black")  # Optional text on the tape

    # Right tape
    draw.rectangle([(width - tape_width, 0), (width, tape_height)], fill=tape_color)
    draw.text((width - tape_width + 10, 10), "Tape", fill="black")  # Optional text on the tape

    return image

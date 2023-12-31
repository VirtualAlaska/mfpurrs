from PIL import Image, ImageSequence
import os

# Set the path to the folder containing the images and GIFs that you want to flip
folder_path = r"<path to directory here>"

# Set the path to the folder where the newly flipped images should be saved
new_folder_path = r"<path to directory here>"

# Create the new folder if it doesn't exist
os.makedirs(new_folder_path, exist_ok=True)

# Loop through all the files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Check if the file is an image (PNG, JPEG, or GIF)
    if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        try:
            # Open the image file
            image = Image.open(file_path)

            # Flip the image or GIF frames horizontally
            if image.format == 'GIF':
                frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
                flipped_frames = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in frames]

                flipped_frames[0].save(
                    os.path.join(new_folder_path, filename),
                    format='GIF',
                    save_all=True,
                    append_images=flipped_frames[1:],
                    loop=0,
                    duration=image.info['duration']
                )
            else:
                # Flip the static image
                flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                flipped_image.save(
                    os.path.join(new_folder_path, filename),
                    format=image.format,  # Preserve the original format
                    quality=95  # Set JPEG quality if applicable
                )

            print(f"Flipped {filename} and saved to {new_folder_path}")
        except Exception as e:
            print(f"Error flipping {filename}: {e}")
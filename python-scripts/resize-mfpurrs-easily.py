from PIL import Image, ImageSequence
import os

# Set the path to the folder containing the mfpurrs that you want to resize
folder_path = r"<path_to_folder>"

# Set the desired width and height (in pixels) for the resized mfpurrs
# The smallest, byte-perfect size of an mfpurr is 40x40 pixels
new_width = 40
new_height = 40

# Set the path to the folder where the newly resized mfpurrs should go in
new_folder_path = r"<path_to_folder>"

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

            # Resize the image or GIF frames
            if image.format == 'GIF':
                frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
                resized_frames = [
                    frame.resize((new_width, new_height), Image.NEAREST).convert("RGBA").convert("P", palette=Image.ADAPTIVE, colors=128)
                    for frame in frames
                ]
                resized_gif = resized_frames[0]
                resized_gif.save(
                    os.path.join(new_folder_path, filename),
                    format='GIF',
                    save_all=True,
                    append_images=resized_frames[1:],
                    loop=0,
                    duration=image.info['duration']
                )
            else:
                # Resize the static image
                resized_image = image.resize((new_width, new_height), Image.NEAREST)
                resized_image.save(
                    os.path.join(new_folder_path, filename),
                    format=image.format,  # Preserve the original format
                    quality=95  # Set JPEG quality if applicable
                )

            print(f"Resized and converted {filename} and saved to {new_folder_path}")
        except Exception as e:
            print(f"Error resizing {filename}: {e}")
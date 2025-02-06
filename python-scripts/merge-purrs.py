import os
from PIL import Image, ImageSequence
from tqdm import tqdm

"""
Use the merge-purrs.py script to create a new set of 10,000 PNGs / GIFs
where the mfpurr is on the left and the megapurr is on the right.

The script assumes that:

	- Each mfpurr is 1024x1024 pixels (sourced from here: https://github.com/VirtualAlaska/mfpurrs/tree/main/art/10k-upscaled-mfpurrs)
	- Each megapurr is 1000x1000 pixels (their size in IPFS)

Update these variables with the folders that store your mfpurrs / megapurrs and where you want the output to go:

	- mfpurr_dir
	- megapurr_dir
	- output_dir
"""

# Define directories
mfpurr_dir = r"PATH_TO_10K_MFPURRS"
megapurr_dir = r"PATH_TO_10K_MFPURRS"
output_dir = r"PATH_TO_DESIRED_OUTPUT_LOCATION"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get sorted list of all image files (PNG & GIF) from both folders
mfpurr_files = sorted([f for f in os.listdir(mfpurr_dir) if f.lower().endswith(('.png', '.gif'))])
megapurr_files = sorted([f for f in os.listdir(megapurr_dir) if f.lower().endswith(('.png', '.gif'))])

# Ensure both folders have the same number of files
if len(mfpurr_files) != len(megapurr_files):
    print("Error: Number of images in both folders do not match!")
    exit(1)

# Function to load an image or extract frames from GIF
def load_image(image_path):
    img = Image.open(image_path)
    
    if img.format == "GIF":
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(img)]
        return frames
    else:
        return [img.convert("RGBA")]  # Return a single-frame list for PNGs

# Function to merge two images (or animations)
def merge_images(mfpurr_frames, megapurr_frames):
    # Resize all MFPurr frames to 1000x1000
    mfpurr_frames = [frame.resize((1000, 1000), Image.NEAREST) for frame in mfpurr_frames]

    # Determine max number of frames
    num_frames = max(len(mfpurr_frames), len(megapurr_frames))

    # Loop shorter GIF to match frame count
    mfpurr_frames *= (num_frames // len(mfpurr_frames)) + 1
    megapurr_frames *= (num_frames // len(megapurr_frames)) + 1

    # Trim excess frames
    mfpurr_frames = mfpurr_frames[:num_frames]
    megapurr_frames = megapurr_frames[:num_frames]

    # Merge frames side by side
    merged_frames = []
    for mf_frame, mp_frame in zip(mfpurr_frames, megapurr_frames):
        merged_img = Image.new("RGBA", (2000, 1000))
        merged_img.paste(mf_frame, (0, 0))
        merged_img.paste(mp_frame, (1000, 0))
        merged_frames.append(merged_img)

    return merged_frames

# Process each pair of images with a progress bar
with tqdm(total=len(mfpurr_files), desc="Merging Images", unit="image") as pbar:
    for mfpurr_file, megapurr_file in zip(mfpurr_files, megapurr_files):
        mfpurr_path = os.path.join(mfpurr_dir, mfpurr_file)
        megapurr_path = os.path.join(megapurr_dir, megapurr_file)
        
        try:
            # Load images or GIF frames
            mfpurr_frames = load_image(mfpurr_path)
            megapurr_frames = load_image(megapurr_path)

            # Merge the images or animations
            merged_frames = merge_images(mfpurr_frames, megapurr_frames)

            # Determine output format (GIF or PNG)
            output_filename = os.path.splitext(mfpurr_file)[0]
            if mfpurr_file.lower().endswith('.gif') and megapurr_file.lower().endswith('.gif'):
                output_path = os.path.join(output_dir, f"{output_filename}.gif")
                merged_frames[0].save(output_path, save_all=True, append_images=merged_frames[1:], loop=0, duration=100)
            else:
                output_path = os.path.join(output_dir, f"{output_filename}.png")
                merged_frames[0].save(output_path, format="PNG")

        except Exception as e:
            print(f"\nError processing {mfpurr_file} and {megapurr_file}: {e}")

        pbar.update(1)  # Update progress bar

print("✅ Merging complete! Merged images saved in:", output_dir)

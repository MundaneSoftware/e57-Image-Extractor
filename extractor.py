import asyncio
import os
import gc
import io

import numpy as np
from pathlib import Path
from pye57 import E57
from PIL import Image

from tkinter import Tk, Label, Button, filedialog, StringVar, messagebox
from tkinter.ttk import Progressbar

# Set a higher limit for the image pixels to avoid decompression bomb warnings
Image.MAX_IMAGE_PIXELS = None  # Disable the limit, or set it to a high number

async def process_e57_file(file_path, output_path, coords_file_path, progress_bar, current_progress):
    """
    Processes a single E57 file to extract spherical images and metadata.

    Args:
        file_path (str): Path to the E57 file.
        output_path (Path): Directory where output images and files will be saved.
        coords_file_path (Path): Path to the coordinates CSV file.
        progress_bar (ttk.Progressbar): Progress bar widget to update.
        current_progress (list): List with one element tracking completed file count.

    Raises:
        FileNotFoundError: If the E57 file does not exist.
    """
    # Ensure the file exists before processing
    if not os.path.exists(file_path):
        print(f"E57 file not found at path: {file_path}")
        raise FileNotFoundError(f"E57 file not found at path: {file_path}")
    
    # Load the E57 file and extract spherical representations
    e57_file = E57(str(file_path))
    spherical_representations = extract_spherical_representations(e57_file)
    num_scans = e57_file.scan_count

    for scan_index in range(num_scans):
        # Retrieve scan metadata
        scan_header = e57_file.get_header(scan_index)
        translation = scan_header.translation
        rotation = scan_header.rotation
        guid = scan_header['guid'].value()
        name = scan_header['name'].value()

        # Process spherical representation if it exists
        spherical_representation = spherical_representations.get(guid)
        if spherical_representation:
            image_file_name, image_full_path = process_image(spherical_representation, name, output_path)

            # Append metadata to the coords file
            with open(coords_file_path, 'a') as f:
                f.write(f"{image_file_name},{image_full_path},{translation[0]},{translation[1]},{translation[2]},"
                        f"{rotation[1]},{rotation[2]},{rotation[3]},{rotation[0]}\n")
    
    # Update the progress bar after processing each file
    current_progress[0] += 1
    progress_bar["value"] = current_progress[0]
    progress_bar.update_idletasks()


def extract_spherical_representations(e57_file):
    """
    Extracts spherical image representations from an E57 file.

    Args:
        e57_file (E57): Loaded E57 file object.

    Returns:
        dict: Mapping of GUIDs to spherical representations.
    """
    spherical_dict = {}

    # Access the root node of the E57 file
    imf = e57_file.image_file
    root = imf.root()

    # Check if 'images2D' exists in the root node
    if root['images2D']:
        for image_idx, image2D in enumerate(root['images2D']):
            try: 
                spherical_representation = image2D['sphericalRepresentation']
            except KeyError:
                # Skip if the key does not exist
                continue

            if spherical_representation:
                # Retrieve associated GUID for the representation
                associated_guid = None
                if image2D['associatedData3DGuid']:
                    associated_guid = image2D['associatedData3DGuid'].value()
                elif image2D['rlms:scanposGuid']:
                    associated_guid = image2D['rlms:scanposGuid'].value()

                if associated_guid:
                    spherical_dict[associated_guid] = spherical_representation
                    
    return spherical_dict


def process_image(spherical_representation, name, output_path):
    """
    Processes and saves a spherical image from its representation.

    Args:
        spherical_representation (Node): Spherical image data node.
        name (str): Name of the image to use as the file name.
        output_path (Path): Directory to save the output image.

    Returns:
        tuple: (image_file_name, image_full_path)
    """
    # Load image data from the representation
    image_ref = spherical_representation["jpegImage"] or spherical_representation["pngImage"]
    image_data = np.zeros(shape=image_ref.byteCount(), dtype=np.uint8)
    image_ref.read(image_data, 0, image_ref.byteCount())

    # Open and resize the image
    img = Image.open(io.BytesIO(image_data))
    img_resized = img.resize((8192, 4096), Image.Resampling.LANCZOS)

    # Save the resized image
    image_file_name = f"{name}.jpeg"
    image_full_path = Path(output_path) / image_file_name
    img_resized.save(image_full_path, "JPEG", quality=50)

    # Clean up memory
    del img_resized
    gc.collect()

    return image_file_name, image_full_path


async def extract_spherical_images(file_paths, progress_bar):
    """
    Processes a list of E57 files to extract spherical images and metadata.

    Args:
        file_paths (list): List of E57 file paths.
        progress_bar (ttk.Progressbar): Progress bar widget to update.
    """
    if not file_paths:
        print("No files selected.")
        return

    # Define the output directory
    output_path = Path(file_paths[0]).parent / "output"
    create_directory_if_not_exist(output_path)

    # Ensure the coords file exists
    coords_file_path = Path(output_path) / "coords.csv"
    if not coords_file_path.exists():
        print(f"Creating coords file: {coords_file_path}")
        with open(coords_file_path, 'w') as f:
            f.write("image_file_name,image_path,translation_x,translation_y,translation_z,rotation_x,rotation_y,rotation_z,rotation_w\n")

    # Initialize progress tracking
    current_progress = [0]
    progress_bar["maximum"] = len(file_paths)

    # Process each file
    for file_path in file_paths:
        if not file_path.endswith('.e57'):
            print(f"Skipping non-E57 file: {file_path}")
            continue
        await process_e57_file(file_path, output_path, coords_file_path, progress_bar, current_progress)


def select_files():
    """Opens a dialog to select multiple E57 files."""
    paths = filedialog.askopenfilenames(
        title="Select E57 Files",
        filetypes=[("E57 files", "*.e57"), ("All files", "*.*")]
    )
    if paths:
        selected_paths.set(paths)
        input_path.set(f"{len(paths)} file(s) selected")
    else:
        input_path.set("No files selected")


def create_directory_if_not_exist(directory_path):
    """
    Ensures a directory exists, creating it if necessary.

    Args:
        directory_path (Path): Directory path to check/create.
    """
    dir_path = Path(directory_path)
    if not dir_path.exists():
        print(f"Creating directory: {directory_path}")
        dir_path.mkdir(parents=True, exist_ok=True)
    else:
        print(f"Directory already exists: {directory_path}")


def start_processing():
    """Triggers the async processing of selected E57 files."""
    paths_str = selected_paths.get()
    if not paths_str:
        messagebox.showerror("Error", "No files selected for processing!")
        return

    try:
        paths_str = paths_str.strip("[]")
        paths_list = [path.strip(" '").strip("('").strip("')") for path in paths_str.split(",")]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse file paths: {e}")
        return

    # Replace the label with a progress bar during processing
    entry.pack_forget()
    progress_bar.pack(pady=10)

    # Run the processing
    asyncio.run(extract_spherical_images(paths_list, progress_bar))

    # Reset the UI after processing
    progress_bar.pack_forget()
    entry.pack(pady=10)
    messagebox.showinfo("Success", "Processing complete!")


# GUI Setup
root = Tk()
root.title("E57 Spherical Image Extractor")

input_path = StringVar()
selected_paths = StringVar()

# GUI Components
Label(root, text="Select E57 files:").pack(pady=10)
entry = Label(root, textvariable=input_path, width=50, relief="sunken", anchor="w")
entry.pack(pady=5)

progress_bar = Progressbar(root, orient="horizontal", mode="determinate", length=300)

Button(root, text="Select Files", command=select_files).pack(pady=5)
Button(root, text="Start Processing", command=start_processing).pack(pady=10)

# Start the GUI
root.geometry("400x200")
root.mainloop()

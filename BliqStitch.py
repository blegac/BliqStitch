import os
import re
import cv2
import numpy as np
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tifffile import imwrite
import tifffile
import scyjava
import imagej
from tqdm import tqdm
from basicpy import BaSiC

def on_select(event):
    selected_item = combo_box.get()
    label.config(text="Selected Item: " + selected_item)

def save_selection():
    global chosen_analysis
    chosen_analysis = combo_box.get()
    print(f"Analysis selected: {chosen_analysis}")
    root.destroy()  # Close the window after saving the selection

root = tk.Tk()
root.title("Combobox Example")

# Create a label
label = tk.Label(root, text="Selected Item: ")
label.pack(pady=10)

# Create a Combobox widget
combo_box = ttk.Combobox(root, values=["Z Projection", "Most Sharp Image"])
combo_box.pack(pady=5)

# Set default value
combo_box.set("Z Projection")

# Bind event to selection
combo_box.bind("<<ComboboxSelected>>", on_select)

# Create an OK button
ok_button = ttk.Button(root, text="OK", command=save_selection)
ok_button.pack(pady=10)

root.mainloop()


if chosen_analysis == "Most Sharp Image":
    # Your existing functions
    def variance_of_laplacian(image):
        return cv2.Laplacian(image, cv2.CV_64F).var()
    
    def process_images(folder_path):
        best_images = {}
        best_scores = defaultdict(lambda: -float('inf'))
        best_filenames = {}  # To store the modified filenames
        
        max_x = -1  # Variable to hold maximum x value
        max_y = -1  # Variable to hold maximum y value

        if not folder_path:
            print("No folder selected. Exiting.")
            return best_images, best_scores, None

        filenames = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        for filename in filenames:
            x_match = re.search(r'-X(\d+)-', filename)
            y_match = re.search(r'-Y(\d+)-', filename)

            x = int(x_match.group(1)) if x_match else 0
            y = int(y_match.group(1)) if y_match else 0

            # Update maximum x and y if necessary
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            image_path = os.path.join(folder_path, filename)
            image = tifffile.imread(image_path)

            if image is None:
                print(f"Failed to load {filename}. Skipping.")
                continue

            score = variance_of_laplacian(image)

            if score > best_scores[(x, y)]:
                best_scores[(x, y)] = score
                best_images[(x, y)] = image
                
                # Create the new filename based on your specifications
                base_name = filename.split('-Slice')[0]
                new_filename = f"{base_name}"
                best_filenames[(x, y)] = new_filename  # Store the new filename

        # For now, setting canvas as None
        canvas = None

        return best_images, best_scores, canvas, best_filenames, max_x, max_y

if chosen_analysis == "Z Projection":
    def process_images(folder_path):
        best_images = {}
        best_filenames = {}  # To store the modified filenames
        
        max_x = -1  # Variable to hold maximum x value
        max_y = -1  # Variable to hold maximum y value

        if not folder_path:
            print("No folder selected. Exiting.")
            return best_images, None

        filenames = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # Group filenames by XY position
        xy_positions = defaultdict(list)
        for filename in filenames:
            x_match = re.search(r'-X(\d+)-', filename)
            y_match = re.search(r'-Y(\d+)-', filename)

            x = int(x_match.group(1)) if x_match else 0
            y = int(y_match.group(1)) if y_match else 0

            xy_positions[(x, y)].append(filename)

        for xy_position, filenames in xy_positions.items():
            x, y = xy_position

            # Update maximum x and y if necessary
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            # Accumulate images for the same XY position
            images_stack = [tifffile.imread(os.path.join(folder_path, filename)) for filename in filenames]

            if not images_stack:
                print(f"No images found for XY position ({x}, {y}). Skipping.")
                continue

            # Stack the images along the Z-axis
            stacked_image = np.stack(images_stack, axis=0)

            # Use maximum intensity projection along the Z-axis
            projection = np.max(stacked_image, axis=0)

            # Create the new filename based on your specifications
            base_name = filenames[0].split('-Slice')[0]  # Assuming all filenames share the same base name
            new_filename = f"{base_name}_zProjection"  # Adjust the new filename as needed
            best_filenames[(x, y)] = new_filename  # Store the new filename

            # Store the Z-projection for each XY position
            best_images[(x, y)] = projection

        return best_images, best_filenames, max_x, max_y



def save_best_images(folder_path, best_images, best_filenames):
    # Create a new folder named 'best_images' in the parent folder of folder_path
    parent_folder = os.path.dirname(folder_path)
    new_folder_path = os.path.join(parent_folder, 'best_images')

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    i = 0
    # Sort the keys by y first, then by x
    sorted_keys = sorted(best_images.keys(), key=lambda k: (k[1], k[0]))

    # Iterate through the sorted keys
    for (x, y) in sorted_keys:
        image = best_images[(x, y)]
        # Get the new filename corresponding to this (x, y) pair from best_filenames
        new_filename = best_filenames.get((x, y), f"Unknown-X{x}-Y{y}.tif")
        new_filename = new_filename.split('-Slice')[0]
        new_filename = f"{new_filename}-Slice-{i}.tif"
        # Create the full path for the new file
        new_file_path = os.path.join(new_folder_path, new_filename)
        i += 1
        # Save the image
        imwrite(new_file_path, image)

    print(f"Best images have been saved in the folder: {new_folder_path}")


def prime_images(folder_path):
    first_images = {}
    first_filenames = {}  # To store the modified filenames
    
    max_x = -1  # Variable to hold maximum x value
    max_y = -1  # Variable to hold maximum y value

    if not folder_path:
        print("No folder selected. Exiting.")
        return first_images, None

    filenames = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # Group filenames by XY position
    xy_positions = defaultdict(list)
    for filename in filenames:
        x_match = re.search(r'-X(\d+)-', filename)
        y_match = re.search(r'-Y(\d+)-', filename)
        z_match = re.search(r'-Z(\d+)-', filename)

        x = int(x_match.group(1)) if x_match else 0
        y = int(y_match.group(1)) if y_match else 0
        z = int(z_match.group(1)) if z_match else 0

        # Only consider the first image (Z=001) for each XY position
        if z == 1:
            xy_positions[(x, y)].append(filename)

    for xy_position, filenames in xy_positions.items():
        x, y = xy_position

        # Update maximum x and y if necessary
        max_x = max(max_x, x)
        max_y = max(max_y, y)

        # Select the first image (Z=001) for each XY position
        first_image_path = os.path.join(folder_path, filenames[0])
        first_image = tifffile.imread(first_image_path)

        if first_image is None:
            print(f"Failed to load {filenames[0]}. Skipping.")
            continue

        # Create the new filename based on your specifications
        base_name = filenames[0].split('-Slice')[0]  # Assuming all filenames share the same base name
        new_filename = f"{base_name}_FirstZ"  # Adjust the new filename as needed
        first_filenames[(x, y)] = new_filename  # Store the new filename

        # Store the first image for each XY position
        first_images[(x, y)] = first_image

    return first_images, first_filenames


def save_first_images(folder_path, best_images, best_filenames):
    
    i = 0

    # Sort the keys by y first, then by x
    sorted_keys = sorted(best_images.keys(), key=lambda k: (k[1], k[0]))

    # Iterate through the sorted keys
    for (x, y) in sorted_keys:
        image = best_images[(x, y)]
        # Get the new filename corresponding to this (x, y) pair from best_filenames
        new_filename = best_filenames.get((x, y), f"Unknown-X{x}-Y{y}.tif")
        new_filename = new_filename.split('-Slice')[0]
        new_filename = f"{new_filename}-Slice-{i}.tif"
        # Create the full path for the new file
        new_file_path = os.path.join(prime_folder_path, new_filename)
        i += 1
        # Save the image
        imwrite(new_file_path, image)

    print(f"Best images have been saved in the folder: {prime_folder_path}")


### ImageJ initialization ###
scyjava.config.add_options('-Xmx14g')
ij = imagej.init('sc.fiji:fiji:2.5.0')

ij.getApp().getInfo(True)


### Directory choice ###
## Input directory ##
root = tk.Tk()
root.withdraw()

folder_path = filedialog.askdirectory(title='Select the folder containing the image stack')
if not folder_path:
    print("No folder selected. Exiting.")
    exit()

## Output Directory ##
root = tk.Tk()
root.withdraw()

output_path = filedialog.askdirectory(title='Select the directory output')
if not output_path:
    print("No folder selected. Exiting.")
    exit()
    
output_dir = os.path.join(output_path, 'Results')

overlap = int(input("Enter the overlap of the stitching (%):"))

# Create a new folder named 'best_images' in the parent folder of folder_path
parent_folder = os.path.dirname(folder_path)

if chosen_analysis == "Z Projection":
    best_images, best_filenames, max_x, max_y = process_images(folder_path)

if chosen_analysis == "Most Sharp Image":
    best_images, best_scores, _, best_filenames, max_x, max_y = process_images(folder_path)

new_folder_path = os.path.join(output_dir, 'best_images')

if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)

save_best_images(new_folder_path, best_images, best_filenames)

print(max_x, max_y)

# Get the first array (image) from the dictionary
first_image_array = list(best_images.values())[0]

# Get the height and width of the image
height, width = first_image_array.shape[:2]  # Assuming the image is 2D (no channels)

# Print the height and width
print("Height of the image:", height)
print("Width of the image:", width)

# Charger la pile d'images en z
img_stack = np.ndarray(shape=(0, height, width))

# Create a tqdm loading bar
with tqdm(total=len(os.listdir(new_folder_path)), desc="Loading Images") as pbar:
    for file_name in sorted(os.listdir(new_folder_path)):
        if file_name.endswith(".tif"):
            img = tifffile.imread(os.path.join(new_folder_path, file_name))
            img_stack = np.concatenate((img_stack, [img]))

            # Update the loading bar
            pbar.update(1)

len_grid = max_x * max_y

# Now, you can proceed with BaSiC processing
basic = BaSiC(get_darkfield=True, smoothness_flatfield=1)
basic.fit(img_stack)

images_transformed = basic.transform(img_stack)

# Save each image individually in the "shaded_images" folder
shaded_images_folder = os.path.join(output_dir, "shaded_images")
os.makedirs(shaded_images_folder, exist_ok=True)

def apply_clahe_to_stack(image_stack, clip_limit=20, grid_size=(5, 5)):
    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    
    # Initialize an empty stack to store enhanced images
    enhanced_stack = []
    
    # Apply CLAHE to each image in the stack
    for img in image_stack:
        # Convert the image to uint16 for CLAHE operation
        img_uint16 = img.astype(np.uint16)
        
        # Apply CLAHE
        enhanced_img_uint16 = clahe.apply(img_uint16)
        
        # Add the enhanced image to the stack
        enhanced_stack.append(enhanced_img_uint16)
    
    return enhanced_stack

# Assuming images_transformed is a NumPy array representing the image stack
enhanced_stack = apply_clahe_to_stack(images_transformed)


for i, original_image_path in enumerate(sorted(os.listdir(new_folder_path))):
    original_image_path = os.path.join(new_folder_path, original_image_path)
    original_image_name = os.path.basename(original_image_path)
    original_image_name = os.path.splitext(original_image_name)[0]
    
    new_filename = f"{original_image_name}.tif"
    shaded_image_path = os.path.join(shaded_images_folder, new_filename)
    
    tifffile.imwrite(shaded_image_path, enhanced_stack[i])

print(f"Shaded images saved in the folder: {shaded_images_folder}")

for key, value in best_filenames.items():
    new_value = value.split('-Slice')[0]
    best_filenames[key] = f"{new_value}-Slice"
name = str(new_value + "-Slice-{i}.tif")

if overlap > 0:
    compute = True
else:
    compute = False
plugin = "Grid/Collection stitching"

args = {
        "type": "[Grid: row-by-row]",
        "order": "[Right & Down]",
        "grid_size_x": max_x,
        "grid_size_y": max_y,
        "tile_overlap": overlap,
        "first_file_index_i": "0",
        "directory": shaded_images_folder,
        "file_names": name,
        "output_textfile_name": "TileConfiguration.txt",
        "fusion_method": "[Linear Blending]",
        "regression_threshold": "0.3",
        "max/avg_displacement_threshold": "10",
        "absolute_displacement_threshold": "10",
        "computation_parameters": "[Save memory (but be slower)]",
        "image_output": "[Fuse and display]",
    }

total_grids = max_x * max_y 

ij.py.run_plugin(plugin, args)
# Capture the currently active image
active_img = ij.WindowManager.getCurrentImage()

# Convert to a numpy array or some other format you prefer
active_img_np = ij.py.from_java(active_img)

# Create the full path for the new TIFF file
tif_file_path = os.path.join(output_dir, new_value + '_shaded_stitched_image.tif')

# Save the NumPy array as a TIFF file
imwrite(tif_file_path, active_img_np)

print(f"The stitched image has been saved as a TIFF file in the folder: {output_dir}")



# Specify the input and output file paths
input_file = os.path.join(shaded_images_folder, "TileConfiguration.txt")
output_file = os.path.join(new_folder_path, "TileConfiguration.txt")

# Read the contents of the input file
with open(input_file, "r") as f:
    text = f.read()

# Write the modified text back to the output file
with open(output_file, "w") as f:
    f.write(text)

print("Replacement complete. Output saved to", output_file)

## Save a stitch image of the best images or the z projection unchanged
args = {
        "type": "[Positions from file]",
        "order": "[Defined by TileConfiguration]",
        "layout_file": "TileConfiguration.txt",
        "directory": new_folder_path,
        "file_names": name,
        "output_textfile_name": "TileConfiguration.txt",
        "fusion_method": "[Linear Blending]",
        "regression_threshold": "0.30",
        "max/avg_displacement_threshold": "2.50",
        "absolute_displacement_threshold": "3.50",
        "computation_parameters": "[Save memory (but be slower)]",
        "image_output": "[Fuse and display]",
    }

total_grids = max_x * max_y 

ij.py.run_plugin(plugin, args)

# Capture the currently active image
active_img = ij.WindowManager.getCurrentImage()

# Convert to a numpy array or some other format you prefer
active_img_np = ij.py.from_java(active_img)

# Create the full path for the new TIFF file
tif_file_path = os.path.join(output_dir, new_value + '_stitched_best_image.tif')

# Save the NumPy array as a TIFF file
imwrite(tif_file_path, active_img_np)

print(f"The stitched first image has been saved as a TIFF file in the folder: {output_dir}")


# Create a new folder named 'first_images' in the parent folder of folder_path
prime_folder_path = os.path.join(output_dir, 'first_images')

if not os.path.exists(prime_folder_path):
    os.makedirs(prime_folder_path)

# Create a new folder named 'first_images_shaded' in the parent folder of folder_path
second_folder_path = os.path.join(output_dir, 'first_images_shaded')

if not os.path.exists(second_folder_path):
    os.makedirs(second_folder_path)

# Call the function and retrieve the results
first_images, first_filenames = prime_images(folder_path)

save_first_images(prime_folder_path, first_images, first_filenames)

# Charger la pile d'images en z
first_stack = np.ndarray(shape=(0, height, width))  # Assuming images are 512x512, adjust accordingly

# Create a tqdm loading bar
with tqdm(total=len(os.listdir(prime_folder_path)), desc="Loading Images") as pbar:
    for file_name in sorted(os.listdir(prime_folder_path)):
        if file_name.endswith(".tif"):
            img = tifffile.imread(os.path.join(prime_folder_path, file_name))
            first_stack = np.concatenate((first_stack, [img]))

            # Update the loading bar
            pbar.update(1)

# Now, you can proceed with BaSiC processing
basic = BaSiC(get_darkfield=True, smoothness_flatfield=1)
basic.fit(first_stack)

first_transformed = basic.transform(first_stack)

for i, original_image_path in enumerate(sorted(os.listdir(prime_folder_path))):
    original_image_path = os.path.join(prime_folder_path, original_image_path)
    original_image_name = os.path.basename(original_image_path)
    original_image_name = os.path.splitext(original_image_name)[0]
    
    new_filename = f"{original_image_name}.tif"
    second_image_path = os.path.join(second_folder_path, new_filename)
    
    tifffile.imwrite(second_image_path, first_transformed[i])

print(f"Transformed images saved in the folder: {second_folder_path}")

# Specify the input and output file paths
input_file = os.path.join(shaded_images_folder, "TileConfiguration.txt")
output_file = os.path.join(second_folder_path, "TileConfiguration.txt")

# Read the contents of the input file
with open(input_file, "r") as f:
    text = f.read()

# Replace "zProjection" with "FirstZ"
modified_text = text.replace("zProjection", "FirstZ")

# Write the modified text back to the output file
with open(output_file, "w") as f:
    f.write(modified_text)

print("Replacement complete. Output saved to", output_file)

args = {
        "type": "[Positions from file]",
        "order": "[Defined by TileConfiguration]",
        "layout_file": "TileConfiguration.txt",
        "directory": second_folder_path,
        "file_names": name,
        "output_textfile_name": "TileConfiguration.txt",
        "fusion_method": "[Linear Blending]",
        "regression_threshold": "0.30",
        "max/avg_displacement_threshold": "2.50",
        "absolute_displacement_threshold": "3.50",
        "computation_parameters": "[Save memory (but be slower)]",
        "image_output": "[Fuse and display]",
    }

ij.py.run_plugin(plugin, args)

# Capture the currently active image
active_img = ij.WindowManager.getCurrentImage()

# Convert to a numpy array or some other format you prefer
active_img_np = ij.py.from_java(active_img)
# Create the full path for the new TIFF file
tif_file_path = os.path.join(output_dir, new_value + '_stitched_first_image.tif')

# Save the NumPy array as a TIFF file
imwrite(tif_file_path, active_img_np)

print(f"The stitched first image has been saved as a TIFF file in the folder: {output_dir}")



#### MIST parameters if needed ####
print("MIST parameters:")
print(f"Grid Width: {max_x}")
print(f"Grid Height: {max_y}")
filename_mist = name.replace("{i}", "{p}")
print(f"Filename Pattern: {filename_mist}")
print(f"Image Directory: {new_folder_path}")
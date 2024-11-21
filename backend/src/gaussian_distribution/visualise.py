import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import math

def update_png(grid, disp, max_val, img_data):
    rows, cols = grid.shape
    
    # Calculate min based on max - use log to band
    bands = 10  # Замените это значение на ваше реальное количество банд
    min_val = math.trunc(math.log10(max_val)) - bands
   
    # Normalise 2d grid into bands by taking log
    for y in range(rows):
        for x in range(cols):
            if grid[y, x] > 0.0:
                disp[y, x] = math.trunc(math.log10(grid[y, x]))
            else:
                disp[y, x] = min_val

    # Construct an image of the given width and height
    img_data = np.zeros((rows, cols, 4), dtype=np.uint8)  # RGBA format

    for y in range(rows):
        for x in range(cols):
            # Default pixel set to white
            pixelR = 255
            pixelG = 255
            pixelB = 255
            
            # Set shade of blue if concentration meets criteria
            if disp[y, x] > min_val:
                conc = (disp[y, x] - min_val) / bands
                pixelR = int(255 - 255 * conc)
                pixelG = int(255 - 255 * conc)
                pixelB = 255

            img_data[y, x] = [pixelR, pixelG, pixelB, 255]  # Alpha channel set to 255 (opaque)

    return img_data

def generate_png(grid, max_val):
    # Calculate grid dimensions
    rows, cols = grid.shape

    # Create an empty image data array
    disp = np.zeros((rows, cols), dtype=int)

    # Update imgData array inplace with rendered image
    img_data = update_png(grid, disp, max_val, None)
    
    return img_data

def export_png(data, target_id):
    # В данном контексте функция может быть использована для отображения изображения в веб-приложении.
    print(f"Image data for {target_id}: {data}")


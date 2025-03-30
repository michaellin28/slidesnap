from PIL import Image
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect

def get_screenshot(region):
    """Capture a screenshot of the specified region."""
    if not region:
        return None
        
    x, y, width, height = region
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(0, x, y, width, height)
    
    # Convert to PIL Image
    buffer = screenshot.toImage()
    size = buffer.size()
    ptr = buffer.bits()
    # Ensure the size is correct for the buffer format
    bytes_per_line = buffer.bytesPerLine()
    num_bytes = bytes_per_line * size.height()
    ptr.setsize(num_bytes)
    
    # Create numpy array
    arr = np.frombuffer(ptr, np.uint8).reshape((size.height(), bytes_per_line))
    
    # Determine the number of channels based on format
    # Common formats might be Format_RGB32 (BGRA) or Format_ARGB32 (BGRA)
    # We need to extract RGB correctly
    if buffer.format() in (buffer.Format.Format_RGB32, buffer.Format.Format_ARGB32, buffer.Format.Format_ARGB32_Premultiplied):
        # Assuming BGRA format based on common Qt behavior
        # Slice to remove alpha and swap B and R channels
        arr = arr[:, :size.width() * 4].reshape((size.height(), size.width(), 4))
        rgb_arr = arr[:, :, [2, 1, 0]] # Select B, G, R and reorder to R, G, B
    elif buffer.format() == buffer.Format.Format_RGB888:
        # Assuming RGB format
        arr = arr[:, :size.width() * 3].reshape((size.height(), size.width(), 3))
        rgb_arr = arr # Already RGB
    else:
        # Fallback or handle other formats if necessary
        print(f"Warning: Unhandled QImage format {buffer.format()}. Attempting default conversion.")
        # Default attempt, might have wrong colors
        arr = arr[:, :size.width() * 4].reshape((size.height(), size.width(), 4))
        rgb_arr = arr[:, :, :3]

    return Image.fromarray(rgb_arr)

def compare_images(img1, img2, threshold=0.95):
    """Compare two images and return True if they are significantly different."""
    if img1 is None or img2 is None:
        return True
        
    # Convert to numpy arrays and calculate difference
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    if arr1.shape != arr2.shape:
        return True
    
    # Calculate Mean Squared Error (MSE)
    err = np.sum((arr1.astype("float") - arr2.astype("float")) ** 2)
    err /= float(arr1.shape[0] * arr1.shape[1] * arr1.shape[2]) # Divide by total number of pixel values (width * height * channels)
    
    # Define an MSE threshold for difference (lower = more sensitive)
    # Increased from 100 to 500 to make it less sensitive
    mse_threshold = 500 
    
    # If MSE is above the threshold, images are considered different
    return err > mse_threshold

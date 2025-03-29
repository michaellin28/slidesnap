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
    ptr.setsize(size.height() * size.width() * 4)
    arr = np.frombuffer(ptr, np.uint8).reshape((size.height(), size.width(), 4))
    return Image.fromarray(arr[:, :, :3])  # Convert RGBA to RGB

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

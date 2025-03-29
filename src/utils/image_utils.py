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
    
    diff = np.abs(arr1 - arr2)
    max_diff = np.max(diff)
    
    # If maximum difference is small, images are similar
    return max_diff > (255 * (1 - threshold))

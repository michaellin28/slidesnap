import time
from datetime import datetime
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
from PIL import Image
from ..utils.image_utils import get_screenshot, compare_images

class ScreenMonitor(QThread):
    screenshot_taken = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.region = None
        self.captured_images = []
        self.last_image = None
        self.output_dir = None
        
    def set_region(self, region):
        self.region = region
    
    def has_region(self):
        return self.region is not None
    
    def get_captured_images(self):
        return self.captured_images
    
    def start(self, pdf_enabled=True, images_per_page=1, pdf_directory="Default"):
        if pdf_directory == "Default":
            pdf_directory = os.path.expanduser("~/Desktop")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(pdf_directory, f"capture_{timestamp}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.captured_images = []
        self.running = True
        super().start()
    
    def stop(self):
        self.running = False
        self.wait()
    
    def run(self):
        while self.running:
            current_image = get_screenshot(self.region)
            
            if self.last_image is None or compare_images(current_image, self.last_image):
                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = os.path.join(self.output_dir, f"screenshot_{timestamp}.png")
                current_image.save(filename)
                self.captured_images.append(filename)
                self.screenshot_taken.emit(filename)
                self.last_image = current_image
            
            time.sleep(0.25)  # Increased monitoring frequency delay to 0.5 seconds

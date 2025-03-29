import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

class PDFCompiler:
    def __init__(self):
        self.page_width, self.page_height = letter
        self.margin = 50
        
    def generate(self, image_paths, images_per_page, output_dir):
        if not image_paths:
            return
            
        # Create PDF filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(output_dir, f"capture_{timestamp}.pdf")
        
        # Initialize PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Calculate image placement based on layout
        if images_per_page == 1:
            positions = [(self.margin, self.margin)]
            max_width = self.page_width - (2 * self.margin)
            max_height = self.page_height - (2 * self.margin)
        elif images_per_page == 2:
            positions = [
                (self.margin, self.page_height/2 + self.margin/2),
                (self.margin, self.margin)
            ]
            max_width = self.page_width - (2 * self.margin)
            max_height = (self.page_height - (3 * self.margin)) / 2
        else:  # 4 images per page
            positions = [
                (self.margin, self.page_height/2 + self.margin/2),
                (self.page_width/2 + self.margin/2, self.page_height/2 + self.margin/2),
                (self.margin, self.margin),
                (self.page_width/2 + self.margin/2, self.margin)
            ]
            max_width = (self.page_width - (3 * self.margin)) / 2
            max_height = (self.page_height - (3 * self.margin)) / 2
        
        # Process images
        current_position = 0
        for image_path in image_paths:
            if current_position == 0:
                c.showPage()
            
            try:
                with Image.open(image_path) as img:
                    # Calculate scaling to fit in available space
                    width, height = img.size
                    scale = min(max_width/width, max_height/height)
                    scaled_width = width * scale
                    scaled_height = height * scale
                    
                    # Center image in its allocated space
                    x, y = positions[current_position]
                    x += (max_width - scaled_width) / 2
                    y += (max_height - scaled_height) / 2 if images_per_page > 1 else 0
                    
                    # Draw image
                    c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
            
            current_position = (current_position + 1) % images_per_page
        
        c.save()

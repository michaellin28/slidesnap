import os
import time # Added for potential delay simulation if needed
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal

class PDFCompiler(QObject):
    progress_updated = pyqtSignal(int)  # Signal for progress percentage
    finished = pyqtSignal(str)         # Signal for completion (path or error)

    def __init__(self):
        super().__init__()
        self.page_width, self.page_height = letter
        self.margin = 50
        self._image_paths = []
        self._images_per_page = 1
        self._output_dir = ""

    def set_params(self, image_paths, images_per_page, output_dir):
        """Set parameters before running generation in a thread."""
        self._image_paths = image_paths
        self._images_per_page = images_per_page
        self._output_dir = output_dir

    def run_generation(self):
        """This method will be run in a separate thread."""
        if not self._image_paths:
            self.finished.emit("Error: No images to compile.")
            return

        # Create PDF filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(self._output_dir, f"capture_{timestamp}.pdf")

        try:
            # Initialize PDF - Default to letter size
            c = canvas.Canvas(pdf_path, pagesize=letter)
            total_images = len(self._image_paths)

            # --- Special handling for 4 or 2 images per page (custom page size) ---
            if self._images_per_page == 4 or self._images_per_page == 2:
                batch_size = self._images_per_page
                for i in range(0, total_images, batch_size):
                    batch_paths = self._image_paths[i:min(i + batch_size, total_images)]
                    if not batch_paths:
                        continue

                    # Determine page size from the first image in the batch
                    try:
                        with Image.open(batch_paths[0]) as img:
                            img_width, img_height = img.size
                    except Exception as e:
                        print(f"Error opening image {batch_paths[0]} to determine page size: {e}")
                        # Fallback or skip? Let's skip this batch for now.
                        # Emit progress for skipped images
                        for k in range(len(batch_paths)):
                             progress_percent = int(((i + k + 1) / total_images) * 100)
                             self.progress_updated.emit(progress_percent)
                        continue

                    # Calculate custom page size (tightly packed)
                    if batch_size == 4:
                        page_width = img_width * 2
                        page_height = img_height * 2
                        # Define quadrant positions (0,0 is bottom-left in reportlab)
                        # Order: Top-Left, Top-Right, Bottom-Left, Bottom-Right
                        positions = [
                            (0, page_height / 2),
                            (page_width / 2, page_height / 2),
                            (0, 0),
                            (page_width / 2, 0)
                        ]
                        quad_width = page_width / 2
                        quad_height = page_height / 2
                    else: # batch_size == 2
                        page_width = img_width
                        page_height = img_height * 2
                        # Define positions: Top, Bottom
                        positions = [
                            (0, page_height / 2),
                            (0, 0)
                        ]
                        quad_width = page_width
                        quad_height = page_height / 2

                    c.setPageSize((page_width, page_height))

                    # Draw images in the batch
                    for j, img_path in enumerate(batch_paths):
                        try:
                            with Image.open(img_path) as img:
                                # Scale image to fit quadrant
                                width, height = img.size
                                scale = min(quad_width / width, quad_height / height, 1.0) # Don't scale up
                                scaled_width = width * scale
                                scaled_height = height * scale

                                # Position within quadrant (bottom-left corner of image)
                                x, y = positions[j]
                                # Center within quadrant (optional, for now just place at corner)
                                # x += (quad_width - scaled_width) / 2
                                # y += (quad_height - scaled_height) / 2

                                c.drawImage(img_path, x, y, width=scaled_width, height=scaled_height)
                        except Exception as e:
                            print(f"Error processing image {img_path}: {e}")

                        # Emit progress based on overall index
                        progress_percent = int(((i + j + 1) / total_images) * 100)
                        self.progress_updated.emit(progress_percent)

                    c.showPage() # Finalize the custom page

            # --- Handling for 1 image per page (standard letter size) ---
            else: # self._images_per_page == 1
                positions = [(self.margin, self.margin)]
                max_width = self.page_width - (2 * self.margin)
                max_height = self.page_height - (2 * self.margin)

                # Process images one by one
                for i, image_path in enumerate(self._image_paths):
                    # Add a new page for every image
                    if i > 0:
                        c.showPage()
                    # Ensure page size is letter
                    c.setPageSize(letter)

                    try:
                        with Image.open(image_path) as img:
                            # Calculate scaling to fit in available space
                            width, height = img.size
                            scale = min(max_width / width, max_height / height, 1.0) # Don't scale up
                            scaled_width = width * scale
                            scaled_height = height * scale

                            # Center image in its allocated space
                            x, y = positions[0] # Only one position for 1 image/page
                            x += (max_width - scaled_width) / 2
                            y += (max_height - scaled_height) / 2 # Center vertically too

                            # Draw image
                            c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
                    except Exception as e:
                        print(f"Error processing image {image_path}: {e}")

                    # Emit progress
                    progress_percent = int(((i + 1) / total_images) * 100)
                    self.progress_updated.emit(progress_percent)

            # Save the PDF after all processing is done
            c.save()
            self.finished.emit(f"PDF generated: {pdf_path}")

        except Exception as e:
            self.finished.emit(f"Error generating PDF: {e}")

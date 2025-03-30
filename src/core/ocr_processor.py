import os
import subprocess
import shutil
from PyQt6.QtCore import QObject, pyqtSignal

class OCRProcessor(QObject):
    finished = pyqtSignal(str)  # Signal for completion (output path or error)

    def __init__(self):
        super().__init__()
        self._input_pdf_path = ""
        self._output_pdf_path = ""

    def set_params(self, input_pdf_path, output_pdf_path):
        """Set parameters before running OCR in a thread."""
        self._input_pdf_path = input_pdf_path
        self._output_pdf_path = output_pdf_path

    def run_ocr(self):
        """Runs the ocrmypdf command-line tool."""
        if not self._input_pdf_path or not self._output_pdf_path:
            self.finished.emit("Error: Missing input or output path for OCR.")
            return

        # Check if ocrmypdf command exists
        if not shutil.which("ocrmypdf"):
             self.finished.emit("Error: 'ocrmypdf' command not found. Please install OCRmyPDF.")
             # Optionally delete the non-OCR'd PDF? For now, keep it.
             # try:
             #     os.remove(self._input_pdf_path)
             # except OSError as e:
             #     print(f"Could not remove intermediate PDF: {e}")
             return

        try:
            # Construct the command
            # Add options as needed, e.g., --force-ocr, --language eng
            command = [
                "ocrmypdf",
                self._input_pdf_path,
                self._output_pdf_path
                # Add more arguments here if necessary, e.g., "--language", "eng"
            ]

            # Run the command
            process = subprocess.run(command, capture_output=True, text=True, check=True)

            # If successful, delete the original non-OCR PDF
            try:
                os.remove(self._input_pdf_path)
            except OSError as e:
                print(f"Warning: Could not remove original non-OCR PDF: {e}")

            self.finished.emit(f"OCR PDF generated: {self._output_pdf_path}")

        except subprocess.CalledProcessError as e:
            # Command failed
            error_message = f"Error during OCR: {e.stderr}"
            # Attempt to clean up potentially incomplete output file
            if os.path.exists(self._output_pdf_path):
                try:
                    os.remove(self._output_pdf_path)
                except OSError:
                    pass # Ignore cleanup error
            self.finished.emit(error_message)
        except Exception as e:
            # Other potential errors
            self.finished.emit(f"Unexpected error during OCR: {e}")

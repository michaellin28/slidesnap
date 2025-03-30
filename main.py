import sys
import os # Added for path joining
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon # Added QIcon
from src.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set Application Name (for Dock, etc.)
    app.setApplicationName("SlideSnap")
    app.setApplicationDisplayName("SlideSnap") # Optional, often same as name
    
    # Set application icon
    script_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(script_dir, 'assets', 'screenpdficon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Icon file not found at {icon_path}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

import sys
import darkdetect
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QApplication,
                               QLabel, QSpinBox, QCheckBox, QFileDialog, QComboBox,
                               QHBoxLayout, QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread
from PyQt6.QtGui import QPalette, QColor # Re-added for theme palettes
from .region_selector import RegionSelector
from ..core.monitor import ScreenMonitor
from ..core.pdf_compiler import PDFCompiler

# Define basic palettes
def light_palette():
    # Create a default palette and return it (usually sufficient for light mode)
    return QPalette()

def dark_palette():
    # Create a dark palette based on common dark theme colors
x    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    # Disabled states
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
    return palette

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture to PDF")
        self.setMinimumWidth(400)

        # Make window stay on top, use standard frame
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Initialize components
        self.monitor = ScreenMonitor()
        self.settings = QSettings('ScreenCapturePDF', 'Settings')
        self.pdf_thread = None
        self.pdf_compiler_worker = None

        # Setup UI
        self.setup_ui()
        # Load settings and apply initial theme *after* UI is set up
        self.load_settings()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Region selection
        region_group = QGroupBox("Region Selection")
        region_layout = QVBoxLayout()
        self.select_region_btn = QPushButton("Select Region")
        self.select_region_btn.clicked.connect(self.select_region)
        self.region_label = QLabel("No region selected")
        region_layout.addWidget(self.select_region_btn)
        region_layout.addWidget(self.region_label)
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)

        # Theme Selection
        theme_group = QGroupBox("Appearance")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.apply_theme) # Connect signal
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Timer settings
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(QLabel("Delay before recording (seconds):"))
        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(0, 10)
        self.timer_spinbox.setValue(3)  # Default 3 seconds
        timer_layout.addWidget(self.timer_spinbox)
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)

        # PDF settings
        pdf_group = QGroupBox("PDF Settings")
        pdf_layout = QVBoxLayout()

        self.enable_pdf_cb = QCheckBox("Generate PDF after session")
        self.enable_pdf_cb.setChecked(True)

        layout_selection = QHBoxLayout()
        layout_selection.addWidget(QLabel("Images per page:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["1", "2", "4"])
        self.layout_combo.setCurrentText("4") # Default to 4 images per page
        layout_selection.addWidget(self.layout_combo)

        pdf_output = QHBoxLayout()
        self.pdf_path_btn = QPushButton("PDF Output Directory")
        self.pdf_path_btn.clicked.connect(self.select_pdf_directory)
        self.pdf_path_label = QLabel("Default")
        pdf_output.addWidget(self.pdf_path_btn)
        pdf_output.addWidget(self.pdf_path_label)

        pdf_layout.addWidget(self.enable_pdf_cb)
        pdf_layout.addLayout(layout_selection)
        pdf_layout.addLayout(pdf_output)
        pdf_group.setLayout(pdf_layout)
        layout.addWidget(pdf_group)

        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

        # Status and Progress Bar
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False) # Initially hidden
        status_layout.addWidget(self.progress_bar)
        layout.addLayout(status_layout)

    def apply_theme(self, theme_choice):
        """Applies the selected theme (Light/Dark/System) using QPalette."""
        app = QApplication.instance()
        if not app: # Should not happen in a running app
            return
            
        effective_theme = theme_choice.lower()

        if effective_theme == "system":
            system_theme = darkdetect.theme()
            if system_theme: # darkdetect returns None if it can't detect
                effective_theme = system_theme.lower()
            else:
                effective_theme = "light" # Default to light if detection fails

        if effective_theme == "dark":
            app.setPalette(dark_palette())
        else: # Light or undetected system
            app.setPalette(light_palette()) # Use default light palette

        # Save the user's *choice* (System, Light, Dark), not the effective theme
        self.settings.setValue('theme', theme_choice)

    def load_settings(self):
        pdf_dir = self.settings.value('pdf_directory', 'Default')
        self.pdf_path_label.setText(pdf_dir)

        # Load theme setting
        saved_theme = self.settings.value('theme', 'System') # Default to System
        # Set combo box value without triggering apply_theme again
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(saved_theme)
        self.theme_combo.blockSignals(False)
        # Apply the theme based on the loaded setting
        self.apply_theme(saved_theme)


    def select_region(self):
        # No need to hide/show main window
        selector = RegionSelector()
        if selector.exec():
            region = selector.get_region()
            self.monitor.set_region(region)
            self.region_label.setText(f"Region: {region[2]}x{region[3]}")

    def select_pdf_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select PDF Output Directory")
        if directory:
            self.pdf_path_label.setText(directory)
            self.settings.setValue('pdf_directory', directory)

    def start_monitoring(self):
        if not self.monitor.has_region():
            # Automatically open region selector if none is selected
            self.status_label.setText("Please select a region.")
            self.select_region()
            # If a region was selected after the dialog, proceed. Otherwise, stop here.
            if not self.monitor.has_region():
                return

        delay_seconds = self.timer_spinbox.value()

        if delay_seconds > 0:
            self.status_label.setText(f"Starting in {delay_seconds} seconds...")
            self.start_btn.setEnabled(False)
            self.select_region_btn.setEnabled(False)

            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_remaining = delay_seconds
            self.countdown_timer.start(1000)
        else:
            self.actually_start_monitoring()

    def update_countdown(self):
        self.countdown_remaining -= 1
        if self.countdown_remaining <= 0:
            self.countdown_timer.stop()
            self.actually_start_monitoring()
        else:
            self.status_label.setText(f"Starting in {self.countdown_remaining} seconds...")

    def actually_start_monitoring(self):
        self.monitor.start(
            pdf_enabled=self.enable_pdf_cb.isChecked(),
            images_per_page=int(self.layout_combo.currentText()),
            pdf_directory=self.pdf_path_label.text()
        )

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_region_btn.setEnabled(False)
        self.status_label.setText("Monitoring...")

    def stop_monitoring(self):
        captured_images = self.monitor.get_captured_images()
        self.monitor.stop()

        if self.enable_pdf_cb.isChecked() and captured_images:
            self.status_label.setText("Preparing PDF generation...")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.select_region_btn.setEnabled(False)

            self.pdf_thread = QThread()
            self.pdf_compiler_worker = PDFCompiler()
            self.pdf_compiler_worker.set_params(
                captured_images,
                int(self.layout_combo.currentText()),
                self.pdf_path_label.text()
            )
            self.pdf_compiler_worker.moveToThread(self.pdf_thread)

            # Connect signals for thread management and UI updates
            self.pdf_thread.started.connect(self.pdf_compiler_worker.run_generation)
            self.pdf_compiler_worker.progress_updated.connect(self.update_pdf_progress)
            self.pdf_compiler_worker.finished.connect(self.pdf_generation_finished) # Slot to update UI
            self.pdf_compiler_worker.finished.connect(self.pdf_thread.quit) # Tell thread's event loop to exit
            # Use thread's finished signal for safe cleanup AFTER its event loop stops
            self.pdf_thread.finished.connect(self.pdf_thread.deleteLater)
            self.pdf_thread.finished.connect(self.pdf_compiler_worker.deleteLater)

            self.pdf_thread.start()
            self.status_label.setText("Generating PDF...")

        else:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.select_region_btn.setEnabled(True)
            self.status_label.setText("Monitoring stopped.")

    def update_pdf_progress(self, value):
        """Slot to update the progress bar."""
        self.progress_bar.setValue(value)

    def pdf_generation_finished(self, result_message):
        """Slot called when PDF generation WORK is done (runs in main thread)."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(result_message)

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_region_btn.setEnabled(True)

        # Clear Python references - thread/worker will be deleted later by connections
        # DO NOT call wait() here as it blocks the main thread!
        self.pdf_thread = None
        self.pdf_compiler_worker = None

    def closeEvent(self, event):
        # Ensure monitor and potentially PDF thread are stopped on close
        self.monitor.stop()
        if self.pdf_thread and self.pdf_thread.isRunning():
            print("Warning: Closing while PDF generation is in progress.")
            # Force quit and wait briefly
            self.pdf_thread.quit()
            self.pdf_thread.wait(500) # Wait 0.5 sec for thread to finish quitting
        event.accept()

    # --- Removed change_opacity, mousePressEvent, mouseMoveEvent ---

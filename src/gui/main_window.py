import sys
import os
import darkdetect
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QApplication,
                               QLabel, QSpinBox, QCheckBox, QFileDialog, QComboBox,
                               QHBoxLayout, QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread
from .region_selector import RegionSelector
from ..core.monitor import ScreenMonitor
from ..core.pdf_compiler import PDFCompiler
from ..core.ocr_processor import OCRProcessor

# Define macOS-like stylesheets
LIGHT_STYLESHEET = """
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f5f5f7;
    color: #1d1d1f;
}
QMainWindow {
    background-color: #f5f5f7;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px; /* Reduced top padding */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px 0px 5px;
    margin-left: 5px;
    color: #6e6e73;
    font-weight: normal;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #d2d2d7;
    padding: 5px 15px;
    border-radius: 5px;
    color: #007aff;
    font-weight: normal;
}
QPushButton:hover {
    background-color: #e9e9ed;
}
QPushButton:pressed {
    background-color: #dcdce1;
}
QPushButton:disabled {
    background-color: #f5f5f7;
    color: #c6c6c8;
    border-color: #e1e1e6;
}
QLabel {
    background-color: transparent;
    color: #1d1d1f;
}
QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d2d2d7;
    padding: 5px 8px;
    border-radius: 5px; /* Explicitly ensure radius */
    min-height: 22px;
}
QComboBox {
    padding-left: 8px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox::down-arrow {
    /* image: url(assets/down_arrow_light.png); */
    width: 12px;
    height: 12px;
}
QCheckBox {
    spacing: 5px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #c6c6c8;
    background-color: #ffffff;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #007aff;
    border: 1px solid #007aff;
    border-radius: 4px;
    /* image: url(assets/checkmark_light.png); */
}
QProgressBar {
    border: 1px solid #d2d2d7;
    border-radius: 5px;
    text-align: center;
    color: #1d1d1f;
    background-color: #e9e9ed;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #007aff;
    border-radius: 5px;
}
"""

DARK_STYLESHEET = """
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #1c1c1e;
    color: #ffffff;
}
QMainWindow {
    background-color: #1c1c1e;
}
QGroupBox {
    background-color: #2c2c2e;
    border: 1px solid #3a3a3c;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px; /* Reduced top padding */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px 0px 5px;
    margin-left: 5px;
    color: #8e8e93;
    font-weight: normal;
}
QPushButton {
    background-color: #3a3a3c;
    border: 1px solid #545458;
    padding: 5px 15px;
    border-radius: 5px;
    color: #0a84ff;
    font-weight: normal;
}
QPushButton:hover {
    background-color: #4a4a4c;
}
QPushButton:pressed {
    background-color: #5a5a5e;
}
QPushButton:disabled {
    background-color: #2c2c2e;
    color: #5a5a5e;
    border-color: #3a3a3c;
}
QLabel {
    background-color: transparent;
    color: #ffffff;
}
QComboBox, QSpinBox {
    background-color: #3a3a3c;
    border: 1px solid #545458;
    padding: 5px 8px;
    border-radius: 5px; /* Explicitly ensure radius */
    color: #ffffff;
    min-height: 22px;
}
QComboBox {
    padding-left: 8px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox::down-arrow {
    /* image: url(assets/down_arrow_dark.png); */
    width: 12px;
    height: 12px;
}
QCheckBox {
    spacing: 5px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #545458;
    background-color: #3a3a3c;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #0a84ff;
    border: 1px solid #0a84ff;
    border-radius: 4px;
    /* image: url(assets/checkmark_dark.png); */
}
QProgressBar {
    border: 1px solid #3a3a3c;
    border-radius: 5px;
    text-align: center;
    color: #ffffff;
    background-color: #2c2c2e;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #0a84ff;
    border-radius: 5px;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture to PDF")
        self.setMinimumWidth(400)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.monitor = ScreenMonitor()
        self.settings = QSettings('ScreenCapturePDF', 'Settings')
        self.pdf_thread = None
        self.pdf_compiler_worker = None
        self.ocr_thread = None
        self.ocr_worker = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10) # Reduced overall spacing

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
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Timer settings
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(QLabel("Delay before recording (seconds):"))
        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(0, 10)
        self.timer_spinbox.setValue(3)
        timer_layout.addWidget(self.timer_spinbox)
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)

        # PDF settings
        pdf_group = QGroupBox("PDF Settings")
        pdf_layout = QVBoxLayout()

        layout_selection = QHBoxLayout()
        layout_selection.addWidget(QLabel("Images per page:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["1", "2", "4"])
        self.layout_combo.setCurrentText("4")
        layout_selection.addWidget(self.layout_combo)

        pdf_output = QHBoxLayout()
        self.pdf_path_btn = QPushButton("PDF Output Directory")
        self.pdf_path_btn.clicked.connect(self.select_pdf_directory)
        self.pdf_path_label = QLabel("Default")
        pdf_output.addWidget(self.pdf_path_btn)
        pdf_output.addWidget(self.pdf_path_label)

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
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        layout.addLayout(status_layout)

    def apply_theme(self, theme_choice):
        app = QApplication.instance()
        if not app: return
        effective_theme = theme_choice.lower()
        if effective_theme == "system":
            system_theme = darkdetect.theme()
            effective_theme = system_theme.lower() if system_theme else "light"
        if effective_theme == "dark":
            app.setStyleSheet(DARK_STYLESHEET)
        else:
            app.setStyleSheet(LIGHT_STYLESHEET)
        self.settings.setValue('theme', theme_choice)

    def load_settings(self):
        pdf_dir = self.settings.value('pdf_directory', 'Default')
        self.pdf_path_label.setText(pdf_dir)
        saved_theme = self.settings.value('theme', 'System')
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(saved_theme)
        self.theme_combo.blockSignals(False)
        self.apply_theme(saved_theme)

    def select_region(self):
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
            self.status_label.setText("Please select a region.")
            self.select_region()
            if not self.monitor.has_region(): return

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
        images_per_page = int(self.layout_combo.currentText())
        self.monitor.start(
            images_per_page=images_per_page,
            pdf_directory=self.pdf_path_label.text()
        )
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_region_btn.setEnabled(False)
        self.status_label.setText("Monitoring...")

    def stop_monitoring(self):
        captured_images = self.monitor.get_captured_images()
        self.monitor.stop()

        if captured_images:
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

            self.pdf_thread.started.connect(self.pdf_compiler_worker.run_generation)
            self.pdf_compiler_worker.progress_updated.connect(self.update_pdf_progress)
            self.pdf_compiler_worker.finished.connect(self.pdf_generation_finished)
            self.pdf_compiler_worker.finished.connect(self.pdf_thread.quit)
            self.pdf_thread.finished.connect(self.pdf_thread.deleteLater)
            self.pdf_thread.finished.connect(self.pdf_compiler_worker.deleteLater)

            self.pdf_thread.start()
            self.status_label.setText("Generating PDF...")
        else:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.select_region_btn.setEnabled(True)
            self.status_label.setText("Monitoring stopped. No images captured.")

    def update_pdf_progress(self, value):
        self.progress_bar.setValue(value)

    def pdf_generation_finished(self, result_message):
        if result_message.startswith("Error:"):
            self.progress_bar.setVisible(False)
            self.status_label.setText(result_message)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.select_region_btn.setEnabled(True)
        else:
            self.status_label.setText("Performing OCR...")
            self.progress_bar.setVisible(False)

            try:
                original_pdf_path = result_message.split("PDF generated: ", 1)[1]
            except IndexError:
                self.status_label.setText("Error: Could not parse PDF path for OCR.")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.select_region_btn.setEnabled(True)
                return

            pdf_dir = os.path.dirname(original_pdf_path)
            pdf_filename = os.path.basename(original_pdf_path)
            ocr_output_path = os.path.join(pdf_dir, f"OCR_{pdf_filename}")

            self.ocr_thread = QThread()
            self.ocr_worker = OCRProcessor()
            self.ocr_worker.set_params(original_pdf_path, ocr_output_path)
            self.ocr_worker.moveToThread(self.ocr_thread)

            self.ocr_thread.started.connect(self.ocr_worker.run_ocr)
            self.ocr_worker.finished.connect(self.ocr_finished)
            self.ocr_worker.finished.connect(self.ocr_thread.quit)
            self.ocr_thread.finished.connect(self.ocr_thread.deleteLater)
            self.ocr_thread.finished.connect(self.ocr_worker.deleteLater)

            self.ocr_thread.start()

    def ocr_finished(self, result_message):
        self.status_label.setText(result_message)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_region_btn.setEnabled(True)

    def closeEvent(self, event):
        self.monitor.stop()
        if self.pdf_thread and self.pdf_thread.isRunning():
            print("Warning: Closing while PDF generation is in progress.")
            self.pdf_thread.quit()
            self.pdf_thread.wait(500)
        if self.ocr_thread and self.ocr_thread.isRunning():
            print("Warning: Closing while OCR is in progress.")
            self.ocr_thread.quit()
            self.ocr_thread.wait(500)
        event.accept()

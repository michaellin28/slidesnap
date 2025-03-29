from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                               QLabel, QSpinBox, QCheckBox, QFileDialog, QComboBox,
                               QHBoxLayout, QGroupBox)
from PyQt6.QtCore import Qt, QSettings
from .region_selector import RegionSelector
from ..core.monitor import ScreenMonitor
from ..core.pdf_compiler import PDFCompiler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture to PDF")
        self.setMinimumWidth(400)
        
        # Initialize components
        self.monitor = ScreenMonitor()
        self.pdf_compiler = PDFCompiler()
        self.settings = QSettings('ScreenCapturePDF', 'Settings')
        
        # Setup UI
        self.setup_ui()
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
        
        # PDF settings
        pdf_group = QGroupBox("PDF Settings")
        pdf_layout = QVBoxLayout()
        
        self.enable_pdf_cb = QCheckBox("Generate PDF after session")
        self.enable_pdf_cb.setChecked(True)
        
        layout_selection = QHBoxLayout()
        layout_selection.addWidget(QLabel("Images per page:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["1", "2", "4"])
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
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
    def select_region(self):
        self.hide()
        selector = RegionSelector()
        if selector.exec():
            region = selector.get_region()
            self.monitor.set_region(region)
            self.region_label.setText(f"Region: {region[2]}x{region[3]}")
        self.show()
    
    def select_pdf_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select PDF Output Directory")
        if directory:
            self.pdf_path_label.setText(directory)
            self.settings.setValue('pdf_directory', directory)
    
    def start_monitoring(self):
        if not self.monitor.has_region():
            self.status_label.setText("Please select a region first")
            return
            
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
        self.monitor.stop()
        if self.enable_pdf_cb.isChecked():
            self.status_label.setText("Generating PDF...")
            self.pdf_compiler.generate(
                self.monitor.get_captured_images(),
                int(self.layout_combo.currentText()),
                self.pdf_path_label.text()
            )
            self.status_label.setText("PDF generated successfully")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_region_btn.setEnabled(True)
    
    def load_settings(self):
        pdf_dir = self.settings.value('pdf_directory', 'Default')
        self.pdf_path_label.setText(pdf_dir)
    
    def closeEvent(self, event):
        self.monitor.stop()
        event.accept()

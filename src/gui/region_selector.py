from PyQt6.QtWidgets import QDialog, QApplication, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QScreen, QFont

class RegionSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        
        # Get screen geometry
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        # Initialize selection points
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        
        # Create info label
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; padding: 5px; border-radius: 3px;")
        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.hide()
        
        # Set cursor to crosshair
        self.setCursor(Qt.CursorShape.CrossCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw semi-transparent overlay
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.drawRect(self.rect())
        
        if not self.is_selecting:
            return
            
        # Draw selected region
        region = self.get_region()
        
        # Make the selected area clear (no overlay)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.drawRect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
        
        # Reset composition mode
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        # Draw border with Mac-like appearance
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(region[0]), int(region[1]), int(region[2]), int(region[3]))
        
        # Draw corner handles
        handle_size = 6
        handle_color = QColor(255, 255, 255)
        painter.setBrush(handle_color)
        
        # Draw the 8 handles - convert all coordinates to integers
        # Top-left
        painter.drawRect(int(region[0] - handle_size/2), int(region[1] - handle_size/2), handle_size, handle_size)
        # Top-middle
        painter.drawRect(int(region[0] + region[2]/2 - handle_size/2), int(region[1] - handle_size/2), handle_size, handle_size)
        # Top-right
        painter.drawRect(int(region[0] + region[2] - handle_size/2), int(region[1] - handle_size/2), handle_size, handle_size)
        # Middle-left
        painter.drawRect(int(region[0] - handle_size/2), int(region[1] + region[3]/2 - handle_size/2), handle_size, handle_size)
        # Middle-right
        painter.drawRect(int(region[0] + region[2] - handle_size/2), int(region[1] + region[3]/2 - handle_size/2), handle_size, handle_size)
        # Bottom-left
        painter.drawRect(int(region[0] - handle_size/2), int(region[1] + region[3] - handle_size/2), handle_size, handle_size)
        # Bottom-middle
        painter.drawRect(int(region[0] + region[2]/2 - handle_size/2), int(region[1] + region[3] - handle_size/2), handle_size, handle_size)
        # Bottom-right
        painter.drawRect(int(region[0] + region[2] - handle_size/2), int(region[1] + region[3] - handle_size/2), handle_size, handle_size)
        
        # Update info label with dimensions
        self.update_info_label(region)
    
    def update_info_label(self, region):
        # Update the info label with dimensions
        width = region[2]
        height = region[3]
        self.info_label.setText(f"{width} × {height}")
        
        # Position the label near the selection
        label_size = self.info_label.sizeHint()
        
        # Position above the selection if there's room, otherwise below
        if region[1] > label_size.height() + 10:
            label_x = region[0] + (region[2] - label_size.width()) // 2
            label_y = region[1] - label_size.height() - 5
        else:
            label_x = region[0] + (region[2] - label_size.width()) // 2
            label_y = region[1] + region[3] + 5
            
        self.info_label.setGeometry(label_x, label_y, label_size.width(), label_size.height())
        self.info_label.show()
    
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.is_selecting = True
        self.update()
    
    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
    
    def mouseReleaseEvent(self, event):
        self.is_selecting = False
        if self.begin and self.end:
            # Only accept if we have a valid selection (non-zero area)
            region = self.get_region()
            if region[2] > 5 and region[3] > 5:
                self.accept()
            else:
                # Reset if the selection is too small
                self.begin = QPoint()
                self.end = QPoint()
                self.info_label.hide()
                self.update()
    
    def get_region(self):
        if self.begin and self.end:
            return (min(self.begin.x(), self.end.x()),
                   min(self.begin.y(), self.end.y()),
                   abs(self.begin.x() - self.end.x()),
                   abs(self.begin.y() - self.end.y()))
        return (0, 0, 0, 0)
        
    def keyPressEvent(self, event):
        # Allow canceling with Escape key
        if event.key() == Qt.Key.Key_Escape:
            self.reject()

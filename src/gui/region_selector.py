from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QScreen

class RegionSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        
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
        painter.setBrush(QColor(0, 150, 255, 50))
        painter.drawRect(region[0], region[1], region[2], region[3])
        
        # Draw border
        painter.setPen(QColor(0, 150, 255))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(region[0], region[1], region[2], region[3])
    
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
            self.accept()
    
    def get_region(self):
        if self.begin and self.end:
            return (min(self.begin.x(), self.end.x()),
                   min(self.begin.y(), self.end.y()),
                   abs(self.begin.x() - self.end.x()),
                   abs(self.begin.y() - self.end.y()))

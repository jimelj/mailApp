from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QBrush


# class StatusIndicator(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.layout = QHBoxLayout()
#         self.setLayout(self.layout)
#         self.setFixedHeight(30)  # Slim bar

#         # Set alignment and spacing for a clean look
#         self.layout.setAlignment(Qt.AlignRight)
#         self.layout.setSpacing(10)

#         print("DEBUG: Initializing StatusIndicator")

#         # Create status indicators
#         self.zip_status = self.create_status_circle_with_text(".ZIP")
#         self.skid_tags_status = self.create_status_circle_with_text("Skid Tags")
#         self.tray_tags_status = self.create_status_circle_with_text("Tray Tags")

#         # Add status indicators to the layout
#         self.layout.addWidget(self.zip_status["widget"])
#         self.layout.addWidget(self.skid_tags_status["widget"])
#         self.layout.addWidget(self.tray_tags_status["widget"])

#         # Add stretch to align with the version text on the left
#         self.layout.addStretch()
#         print("DEBUG: StatusIndicator initialized successfully")

#     def create_status_circle_with_text(self, text):
#         """Create a status circle with text beside it."""
#         widget = QWidget()
#         widget_layout = QHBoxLayout()
#         widget.setLayout(widget_layout)
#         widget_layout.setAlignment(Qt.AlignLeft)
#         widget_layout.setSpacing(5)

#         # Circle
#         circle = QLabel()
#         circle.setFixedSize(15, 15)
#         circle.setStyleSheet("background-color: red; border-radius: 7.5px;")  # Red by default

#         # Text
#         text_label = QLabel(text)
#         text_label.setAlignment(Qt.AlignLeft)

#         # Add to layout
#         widget_layout.addWidget(circle)
#         widget_layout.addWidget(text_label)

#         return {"circle": circle, "widget": widget}

#     def set_status(self, component, status):
#         """Set the color of a status circle."""
#         color = "green" if status else "red"
#         if component == "ZIP":
#             self.zip_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 7.5px;")
#         elif component == "Skid Tags":
#             self.skid_tags_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 7.5px;")
#         elif component == "Tray Tags":
#             self.tray_tags_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 7.5px;")

class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("statusIndicator")
        
        # Set layout properties
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Create status indicators with modern design
        self.zip_status = self.create_status_indicator("ZIP")
        self.skid_tags_status = self.create_status_indicator("Skid Tags")
        self.tray_tags_status = self.create_status_indicator("Tray Tags")

        # Add status indicators to the layout
        self.layout.addWidget(self.zip_status["widget"])
        self.layout.addWidget(self.skid_tags_status["widget"])
        self.layout.addWidget(self.tray_tags_status["widget"])

    def create_status_indicator(self, text):
        """Create a status indicator with bright red circle and text."""
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget.setLayout(widget_layout)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(8)
        widget_layout.setAlignment(Qt.AlignCenter)

        # Create a simple circle label rather than custom painted widget
        circle = QLabel()
        circle.setFixedSize(14, 14)
        circle.setStyleSheet("background-color: #FF0000; border-radius: 7px;")

        # Text label with clear styling
        text_label = QLabel(text)
        text_label.setStyleSheet("color: #000000; font-size: 11pt;")

        # Add to layout
        widget_layout.addWidget(circle)
        widget_layout.addWidget(text_label)

        return {"indicator": circle, "widget": widget}

    def set_status(self, component, status):
        """Set the status of an indicator."""
        color = "#00CC00" if status else "#FF0000"  # Bright green or bright red
        
        if component == "ZIP":
            self.zip_status["indicator"].setStyleSheet(f"background-color: {color}; border-radius: 7px;")
        elif component == "Skid Tags":
            self.skid_tags_status["indicator"].setStyleSheet(f"background-color: {color}; border-radius: 7px;")
        elif component == "Tray Tags":
            self.tray_tags_status["indicator"].setStyleSheet(f"background-color: {color}; border-radius: 7px;")

    def reset_status(self):
        """Reset all indicators to the default (red) state."""
        self.set_status("ZIP", False)
        self.set_status("Skid Tags", False)
        self.set_status("Tray Tags", False)


class StatusLight(QWidget):
    """A modern status light indicator with smooth rendering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = False
        self.color = QColor("#e74c3c")  # Red by default
        self.setMinimumSize(12, 12)
    
    def set_status(self, status):
        """Set the status (True=green, False=red)."""
        self.status = status
        self.color = QColor("#2ecc71") if status else QColor("#e74c3c")
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Custom paint event for smooth circle rendering."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the outer border
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.setBrush(QBrush(self.color))
        
        # Draw a circle that fills the widget
        size = min(self.width(), self.height()) - 2
        x = (self.width() - size) / 2
        y = (self.height() - size) / 2
        painter.drawEllipse(int(x), int(y), size, size)
        
        # Add a highlight effect for a 3D look
        if self.status:
            highlight = QColor(255, 255, 255, 70)
            painter.setBrush(QBrush(highlight))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x + size/4), int(y + size/4), int(size/2), int(size/2))
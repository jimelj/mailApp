from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


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
        # self.setMinimumHeight(18)  # Adjust height to match the status bar
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # Create status indicators
        self.zip_status = self.create_status_circle_with_text("ZIP")
        self.skid_tags_status = self.create_status_circle_with_text("Skid Tags")
        self.tray_tags_status = self.create_status_circle_with_text("Tray Tags")

        # Add status indicators to the layout
        self.layout.addWidget(self.zip_status["widget"])
        self.layout.addWidget(self.skid_tags_status["widget"])
        self.layout.addWidget(self.tray_tags_status["widget"])

    def create_status_circle_with_text(self, text):
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget.setLayout(widget_layout)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(5)

        # Circle
        circle = QLabel()
        circle.setFixedSize(10, 10)  # Adjust size as needed
        circle.setStyleSheet("background-color: red; border-radius: 5px;")  # Red by default

        # Text
        text_label = QLabel(text)

        # Add to layout
        widget_layout.addWidget(circle)
        widget_layout.addWidget(text_label)

        return {"circle": circle, "widget": widget}
    def set_status(self, component, status):
        color = "green" if status else "red"
        if component == "ZIP":
            self.zip_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        elif component == "Skid Tags":
            self.skid_tags_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        elif component == "Tray Tags":
            self.tray_tags_status["circle"].setStyleSheet(f"background-color: {color}; border-radius: 5px;")

    def reset_status(self):
        """Reset all indicators to the default (red) state."""
        self.set_status("ZIP", False)
        self.set_status("Skid Tags", False)
        self.set_status("Tray Tags", False)
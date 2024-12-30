import os
import platform  # Import this for cross-platform OS detection
import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage


class PrintSkidTagsTab(QWidget):
    """Tab for displaying and printing SkidTags.pdf."""

    def __init__(self):
        super().__init__()

        # PDF management
        self.pdf_path = None
        self.doc = None
        self.current_page_index = 0
        self.total_pages = 0

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.navigation_layout = QHBoxLayout()

        # PDF display area
        self.page_display = QLabel("No PDF loaded")
        self.page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.page_display)

        # Navigation buttons
        self.back_button = QPushButton("Back")
        self.page_label = QLabel("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_button = QPushButton("Next")

        self.back_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.page_label)
        self.navigation_layout.addWidget(self.next_button)

        # Wrap navigation and print buttons in a container layout
        self.container_layout = QVBoxLayout()
        self.container_layout.addLayout(self.navigation_layout)
        self.container_layout.addWidget(self.print_button)

        # Add navigation layout to the main layout
        self.main_layout.addLayout(self.navigation_layout)

        # Print button
        self.print_button = QPushButton("Print Skid Tags")
        self.print_button.clicked.connect(self.print_pdf)
        self.main_layout.addWidget(self.print_button)

        # Add the container layout to the main layout
        self.main_layout.addLayout(self.container_layout)

    def load_pdf(self, pdf_path):
        """Load the PDF file."""
        if not os.path.exists(pdf_path):
            self.show_error(f"PDF file not found: {pdf_path}")
            return

        try:
            self.doc = fitz.open(pdf_path)
            self.pdf_path = pdf_path
            self.total_pages = len(self.doc)
            self.current_page_index = 0

            if self.total_pages == 0:
                raise ValueError("The document contains no pages.")

            print(f"PDF loaded successfully: {pdf_path}, Total Pages: {self.total_pages}")
            self.update_page()
        except Exception as e:
            self.doc = None
            self.total_pages = 0
            self.current_page_index = 0
            self.show_error(f"Failed to load PDF: {e}")

    def update_page(self):
        """Display the current page."""
        if self.doc is None or not (0 <= self.current_page_index < self.total_pages):
            self.show_error("Invalid page index or no document loaded.")
            return

        try:
            page = self.doc[self.current_page_index]
            pixmap = page.get_pixmap(dpi=150)

            image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)

            # scaled_pixmap = pixmap.scaled(
            #     self.page_display.size(),
            #     Qt.KeepAspectRatio,
            #     Qt.SmoothTransformation
            # )
            # Get the available size for the widget
            available_size = self.page_display.size()

            # Scale the pixmap to fit within the available size
            scaled_pixmap = pixmap.scaled(
                available_size,
                # Qt.KeepAspectRatio,
                # Qt.SmoothTransformation
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )


            self.page_display.setPixmap(scaled_pixmap)
            self.page_label.setText(f"Page {self.current_page_index + 1} of {self.total_pages}")
            self.back_button.setEnabled(self.current_page_index > 0)
            self.next_button.setEnabled(self.current_page_index < self.total_pages - 1)
        except Exception as e:
            self.show_error(f"Error displaying page: {e}")

            
    def resizeEvent(self, event):
        """Re-render the current page on window resize."""
        self.update_page()
        super().resizeEvent(event)



    def next_page(self):
        """Go to the next page."""
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.update_page()

    def previous_page(self):
        """Go to the previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.update_page()

    def print_pdf(self):
        """Print the PDF document."""
        if not self.pdf_path:
            self.show_error("No PDF loaded. Cannot print.")
            return

        try:
            # os.system(f"lp \"{self.pdf_path}\"")  # Print command for UNIX-like systems
            # print("Print job submitted successfully.")
            if platform.system() == "Windows":
                os.startfile(self.pdf_path, "print")  # Windows-specific print command
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open -a Preview \"{self.pdf_path}\"")  # Use Preview for printing
            else:
                print("Unsupported platform for printing.")    
        except Exception as e:
            self.show_error(f"Failed to print PDF: {e}")

    def show_error(self, message):
        """Display an error message."""
        print(message)
        self.page_display.setText(message)

    def resizeEvent(self, event):
        """Re-render the current page on window resize."""
        self.update_page()
        super().resizeEvent(event)
import os
import platform
import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage


class PrintSkidTagsTab(QWidget):
    """Tab for displaying and printing SkidTags.pdf with OS-specific behavior."""

    def __init__(self, status_indicator):
        super().__init__()

        self.status_indicator = status_indicator

        # Detect OS
        self.current_os = platform.system()

        # PDF management
        self.pdf_path = None
        self.doc = None
        self.current_page_index = 0
        self.total_pages = 0
        self.last_size = None
        self.resize_timer = None

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 10, 20, 10)

        # PDF display area with scroll capability
        self.page_display = QLabel("No PDF loaded")
        self.page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_display.setObjectName("pdfView")
        self.main_layout.addWidget(self.page_display, stretch=1)

        # Page number label
        self.page_label = QLabel("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("font-size: 14px; color: #555;")
        self.main_layout.addWidget(self.page_label)

        # Navigation buttons (Back and Next)
        self.navigation_layout = QHBoxLayout()
        self.navigation_layout.setSpacing(15)

        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")
        self.back_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        # Navigation buttons are controlled by stylesheet now
        self.back_button.setEnabled(False)
        self.next_button.setEnabled(False)

        self.navigation_layout.addStretch()
        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.next_button)
        self.navigation_layout.addStretch()
        self.main_layout.addLayout(self.navigation_layout)

        # Print button (separate row)
        self.print_button = QPushButton("Print Skid Tags")
        self.print_button.clicked.connect(self.print_pdf)
        self.print_layout = QHBoxLayout()
        self.print_layout.addStretch()
        self.print_layout.addWidget(self.print_button)
        self.print_layout.addStretch()
        self.main_layout.addLayout(self.print_layout)

    def load_pdf(self, pdf_path):
        """Load the PDF file."""
        if not os.path.exists(pdf_path):
            self.show_error(f"PDF file not found: {pdf_path}")
            self.status_indicator.set_status("Skid Tags", False)  # Red circle for Skid Tags
            return
        else: 
            self.status_indicator.set_status("Skid Tags", True)  # Green circle for Skid Tags
        
        try:
            # Close previous PDF if open
            if self.doc:
                self.doc.close()
                
            self.doc = fitz.open(pdf_path)
            print(f"DEBUG: Successfully opened PDF: {pdf_path}")
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
        """Display the current page with OS-specific behavior."""
        if self.doc is None or not (0 <= self.current_page_index < self.total_pages):
            self.show_error("Invalid page index or no document loaded.")
            return

        try:
            page = self.doc[self.current_page_index]
            pixmap = page.get_pixmap(dpi=150)

            image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888)
            pdf_pixmap = QPixmap.fromImage(image)

            # Get current dimensions once
            current_width = self.page_display.width()
            current_height = self.page_display.height()
            
            # Only scale if the size is at least 50px in both dimensions (prevents micro-scaling)
            if current_width > 50 and current_height > 50:
                # Use consistent scaling approach for all platforms
                scaled_pixmap = pdf_pixmap.scaled(
                    current_width - 20,  # Subtract margin to prevent scrollbar flickering
                    current_height - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.page_display.setPixmap(scaled_pixmap)
            
            self.page_label.setText(f"Page {self.current_page_index + 1} of {self.total_pages}")
            self.back_button.setEnabled(self.current_page_index > 0)
            self.next_button.setEnabled(self.current_page_index < self.total_pages - 1)
            
            # Remember the current size to avoid unnecessary updates
            self.last_size = (current_width, current_height)
        except Exception as e:
            self.show_error(f"Error displaying page: {e}")

    def resizeEvent(self, event):
        """Handle window resize with debouncing to prevent continuous zooming."""
        super().resizeEvent(event)
        
        # Skip if no PDF is loaded
        if not self.doc:
            return
            
        # Get the new size
        new_width = self.page_display.width()
        new_height = self.page_display.height()
        
        # Only update if the size change is significant
        if (not self.last_size or 
            abs(new_width - self.last_size[0]) > 50 or 
            abs(new_height - self.last_size[1]) > 50):
            
            # Cancel any pending timer
            if self.resize_timer:
                self.resize_timer.stop()
                
            # Set a timer to update the page after resizing stops
            self.resize_timer = QTimer()
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self.update_page)
            self.resize_timer.start(300)  # 300ms delay

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
            if self.current_os == "Windows":
                # Debugging: Verify the PDF path is correct and accessible
                if not os.path.exists(self.pdf_path):
                    self.show_error(f"File not found: {self.pdf_path}")
                    return
                
                # Ensure the PDF path uses raw strings or proper formatting
                pdf_path_fixed = os.path.abspath(self.pdf_path)
                print(f"Attempting to print: {pdf_path_fixed}")
                
                # Attempt to print the PDF
                os.startfile(pdf_path_fixed, "open")
            elif self.current_os == "Darwin":
                # macOS: Use Preview for printing
                os.system(f"open -a Preview \"{self.pdf_path}\"")
            else:
                self.show_error("Unsupported platform for printing.")
        except FileNotFoundError:
            self.show_error(f"File not found: {self.pdf_path}")
        except OSError as e:
            # More informative error handling for WinError 1155
            if hasattr(e, 'winerror') and e.winerror == 1155:
                self.show_error(
                    "No application is associated with PDF files for this operation. "
                    "Please install a PDF viewer and set it as default."
                )
            else:
                self.show_error(f"Failed to print PDF: {e}")
        except Exception as e:
            self.show_error(f"Unexpected error occurred: {e}")

    def show_error(self, message):
        """Display an error message."""
        print(message)
        self.page_display.setText(message)

    def clear_pdf(self):
        """Clear the displayed PDF in the Skid Tags tab."""
        if self.doc:
            self.doc.close()
            self.doc = None
            
        self.page_display.clear()  # Clear the PDF display area
        self.page_display.setText("No PDF loaded")  # Reset to the default message
        self.page_label.setText("Page 0 of 0")  # Reset the page label
        self.back_button.setEnabled(False)  # Disable the Back button
        self.next_button.setEnabled(False)  # Disable the Next button
        self.pdf_path = None  # Clear the loaded PDF path
        self.current_page_index = 0
        self.total_pages = 0
        print("Skid Tags tab reset.")

    def reset(self):
        """Clear the displayed PDF and reset the tab."""
        self.clear_pdf()  # Call the clear_pdf method to reset the display
        print("PrintTrayTagsTab reset.")
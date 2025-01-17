import os
import platform
import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
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

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 10, 20, 10)

        # PDF display area
        self.page_display = QLabel("No PDF loaded")
        self.page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: 1px solid #0056b3;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        self.back_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

        self.navigation_layout.addStretch()
        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.next_button)
        self.navigation_layout.addStretch()
        self.main_layout.addLayout(self.navigation_layout)

        # Print button (separate row)
        self.print_button = QPushButton("Print Skid Tags")
        self.print_button.clicked.connect(self.print_pdf)
        self.print_button.setStyleSheet(button_style)
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
            self.doc = fitz.open(pdf_path)
            print(f"DEBUG: Successfully opened PDF: {pdf_path}")
            self.pdf_path = pdf_path
            self.total_pages = len(self.doc)
            self.current_page_index = 0

            if self.total_pages == 0:
                raise ValueError("The document contains no pages.")

            print(f"PDF loaded successfully: {pdf_path}, Total Pages: {self.total_pages}")
            self.update_page()
            print('JJJ')
            print(pdf_path)
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

            if self.current_os == "Windows":
                # Windows logic
                available_width = self.width() - 50
                available_height = self.height() - 150
                self.page_display.setFixedSize(available_width, available_height)

                scaled_pixmap = pdf_pixmap.scaled(
                    available_width,
                    available_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            else:
                # macOS (and other OS) logic
                scaled_pixmap = pdf_pixmap.scaled(
                    self.page_display.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
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
            if e.winerror == 1155:
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
        self.page_display.clear()  # Clear the PDF display area
        self.page_display.setText("No PDF loaded")  # Reset to the default message
        self.page_label.setText("Page 0 of 0")  # Reset the page label
        self.back_button.setEnabled(False)  # Disable the Back button
        self.next_button.setEnabled(False)  # Disable the Next button
        self.pdf_path = None  # Clear the loaded PDF path
        self.doc = None  # Clear the document
        self.current_page_index = 0
        self.total_pages = 0
        print("Skid Tags tab reset.")

    def reset(self):
        """Clear the displayed PDF and reset the tab."""
        self.clear_pdf()  # Call the clear_pdf method to reset the display
        print("PrintTrayTagsTab reset.")
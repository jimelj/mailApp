import sys
import os
import shutil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
from PySide6.QtGui import QGuiApplication
import pandas as pd
from csmController import CSMTab, parse_zip_and_prepare_data  # Import the tab from csmController
from printController import PrintSkidTagsTab  # Import the tab from printController
from trayController import PrintTrayTagsTab  # Import the tab from trayController

# Set high DPI scaling policy
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)


class MainTab(QWidget):
    """Main tab for uploading ZIP files."""

    def __init__(self, csm_tab, skid_tags_tab, tray_tags_tab):
        super().__init__()

        self.setMinimumSize(1024, 768)  # Set a minimum size for the window
        self.setGeometry(100, 100, 1200, 800)  # Position and initial size
        self.csm_tab = csm_tab
        self.skid_tags_tab = skid_tags_tab
        self.tray_tags_tab = tray_tags_tab
        self.layout = QVBoxLayout(self)

        # Welcome and instructions
        self.layout.addWidget(QLabel("Welcome to the Mail Data Management System!"))
        self.layout.addWidget(QLabel("Use this tab to upload ZIP files and manage data."))

        # Upload Button
        self.upload_button = QPushButton("Upload ZIP File")
        self.upload_button.clicked.connect(self.upload_zip)

        # Button Styling
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
        self.upload_button.setStyleSheet(button_style)

        self.layout.addWidget(self.upload_button)

        # Feedback Label
        self.feedback_label = QLabel("")
        self.layout.addWidget(self.feedback_label)

    # def clean_up_directories(self):
    #     """Delete all contents inside the 'data/extracted' directory."""
    #     extracted_directory = "data/extracted"
    #     if os.path.exists(extracted_directory):
    #         shutil.rmtree(extracted_directory)
    #         print(f"Cleaned up directory: {extracted_directory}")
    #     else:
    #         print(f"No directory to clean: {extracted_directory}")

    def upload_zip(self):
        # self.clean_up_directories()
        """Handle ZIP file upload and processing."""
        zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File", "", "ZIP Files (*.zip)")
        if zip_file_path:
            try:
                # Parse the ZIP file and update the CSM tab
                df_filtered = parse_zip_and_prepare_data(zip_file_path)
                self.csm_tab.update_data(df_filtered)

                self.feedback_label.setText("File uploaded and data processed successfully!")
                self.feedback_label.setStyleSheet("color: green;")

                # Load SkidTags.pdf if it exists
                extracted_path = "data/extracted"
                skid_tags_pdf_path = os.path.join(extracted_path, "Reports", "SkidTags.pdf")
                if os.path.exists(skid_tags_pdf_path):
                    self.skid_tags_tab.load_pdf(skid_tags_pdf_path)
                    self.feedback_label.setText("ZIP file uploaded and data processed successfully!")
                    self.feedback_label.setStyleSheet("color: green;")
                else:
                    self.feedback_label.setText("SkidTags.pdf not found in the extracted ZIP file.")
                    self.feedback_label.setStyleSheet("color: red;")

                # Load TrayTags.pdf if it exists
                tray_tags_pdf_path = os.path.join(extracted_path, "Reports", "TrayTags.pdf")
                if os.path.exists(tray_tags_pdf_path):
                    self.tray_tags_tab.load_pdf(tray_tags_pdf_path)
                    self.feedback_label.setText("ZIP file uploaded and data processed successfully!")
                    self.feedback_label.setStyleSheet("color: green;")
                else:
                    self.feedback_label.setText("TrayTags.pdf not found in the extracted ZIP file.")
                    self.feedback_label.setStyleSheet("color: red;")

            except Exception as e:
                self.feedback_label.setText(f"Error processing ZIP file: {e}")
                self.feedback_label.setStyleSheet("color: red;")


class MainApp(QMainWindow):
    """Main application window with tabbed navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Data Management System")
        screen = QApplication.primaryScreen().availableGeometry()

        # Ensure the window size fits within the screen dimensions
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Set the window size relative to the screen size (e.g., 80% width and height)
        self.resize(int(screen_width * 0.8), int(screen_height * 0.8))

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the tabs
        self.csm_tab = CSMTab(pd.DataFrame())  # Use the existing implementation of CSMTab
        self.skid_tags_tab = PrintSkidTagsTab()
        self.tray_tags_tab = PrintTrayTagsTab()
        self.main_tab = MainTab(self.csm_tab, self.skid_tags_tab, self.tray_tags_tab)

        # Add tabs to the application
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.csm_tab, "CSM")
        self.tab_widget.addTab(self.skid_tags_tab, "Print Skid Tags")
        self.tab_widget.addTab(self.tray_tags_tab, "Print Tray Tags")

    def closeEvent(self, event):
        """Clean up directories when the application closes."""
        self.clean_up_directories()
        event.accept()

    def clean_up_directories(self):
        """Delete all contents inside the 'data/extracted' directory."""
        extracted_directory = "data/extracted"
        if os.path.exists(extracted_directory):
            shutil.rmtree(extracted_directory)
            print(f"Cleaned up directory: {extracted_directory}")
        else:
            print(f"No directory to clean: {extracted_directory}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
import sys
import os
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
import pandas as pd
from csmController import CSMTab, parse_zip_and_prepare_data # Import the tab from csmControllerfrom printController import PrintSkidTagsTab  # Import the PrintSkidTagsTab class from printController
from printController import PrintSkidTagsTab  # Import the tab from printController


class MainTab(QWidget):
    """Main tab for uploading ZIP files."""

    def __init__(self, csm_tab, skid_tags_tab):
        super().__init__()
        self.csm_tab = csm_tab
        self.skid_tags_tab = skid_tags_tab
        self.layout = QVBoxLayout(self)

        # Welcome and instructions
        self.layout.addWidget(QLabel("Welcome to the Mail Data Management System!"))
        self.layout.addWidget(QLabel("Use this tab to upload ZIP files and manage data."))

        # Upload Button
        self.upload_button = QPushButton("Upload ZIP File")
        self.upload_button.clicked.connect(self.upload_zip)
        self.layout.addWidget(self.upload_button)

        # Feedback Label
        self.feedback_label = QLabel("")
        self.layout.addWidget(self.feedback_label)

    def upload_zip(self):
        """Handle ZIP file upload and processing."""
        zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File", "", "ZIP Files (*.zip)")
        if zip_file_path:
            try:
                # Parse the ZIP file and update the CSM tab
                df_filtered = parse_zip_and_prepare_data(zip_file_path)
                self.csm_tab.update_data(df_filtered)

                self.feedback_label.setText("File uploaded and data processed successfully!")
                self.feedback_label.setStyleSheet("color: green;")
                # # Unzip the file into the data/extracted directory
                extracted_path = "data/extracted"
                # if os.path.exists(extracted_path):
                #     shutil.rmtree(extracted_path)
                # os.makedirs(extracted_path)

                # shutil.unpack_archive(zip_file_path, extracted_path)
                # print(f"ZIP file extracted to: {extracted_path}")

                # # Load and process CSM data
                # csm_file_path = os.path.join(extracted_path, "Reports", "CSMFile.txt")  # Adjust the filename as needed
                # if os.path.exists(csm_file_path):
                #     self.csm_tab.process_csm_data(csm_file_path)
                # else:
                #     print("No CSM file found in the extracted directory.")

                # Load SkidTags.pdf if it exists
                skid_tags_pdf_path = os.path.join(extracted_path, "Reports", "SkidTags.pdf")
                if os.path.exists(skid_tags_pdf_path):
                    self.skid_tags_tab.load_pdf(skid_tags_pdf_path)
                    self.feedback_label.setText("ZIP file uploaded and data processed successfully!")
                    self.feedback_label.setStyleSheet("color: green;")
                else:
                    self.feedback_label.setText("SkidTags.pdf not found in the extracted ZIP file.")
                    self.feedback_label.setStyleSheet("color: red;")

            except Exception as e:
                self.feedback_label.setText(f"Error processing ZIP file: {e}")
                self.feedback_label.setStyleSheet("color: red;")


class MainApp(QMainWindow):
    """Main application window with tabbed navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Data Management System")
        self.resize(1000, 700)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the tabs
        self.csm_tab = CSMTab(pd.DataFrame())  # Use the existing implementation of CSMTab
        self.skid_tags_tab = PrintSkidTagsTab()
        self.main_tab = MainTab(self.csm_tab, self.skid_tags_tab)

        # Add tabs to the application
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.csm_tab, "CSM")
        self.tab_widget.addTab(self.skid_tags_tab, "Print Skid Tags")

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
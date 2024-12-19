import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
from csmController import CSMTab, parse_zip_and_prepare_data # Import the tab from csmController
from printController import PrintSkidTagsTab  # Import the tab from printController
import os
import shutil
import pandas as pd


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
        """Handle ZIP file upload and parsing."""
        zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File", "", "ZIP Files (*.zip)")
        if zip_file_path:
            try:
                # Parse the ZIP file and update the CSM tab
                df_filtered = parse_zip_and_prepare_data(zip_file_path)
                self.csm_tab.update_data(df_filtered)

                self.feedback_label.setText("File uploaded and data processed successfully!")
                self.feedback_label.setStyleSheet("color: green;")
            except Exception as e:
                # Display error feedback
                self.feedback_label.setText(f"Error: {e}")
                self.feedback_label.setStyleSheet("color: red;")


# class PrintSkidTagsTab(QWidget):
#     """Placeholder for future functionality."""
#     def __init__(self):
#         super().__init__()
#         self.layout = QVBoxLayout(self)
#         self.layout.addWidget(QLabel("Feature under development: Print Skid Tags"))


class MainApp(QMainWindow):
    """Main application window with tabbed navigation."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Data Management System")
        self.resize(1000, 700)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create the CSM tab and Main tab and Print Tab
        self.csm_tab = CSMTab(pd.DataFrame())
        self.skid_tags_tab = PrintSkidTagsTab()  # Use the PrintSkidTagsTab from printController
        self.main_tab = MainTab(self.csm_tab, self.skid_tags_tab)

        # Add tabs
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.csm_tab, "CSM")
        self.tab_widget.addTab(PrintSkidTagsTab(), "Print Skid Tags")

    def closeEvent(self, event):
        """Override close event to clean up directories on exit."""
        self.clean_up_directories()

        # Allow the application to exit
        event.accept()

    def clean_up_directories(self):
        """Delete all contents inside 'data' directory but leave 'data/extracted' intact."""
        # Define the directories that need cleaning
        directory_to_clean = 'data'
        extracted_directory = 'data/extracted'

        if os.path.exists(directory_to_clean):
            # Walk through the directory and remove all files and subdirectories inside 'data'
            for root, dirs, files in os.walk(directory_to_clean, topdown=False):
                # Prevent 'data/extracted' from being cleaned
                if extracted_directory in dirs:
                    dirs.remove('extracted')  # Skip cleaning 'data/extracted'

                # Delete all files in the directory
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)  # Remove the file

                # Delete all subdirectories except for 'data/extracted'
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    os.rmdir(dir_path)  # Remove empty directories

            print("Data directory cleaned up successfully.")
        else:
            self.show_error(f"Directory '{directory_to_clean}' not found.")
        
        # Ensure 'data/extracted' is empty (remove files inside it if any)
        if os.path.exists(extracted_directory):
            for root, dirs, files in os.walk(extracted_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)  # Remove any files inside 'data/extracted'

            print("Data/extracted directory is now empty.")

    def show_error(self, message):
        """Display an error message."""
        print(message)  # Debugging message

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    # main_window.show()
    # Show the window maximized (full-screen mode)
    main_window.showMaximized()
    sys.exit(app.exec())


    # TODO: Implement print display and actually print...done
    # TODO: should we clear data on exit?...done
    # TODO: fix printcontroller to behave like csmcontroller load data only when zip is..Done
    # TODO: Display IHD on main page after data is uploaded so when moving back and forth its relavant also maybe put it in the status bar!!!
import sys
import os
import platform 
import shutil
from datetime import datetime 
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
from PySide6.QtGui import QGuiApplication
import pandas as pd
from csmController import CSMTab, parse_zip_and_prepare_data  # Import the tab from csmController
from printController import PrintSkidTagsTab  # Import the tab from printController
from trayController import PrintTrayTagsTab  # Import the tab from trayController
from util import process_zip_name
import stat
# import psutil  # For checking and closing open file handles
from time import sleep
import fitz
from pathlib import Path
# Conditional import for Windows-specific packages
if platform.system() == "Windows":
    import win32file
    import win32con


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

    # Date Display Label (initially hidden)
    # Add date label for top-right display
        self.date_label = QLabel(parent=self)  # Use the parent main window
        self.date_label.setStyleSheet("color: green; font-size: 36px; font-weight: bold;")
        self.date_label.setAlignment(Qt.AlignRight)
        self.date_label.hide()  # Hide initially

    def resizeEvent(self, event):
        """Reposition the date label on window resize."""
        super().resizeEvent(event)
        # Position date label at the top-right corner
        self.date_label.move(self.width() - self.date_label.width() - 20, 10)


    def upload_zip(self):
        # self.clean_up_directories()
        """Handle ZIP file upload and processing."""
        # Dynamically determine the OS
        current_os = platform.system()
            # Process the ZIP name
        
        # processed_zip_name = process_zip_name(self)
        # print(f"Processed ZIP Name: {processed_zip_name}")
    
        # # Pass the processed ZIP name to save_reports
        # save_reports(processed_zip_name)

        # Define the default folder based on the OS
        if current_os == "Windows":
            default_folder = r"\\cbahqdist-ts\DIST_L_JCTS\UMS Presort\in\hold"
        elif current_os == "Darwin":  # macOS
            default_folder = os.path.expanduser("~/Documents") 
        else:  # For Linux or other OS
            default_folder = os.path.expanduser("~/") 

        zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File",default_folder, "ZIP Files (*.zip)")
        if zip_file_path:
            try:
                # Parse the ZIP file and update the CSM tab
                df_filtered = parse_zip_and_prepare_data(zip_file_path)

                self.csm_tab.update_data(df_filtered)
                # Extract the date from the data or filename
                date_from_file = self.extract_date_from_file(zip_file_path)
                # Extract the base name and remove the '.zip' extension
                zip_base_name = os.path.basename(zip_file_path).replace('.zip', '')
                # Process the ZIP name
                processed_zip_name = process_zip_name(zip_base_name)
                print(f"Processed ZIP Name: {processed_zip_name}")
                # Pass the processed ZIP name to the CSMTab instance
                self.csm_tab.set_processed_zip_name(processed_zip_name)

               
                # Update and show the date label
                self.date_label.setText(f"IHD: {date_from_file}")
                self.date_label.adjustSize()  # Adjust size for text
                self.date_label.show()  # Show the date label
                self.resizeEvent(None)  # Reposition the label after updating

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

    def extract_date_from_file(self, file_path):
        """Extract the date from the file name in MM-DD-YY format."""
        try:
            # Extracting date part (assuming format: 'MailDate MM-DD-YY_...')
            file_name = os.path.basename(file_path)
            date_part = file_name.split(" ")[1].split("_")[0]  # Get '12-13-24'
            file_date = datetime.strptime(date_part, "%m-%d-%y").strftime("%B %d, %Y")
            return file_date
        except Exception:
            return "Unknown Date"
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
        """Delete all contents inside the 'data' directory."""
        script_directory = Path(__file__).parent
        data_directory = script_directory / "data"
        current_os = platform.system()
        print(data_directory)
        print(data_directory)       

        if os.path.exists(data_directory):
            try:
                    if current_os == "Windows":
                        self.force_clean_up_windows(data_directory)
                    else:
                        self.default_clean_up(data_directory)
            except Exception as e:
                    print(f"Error cleaning up directory '{data_directory}': {e}")
        else:
            print(f"Directory does not exist: {data_directory}")

    def force_clean_up_windows(self, directory):
        """Forcefully unlock and delete files on Windows."""
        def handle_remove_readonly(func, path, exc_info):
            """Handle read-only file removal."""
            os.chmod(path, stat.S_IWRITE)  # Change to writable
            func(path)

        try:
            # Ensure no processes are using the files
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.force_delete_file_windows(file_path)

            # Use shutil.rmtree with the custom handler for read-only files
            shutil.rmtree(directory, onerror=handle_remove_readonly)
            print(f"Forcefully cleaned up directory (Windows): {directory}")
        except Exception as e:
            print(f"Error during Windows cleanup: {e}")

    def force_delete_file_windows(self, file_path):
        """Unlock and delete a file on Windows."""
        try:
            import win32api
            import win32con

            # Unlock file if on Windows
            win32api.SetFileAttributes(file_path, win32con.FILE_ATTRIBUTE_NORMAL)
            os.remove(file_path)
            print(f"Forcefully deleted file: {file_path}")
        except Exception as e:
            print(f"Error forcefully deleting file {file_path}: {e}")

    def default_clean_up(self, data_directory):
        try:
                # Loop through the contents of the directory
                for item in os.listdir(data_directory):
                    item_path = os.path.join(data_directory, item)

                    # Check if it's a file or directory and delete accordingly
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)  # Remove file or symbolic link
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove directory

                print(f"Cleaned up directory: {data_directory}")
        except Exception as e:
            print(f"Error cleaning up directory '{data_directory}': {e}")
  
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())


  
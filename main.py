import sys
import os
import platform 
import shutil
from datetime import datetime 
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QSplashScreen
from PySide6.QtGui import QGuiApplication, QPixmap
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
import subprocess
from dotenv import load_dotenv
import traceback
import logging
# Conditional import for Windows-specific packages
if platform.system() == "Windows":
    import win32file
    import win32con


# def set_working_directory():
#     # Get the directory of the executable or script
#     if getattr(sys, 'frozen', False):  # Check if bundled by PyInstaller
#         application_path = os.path.dirname(sys.executable)
#     else:
#         application_path = os.path.dirname(__file__)

#     os.chdir(application_path)
#     print(f"Working directory set to: {application_path}")
# Determine the base path for bundled or development environment
# if getattr(sys, 'frozen', False):  # Check if running as a bundled application
#     base_path = sys._MEIPASS
# else:
#     base_path = os.path.dirname(__file__)

# # Construct paths to bundled data files
# facility_report_path = os.path.join(base_path, 'facilityReport.xlsx')
# zips_address_file_path = os.path.join(base_path, 'Zips by Address File Group.xlsx')
# env_file_path = os.path.join(base_path, '.env')

# # Print paths for debugging purposes
# print(f"DEBUG: Facility Report Path - {facility_report_path}")
# print(f"DEBUG: Zips Address File Path - {zips_address_file_path}")
# print(f"DEBUG: .env File Path - {env_file_path}")


# def set_working_directory():
#     # Get the directory of the executable or script
#     if getattr(sys, 'frozen', False):  # Check if bundled by PyInstaller
#         application_path = os.path.dirname(sys.executable)
#     else:
#         application_path = os.path.dirname(__file__)

#     os.chdir(application_path)
#     print(f"DEBUG: Working directory set to: {application_path}")

#     # Dynamically determine paths for bundled files
#     global facility_report_path, zips_address_file_path, env_file_path
#     facility_report_path = os.path.join(application_path, "facilityReport.xlsx")
#     zips_address_file_path = os.path.join(application_path, "Zips by Address File Group.xlsx")
#     env_file_path = os.path.join(application_path, ".env")

#     # Debugging the paths
#     print(f"DEBUG: Facility Report Path - {facility_report_path}")
#     print(f"DEBUG: Zips Address File Path - {zips_address_file_path}")
#     print(f"DEBUG: .env File Path - {env_file_path}")


# set_working_directory()

def set_working_directory():
    """
    Sets the working directory based on the runtime environment (bundled or development)
    and dynamically determines paths for bundled files.
    """
    global facility_report_path, zips_address_file_path, env_file_path, splash_screen_path

    if getattr(sys, 'frozen', False):  # Check if running as a bundled application
        base_path = sys._MEIPASS  # Temporary directory for PyInstaller bundled app
    else:
        base_path = os.path.dirname(__file__)  # Development environment

    # Set the working directory
    os.chdir(base_path)
    print(f"DEBUG: Working directory set to: {base_path}")

    # Construct paths to bundled or local data files
    facility_report_path = os.path.join(base_path, "facilityReport.xlsx")
    zips_address_file_path = os.path.join(base_path, "Zips by Address File Group.xlsx")
    env_file_path = os.path.join(base_path, ".env")
    splash_screen_path = os.path.join(base_path, 'resources', 'splash.png')

    # Print paths for debugging purposes
    print(f"DEBUG: Facility Report Path - {facility_report_path}")
    print(f"DEBUG: Zips Address File Path - {zips_address_file_path}")
    print(f"DEBUG: .env File Path - {env_file_path}")
    print(f"DEBUG: Splash Screen Path - {splash_screen_path}")

# Call the function during initialization
set_working_directory()

def simulate_loading(splash):
    """
    Simulate the loading process with progress updates on the splash screen.
    """
    tasks = [
        "Initializing modules...",
        "Loading resources...",
        "Connecting to services...",
        "Finalizing setup..."
    ]

    delay = 1000  # Delay for each task in milliseconds
    total_duration = len(tasks) * delay

    for i, task in enumerate(tasks):
        QTimer.singleShot(i * delay, lambda t=task: update_splash_message(splash, t))

    # Close the splash and load the main window after all tasks
    QTimer.singleShot(total_duration, splash.close)
    QTimer.singleShot(total_duration, load_main_window)


def update_splash_message(splash, message):
    """
    Update the message displayed on the splash screen.
    """
    splash.showMessage(
        message,
        Qt.AlignBottom | Qt.AlignCenter,
        Qt.white
    )


def load_main_window():
    """
    Load the main application window.
    """
    main_window = MainApp()
    main_window.show()


logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_uncaught_exceptions(ex_cls, ex, tb):
    logging.critical("Uncaught exception", exc_info=(ex_cls, ex, tb))

sys.excepthook = log_uncaught_exceptions

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file_path):
    load_dotenv(dotenv_path=env_file_path)
    print("Environment variables loaded from .env file.")
else:
    print("Warning: .env file not found. Using default environment variables.")


# def get_version():
#     # Try to get version from Git tags
#     try:
#         version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL)
#         return version.decode("utf-8").strip()
#     except Exception:
#         # Fallback to VERSION file if Git tags are unavailable
#         with open("VERSION", "r") as file:
#             return file.read().strip()

def get_version():
    # Try to get version from Git tags
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL
        )
        return version.decode("utf-8").strip()
    except Exception as git_error:
        print(f"DEBUG: Git version retrieval failed: {git_error}")
        
        # Fallback to VERSION file
        try:
            version_file_path = os.path.join(
                sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 
                "VERSION"
            )
            with open(version_file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError as file_error:
            print(f"DEBUG: VERSION file not found: {file_error}")
            return "Unknown Version"

__version__ = get_version()

# Print version for confirmation
print(f"App Version: {__version__}")

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
        print("DEBUG: Initializing MainApp...")
        self.setWindowTitle("PostFlow - Mail Data Management")
        screen = QApplication.primaryScreen().availableGeometry()

        # Ensure the window size fits within the screen dimensions
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Set the window size relative to the screen size (e.g., 80% width and height)
        self.resize(int(screen_width * 0.8), int(screen_height * 0.8))

        # Add the app version to the status bar
        self.statusBar().showMessage(f"Version: {__version__}")

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
        """
        Handle cleanup and close operations when the application window is closed.
        """
        print("DEBUG: Starting closeEvent...")
        try:
            self.clean_up_directories()
            print("DEBUG: Cleaned up directories.")
            self.clean_up_temporary_directories()
            print("DEBUG: Cleaned up temporary directories.")
        except Exception as e:
            print(f"DEBUG: Exception in closeEvent: {e}")
        finally:
            event.accept()
            print("DEBUG: Event accepted, closing application.")

    def closeEvent(self, event):
        """Clean up directories when the application closes."""
        self.clean_up_directories()
        self.clean_up_temporary_directories()
        event.accept()

    
    def clean_up_directories(self):
            """Delete all contents inside the 'data' directory."""
            script_directory = Path(__file__).parent
            data_directory = script_directory / "data"
            current_os = platform.system()

            print(f"Cleaning up directory: {data_directory}")

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

    def force_clean_up_windows(self, data_directory):
        """Forcefully unlock and delete files on Windows."""
        def handle_remove_readonly(func, path, exc_info):
            """Handle read-only file removal."""
            os.chmod(path, stat.S_IWRITE)  # Change to writable
            func(path)

        try:
            for root, _, files in os.walk(data_directory):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Explicitly close PDFs if they are still open
                    if file.endswith(".pdf"):
                        self.close_pdf_if_open(file_path)

                    # Forcefully delete the file
                    self.force_delete_file_windows(file_path)

            # Remove the directory structure
            shutil.rmtree(data_directory, onerror=handle_remove_readonly)
            print(f"Forcefully cleaned up directory (Windows): {data_directory}")
        except Exception as e:
            print(f"Error during Windows cleanup: {e}")

    def close_pdf_if_open(self, file_path):
        """Close the PDF file if it's open within the application."""
        try:
            # Check if skid tags or tray tags PDFs are open
            if hasattr(self, 'skid_tags_pdf') and self.skid_tags_pdf:
                if self.skid_tags_pdf.name == file_path:
                    self.skid_tags_pdf.close()
                    self.skid_tags_pdf = None
                    print(f"Closed open PDF: {file_path}")

            if hasattr(self, 'tray_tags_pdf') and self.tray_tags_pdf:
                if self.tray_tags_pdf.name == file_path:
                    self.tray_tags_pdf.close()
                    self.tray_tags_pdf = None
                    print(f"Closed open PDF: {file_path}")
        except Exception as e:
            print(f"Error closing PDF {file_path}: {e}")

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
    def clean_up_temporary_directories(self):
        """
        Cleans up the temporary directory created by the application during execution.
        """
        try:
            # Check if running in a PyInstaller bundled app
            if getattr(sys, 'frozen', False):
                temp_dir = sys._MEIPASS  # Temporary directory used by PyInstaller
                app_temp_data_dir = os.path.join(temp_dir, "data")

                print(f"Cleaning up temporary directory: {app_temp_data_dir}")

                # Check if the directory exists
                if os.path.exists(app_temp_data_dir):
                    shutil.rmtree(app_temp_data_dir)  # Remove the directory and its contents
                    print(f"Successfully cleaned up: {app_temp_data_dir}")
                else:
                    print(f"Temporary directory does not exist: {app_temp_data_dir}")
            else:
                print("Not running in a PyInstaller bundled app. Skipping temp directory cleanup.")
        except Exception as e:
            print(f"Error during cleanup of temporary directory: {e}")
        
def main():
    try:
        app = QApplication(sys.argv)

        # Show splash screen
        print(f"DEBUG: Using splash screen from path: {splash_screen_path}")
        splash_pix = QPixmap(splash_screen_path).scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = QSplashScreen(splash_pix)
        splash.setWindowFlag(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        splash.show()
        splash.raise_()
        splash.activateWindow()
        print("DEBUG: Splash screen shown and activated.")

        # Perform initialization tasks
        perform_initialization_tasks(splash)

        # Show main window
        print("DEBUG: Initializing MainApp.")
        main_window = MainApp()
        splash.finish(main_window)
        main_window.show()
        print("DEBUG: MainApp shown and running.")

        sys.exit(app.exec())

    except Exception as e:
        # Log errors
        with open("error.log", "w") as log_file:
            log_file.write("An error occurred:\n")
            log_file.write(str(e) + "\n")
            log_file.write(traceback.format_exc())
        print(f"An error occurred. Check error.log for details: {e}")
def perform_initialization_tasks(splash):
    """
    Simulates initialization tasks with splash screen updates.
    """
    tasks = [
        "Initializing modules...",
        "Loading resources...",
        "Connecting to services...",
        "Finalizing setup..."
    ]

    for task in tasks:
        print(f"DEBUG: {task}")
        splash.showMessage(task, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        QApplication.processEvents()  # Allow UI updates during long-running tasks
        sleep(1)  # Simulate task duration



if __name__ == "__main__":
    main()
         
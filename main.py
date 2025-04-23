import sys
import os
import platform 
import shutil
from datetime import datetime 
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QSplashScreen, QComboBox, QGroupBox, QFrame, QHBoxLayout, QProgressBar
from PySide6.QtGui import QGuiApplication, QPixmap
import pandas as pd
from StatusIndicator import StatusIndicator
from csmController import CSMTab, parse_zip_and_prepare_data  # Import the tab from csmController
from printController import PrintSkidTagsTab  # Import the tab from printController
from trayController import PrintTrayTagsTab  # Import the tab from trayController
from money import MoneyTab
from update import UpdateApp
from trucking import TruckingTab
from util import clean_backend_files, clean_backend_files_with_move, process_zip_name
import stat
import requests
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
#     # Get the directory of the executable or script fff
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
    global facility_report_path, zips_address_file_path, env_file_path, splash_screen_path, rptlist

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
    rptlist = os.path.join(base_path, 'data', 'extracted', 'Reports', 'RptList.txt')

    # Print paths for debugging purposes
    print(f"DEBUG: Facility Report Path - {facility_report_path}")
    print(f"DEBUG: Zips Address File Path - {zips_address_file_path}")
    print(f"DEBUG: .env File Path - {env_file_path}")
    print(f"DEBUG: Splash Screen Path - {splash_screen_path}")
    print(f"DEBUG: RPTLIST - {rptlist}")

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

import os
print("DEBUG: All environment variables")
for key, value in os.environ.items():
    print(f"{key}: {value}")
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
    """
    Get the version from Git tags, environment variable, or fallback to the VERSION file.
    """
    try:
        # Use version from environment variable if set
        if getattr(sys, "frozen", False):  # Bundled app
            version = os.getenv("VERSION", "Unknown Version")
            if version != "Unknown Version":
                print(f"DEBUG: Retrieved version from environment variable: {version}")
                return version

        # # Try to get the version from Git tags
        # version = subprocess.check_output(
        #     ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL
        # )
        # print(f"DEBUG: Retrieved version from Git: {version.decode('utf-8').strip()}")
        # return version.decode("utf-8").strip()
    except Exception as git_error:
        print(f"DEBUG: Git version retrieval failed: {git_error}")

    # Fallback to VERSION file
    try:
        version_file_path = os.path.join(
            sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__),
            "VERSION",
        )
        with open(version_file_path, "r") as file:
            version = file.read().strip()
            print(f"DEBUG: Retrieved version from VERSION file: {version}")
            return version
    except FileNotFoundError as file_error:
        print(f"DEBUG: VERSION file not found: {file_error}")
        return "Unknown Version"


__version__ = get_version()

# Print version for confirmation
print(f"App Version: {__version__}")


updater = UpdateApp(__version__)



# Set high DPI scaling policy
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)


class MainTab(QWidget):
    """Main tab for uploading ZIP files."""

    def __init__(self, status_indicator, csm_tab, skid_tags_tab, tray_tags_tab, money_tab, trucking_tab ):
        super().__init__()

        self.setMinimumSize(1024, 768)  # Set a minimum size for the window
        self.setGeometry(100, 100, 1200, 800)  # Position and initial size
        self.status_indicator = status_indicator
        self.csm_tab = csm_tab
        self.skid_tags_tab = skid_tags_tab
        self.tray_tags_tab = tray_tags_tab
        self.money_tab = money_tab
        self.trucking_tab = trucking_tab
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Welcome and instructions with better styling
        welcome_label = QLabel("Welcome to PostFlow")
        welcome_label.setObjectName("welcomeLabel")
        self.layout.addWidget(welcome_label)
        
        instruction_label = QLabel("Use this application to manage mail data, print tags, and track finances.")
        instruction_label.setObjectName("instructionLabel")
        self.layout.addWidget(instruction_label)

        # Add a horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #cccccc;")
        self.layout.addWidget(separator)

        # Create a group box for processing mode selection
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QHBoxLayout()
        
        # Radio buttons for processing mode
        self.individual_mode_radio = QPushButton("Select Individual File")
        self.individual_mode_radio.setCheckable(True)
        self.individual_mode_radio.setChecked(True)  # Default mode
        self.individual_mode_radio.clicked.connect(self.switch_to_individual_mode)
        
        self.batch_mode_radio = QPushButton("Load All Files")
        self.batch_mode_radio.setCheckable(True)
        self.batch_mode_radio.clicked.connect(self.switch_to_batch_mode)
        
        self.historical_mode_radio = QPushButton("Access Historical Data")
        self.historical_mode_radio.setCheckable(True)
        self.historical_mode_radio.clicked.connect(self.switch_to_historical_mode)
        
        # Style radio buttons as segmented control
        mode_buttons_style = """
            QPushButton {
                border: 1px solid #0066cc;
                border-radius: 0px;
                padding: 8px 16px;
                background-color: white;
                color: #0066cc;
            }
            QPushButton:checked {
                background-color: #0066cc;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: #f0f8ff;
            }
        """
        self.individual_mode_radio.setStyleSheet(mode_buttons_style)
        self.batch_mode_radio.setStyleSheet(mode_buttons_style)
        self.historical_mode_radio.setStyleSheet(mode_buttons_style)
        
        # Create a widget for the button group to apply rounded corners to the group
        button_group_widget = QWidget()
        button_group_layout = QHBoxLayout(button_group_widget)
        button_group_layout.setContentsMargins(0, 0, 0, 0)
        button_group_layout.setSpacing(0)
        button_group_layout.addWidget(self.individual_mode_radio)
        button_group_layout.addWidget(self.batch_mode_radio)
        button_group_layout.addWidget(self.historical_mode_radio)
        
        # Set first and last button corner styles
        self.individual_mode_radio.setStyleSheet(self.individual_mode_radio.styleSheet() + 
                                             "border-top-left-radius: 4px; border-bottom-left-radius: 4px;")
        self.historical_mode_radio.setStyleSheet(self.historical_mode_radio.styleSheet() + 
                                            "border-top-right-radius: 4px; border-bottom-right-radius: 4px;")
        
        mode_layout.addWidget(button_group_widget)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        self.layout.addWidget(mode_group)

        # Create a group box for file selection (individual & historical modes)
        self.file_selection_group = QGroupBox("ZIP File Selection")
        file_layout = QVBoxLayout()
        
        # Dropdown for ZIP file selection with label
        file_layout.addWidget(QLabel("Select a MailDat ZIP file:"))
        self.zip_dropdown = QComboBox()
        self.zip_dropdown.currentIndexChanged.connect(self.select_zip_file)
        file_layout.addWidget(self.zip_dropdown)
        
        # Refresh buttons
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh ZIP Files")
        self.refresh_button.clicked.connect(self.fetch_zip_files)
        self.refresh_button.setMaximumWidth(200)
        
        self.refresh_historical_button = QPushButton("Refresh Historical Files")
        self.refresh_historical_button.clicked.connect(self.fetch_historical_files)
        self.refresh_historical_button.setMaximumWidth(200)
        self.refresh_historical_button.hide()  # Hidden by default
        
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addWidget(self.refresh_historical_button)
        refresh_layout.addStretch()
        
        file_layout.addLayout(refresh_layout)
        self.file_selection_group.setLayout(file_layout)
        self.layout.addWidget(self.file_selection_group)
        
        # Create a group box for batch processing (initially hidden)
        self.batch_processing_group = QGroupBox("Batch Processing")
        batch_layout = QVBoxLayout()
        
        # Progress information
        self.batch_status_label = QLabel("Click 'Process All Files' to download and process all recent ZIP files.")
        self.batch_status_label.setWordWrap(True)
        batch_layout.addWidget(self.batch_status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        batch_layout.addWidget(self.progress_bar)
        
        # Process button
        self.process_all_button = QPushButton("Process All Files")
        self.process_all_button.clicked.connect(self.process_all_files)
        self.process_all_button.setMaximumWidth(200)
        batch_layout.addWidget(self.process_all_button)
        
        self.batch_processing_group.setLayout(batch_layout)
        self.batch_processing_group.hide()  # Hidden by default
        self.layout.addWidget(self.batch_processing_group)

        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        # Feedback Label
        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)
        status_layout.addWidget(self.feedback_label)
        
        status_group.setLayout(status_layout)
        self.layout.addWidget(status_group)
        
        # Add stretch to push everything up
        self.layout.addStretch(1)

        # Date Display Label with better positioning
        self.date_label = QLabel(parent=self)
        self.date_label.setObjectName("dateLabel")
        self.date_label.setStyleSheet("color: #009933; font-size: 22pt; font-weight: bold;")
        self.date_label.setAlignment(Qt.AlignRight)
        self.date_label.hide()  # Hide initially
        
        # Current mode tracking
        self.current_mode = "individual"  # Default mode
        
        # Initialize with individual file selection mode
        self.fetch_zip_files()

    def switch_to_individual_mode(self):
        """Switch to individual file selection mode."""
        self.reset_selection_ui()
        self.current_mode = "individual"
        
        # Ensure only this button is checked
        self.individual_mode_radio.setChecked(True)
        self.batch_mode_radio.setChecked(False)
        self.historical_mode_radio.setChecked(False)
        
        # Update UI
        self.file_selection_group.setTitle("ZIP File Selection")
        self.file_selection_group.show()
        self.batch_processing_group.hide()
        self.refresh_button.show()
        self.refresh_historical_button.hide()
        
        # Fetch regular ZIP files
        self.fetch_zip_files()

    def switch_to_batch_mode(self):
        """Switch to batch processing mode."""
        self.reset_selection_ui()
        self.current_mode = "batch"
        
        # Ensure only this button is checked
        self.individual_mode_radio.setChecked(False)
        self.batch_mode_radio.setChecked(True)
        self.historical_mode_radio.setChecked(False)
        
        # Update UI
        self.file_selection_group.hide()
        self.batch_processing_group.show()
        
        # Reset batch processing UI
        self.progress_bar.setValue(0)
        self.batch_status_label.setText("Click 'Process All Files' to download and process all recent ZIP files.")

    def switch_to_historical_mode(self):
        """Switch to historical data access mode."""
        self.reset_selection_ui()
        self.current_mode = "historical"
        
        # Ensure only this button is checked
        self.individual_mode_radio.setChecked(False)
        self.batch_mode_radio.setChecked(False)
        self.historical_mode_radio.setChecked(True)
        
        # Update UI
        self.file_selection_group.setTitle("Historical ZIP File Selection")
        self.file_selection_group.show()
        self.batch_processing_group.hide()
        self.refresh_button.hide()
        self.refresh_historical_button.show()
        
        # Fetch historical ZIP files
        self.fetch_historical_files()

    def reset_selection_ui(self):
        """Reset UI elements related to file selection."""
        self.zip_dropdown.clear()
        self.zip_dropdown.addItem("Please select a MailDat file")
        self.feedback_label.setText("")
        self.date_label.hide()
        self.reset_all_tabs()

    def fetch_zip_files(self):
        """Fetch the latest ZIP files from the FTP server for individual selection."""
        from util import fetch_latest_ftp_files  # Assuming this function exists in util.py

        try:
            # Clear the dropdown before adding new items
            self.zip_dropdown.clear()

            # Add the default option
            self.zip_dropdown.addItem("Please select a MailDat file")
            zip_files = fetch_latest_ftp_files()  # This should return a list of ZIP filenames
            self.zip_dropdown.addItems(zip_files)
            self.feedback_label.setText("Fetched latest ZIP files successfully!")
            self.feedback_label.setStyleSheet("color: #009933;")
        except Exception as e:
            self.feedback_label.setText(f"Error fetching ZIP files: {e}")
            self.feedback_label.setStyleSheet("color: #cc3300;")

    def fetch_historical_files(self):
        """Fetch historical ZIP files from the backup folder on the FTP server."""
        from util import fetch_backup_ftp_files  # New function to fetch from backup folder

        try:
            # Clear the dropdown before adding new items
            self.zip_dropdown.clear()

            # Add the default option
            self.zip_dropdown.addItem("Please select a historical MailDat file")
            zip_files = fetch_backup_ftp_files()  # Fetch files from backup folder
            self.zip_dropdown.addItems(zip_files)
            self.feedback_label.setText("Fetched historical ZIP files successfully!")
            self.feedback_label.setStyleSheet("color: #009933;")
        except Exception as e:
            self.feedback_label.setText(f"Error fetching historical ZIP files: {e}")
            self.feedback_label.setStyleSheet("color: #cc3300;")

    def process_all_files(self):
        """Process all available ZIP files in batch mode."""
        from util import download_and_process_all_files
        
        # Reset state
        self.reset_all_tabs()
        self.progress_bar.setValue(0)
        self.batch_status_label.setText("Starting batch processing...")
        
        # Disable the button during processing
        self.process_all_button.setEnabled(False)
        
        try:
            # Process all files with progress updates
            def update_progress(message, percentage):
                self.batch_status_label.setText(message)
                self.progress_bar.setValue(int(percentage))
                QApplication.processEvents()  # Ensure UI updates
            
            # Start processing
            # Correct unpacking to expect 5 values
            combined_df, processed_zip_files, report_file_paths, errors, merged_pdfs = download_and_process_all_files(update_progress)
            
            if combined_df.empty:
                if errors:
                    error_text = "\n".join(errors[:3])  # Show first 3 errors
                    if len(errors) > 3:
                        error_text += f"\n...and {len(errors) - 3} more errors."
                    self.batch_status_label.setText(f"Batch processing completed with errors:\n{error_text}")
                else:
                    self.batch_status_label.setText("No data was processed. Please check the FTP server or try again.")
            else:
                # Update tabs with the combined data
                self.csm_tab.update_data(combined_df)
                
                # Load merged PDF files if available
                extracted_path = "data/extracted"
                
                # Load merged SkidTags.pdf
                if "SkidTags" in merged_pdfs:
                    self.skid_tags_tab.load_pdf(merged_pdfs["SkidTags"])
                    self.status_indicator.set_status("Skid Tags", True)
                else:
                    print("No merged SkidTags PDF was created.")
                    
                # Load merged TrayTags.pdf
                if "TrayTags" in merged_pdfs:
                    self.tray_tags_tab.load_pdf(merged_pdfs["TrayTags"])
                    self.status_indicator.set_status("Tray Tags", True)
                else:
                    print("No merged TrayTags PDF was created.")
                
                # Update money tab with combined report data
                if report_file_paths: # Check if any report files were found
                    from util import process_batch_rptlist
                    combined_report_data, report_headers, report_skipped_lines = process_batch_rptlist(report_file_paths)
                    self.money_tab.load_batch_report(combined_report_data, report_headers)
                    if report_skipped_lines:
                        print(f"Skipped {len(report_skipped_lines)} lines during batch report processing.")
                        # Optionally, display skipped lines info in UI
                else:
                    print("DEBUG: No RptList.txt files found for batch processing.")
                    self.money_tab.reset() # Clear money tab if no reports
                    
                # Update status indicator for ZIP files
                self.status_indicator.set_status("ZIP", True)
                
                # Show success message
                self.batch_status_label.setText(f"Successfully processed {len(processed_zip_files)} files. " + 
                                              f"Combined data contains {len(combined_df)} records." +
                                              (f" Merged {len(merged_pdfs)} PDF type(s)." if merged_pdfs else ""))
                
                # Set a batch name for reporting
                batch_name = f"Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.csm_tab.set_processed_zip_name(batch_name)
                
                # Update feedback
                self.feedback_label.setText(f"Batch processing completed successfully: {len(processed_zip_files)} files processed.")
                self.feedback_label.setStyleSheet("color: #009933;")
                
                # Set a generic date for batch processing
                batch_date = datetime.now().strftime("%B %d, %Y")
                self.date_label.setText(f"Batch Processed: {batch_date}")
                self.date_label.adjustSize()
                self.date_label.show()
                self.resizeEvent(None)  # Reposition the label
        except Exception as e:
            self.batch_status_label.setText(f"Error during batch processing: {e}")
            self.feedback_label.setText(f"Error during batch processing: {e}")
            self.feedback_label.setStyleSheet("color: #cc3300;")
        finally:
            # Re-enable the button
            self.process_all_button.setEnabled(True)

    def select_zip_file(self):
        """Handle ZIP file selection and reset data."""
        self.reset_all_tabs()
        selected_file = self.zip_dropdown.currentText()
        if selected_file == "Please select a MailDat file" or selected_file == "Please select a historical MailDat file":
            return  # Do nothing if the default option is selected

        if selected_file:
            try:
                # Download and process the selected ZIP file based on current mode
                from util import download_file_from_ftp, download_file_from_backup_ftp
                
                self.feedback_label.setText(f"Downloading {selected_file}...")
                self.feedback_label.setStyleSheet("color: #0066cc;")
                
                # Use the appropriate download function based on current mode
                if self.current_mode == "historical":
                    local_file_path = download_file_from_backup_ftp(selected_file)
                else:
                    local_file_path = download_file_from_ftp(selected_file)
                
                self.feedback_label.setText(f"Processing {selected_file}...")
                df_filtered = parse_zip_and_prepare_data(local_file_path)

                # Update tabs with new data
                self.csm_tab.update_data(df_filtered)

                extracted_report_path = os.path.join("data", "extracted", "Reports", "RptList.txt")
                if os.path.exists(extracted_report_path):
                    print(f"DEBUG: Notifying MoneyTab to reload report: {extracted_report_path}")
                    self.money_tab.reload_report(extracted_report_path)
                else:
                    print("DEBUG: RptList.txt does not exist, skipping reload.")

                # Extract the date from the file name
                date_from_file = self.extract_date_from_file(local_file_path)
                mode_prefix = "Historical: " if self.current_mode == "historical" else ""
                self.feedback_label.setText(f"Loaded data from {selected_file} ({mode_prefix}IHD: {date_from_file})")
                self.feedback_label.setStyleSheet("color: #009933;")

                # Update and show the date label
                self.date_label.setText(f"{mode_prefix}IHD: {date_from_file}")
                self.date_label.adjustSize()  # Adjust size for text
                self.date_label.show()  # Show the date label
                self.resizeEvent(None)  # Reposition the label after updating

                zip_base_name = os.path.splitext(selected_file)[0]
                # Process the ZIP name
                processed_zip_name = process_zip_name(zip_base_name)
                print(f"Processed ZIP Name: {processed_zip_name}")
                # Pass the processed ZIP name to the CSMTab instance
                self.csm_tab.set_processed_zip_name(processed_zip_name)

                # Define the extracted path
                extracted_path = "data/extracted"

                # Load SkidTags.pdf if it exists
                skid_tags_pdf_path = os.path.join(extracted_path, "Reports", "SkidTags.pdf")
                if os.path.exists(skid_tags_pdf_path):
                    self.skid_tags_tab.load_pdf(skid_tags_pdf_path)
                else:
                    print("SkidTags.pdf not found in the extracted ZIP file.")

                # Load TrayTags.pdf if it exists
                tray_tags_pdf_path = os.path.join(extracted_path, "Reports", "TrayTags.pdf")
                if os.path.exists(tray_tags_pdf_path):
                    self.tray_tags_tab.load_pdf(tray_tags_pdf_path)
                else:
                    print("TrayTags.pdf not found in the extracted ZIP file.")

                # Update ZIP status
                self.status_indicator.set_status("ZIP", True if os.path.exists(local_file_path) else False)

            except Exception as e:
                self.status_indicator.set_status("ZIP", False)
                self.feedback_label.setText(f"Error processing file {selected_file}: {e}")
                self.feedback_label.setStyleSheet("color: #cc3300;")

    def reset_all_tabs(self):
        data_path = "data/extracted"
        
        """Reset all tabs to ensure no lingering data remains."""
        if hasattr(self, 'csm_tab'):
            self.csm_tab.reset()
        if hasattr(self, 'skid_tags_tab'):
            self.skid_tags_tab.reset()
        if hasattr(self, 'tray_tags_tab'):
            self.tray_tags_tab.reset()
        print("All tabs reset.")

        # Hide the date label
        self.date_label.setText("")
        self.date_label.hide()

        # Reset the status indicators
        self.status_indicator.reset_status()

        clean_backend_files()
        
    def extract_date_from_file(self, file_path):
        """Extract the date from the file name in MM-DD-YY format."""
        try:
            file_name = os.path.basename(file_path)
            date_part = file_name.split(" ")[1].split("_")[0]
            return datetime.strptime(date_part, "%m-%d-%y").strftime("%B %d, %Y")
        except Exception:
            return "Unknown Date"   

    def resizeEvent(self, event):
        """Reposition the date label on window resize."""
        super().resizeEvent(event)
        # Position date label at the top-right corner
        if self.date_label.isVisible():
            self.date_label.move(self.width() - self.date_label.width() - 20, 10)


    # def upload_zip(self):
    #     # self.clean_up_directories()
    #     """Handle ZIP file upload and processing."""
    #     # Dynamically determine the OS
    #     current_os = platform.system()
    #         # Process the ZIP name
        
    #     # processed_zip_name = process_zip_name(self)
    #     # print(f"Processed ZIP Name: {processed_zip_name}")
    
    #     # # Pass the processed ZIP name to save_reports
    #     # save_reports(processed_zip_name)

    #     # Define the default folder based on the OS
    #     if current_os == "Windows":
    #         default_folder = r"\\cbahqdist-ts\DIST_L_JCTS\UMS Presort\in\hold"
    #     elif current_os == "Darwin":  # macOS
    #         default_folder = os.path.expanduser("~/Documents") 
    #     else:  # For Linux or other OS
    #         default_folder = os.path.expanduser("~/") 

    #     zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP File",default_folder, "ZIP Files (*.zip)")
    #     if zip_file_path:
    #         try:
    #             # Parse the ZIP file and update the CSM tab
    #             df_filtered = parse_zip_and_prepare_data(zip_file_path)

    #             self.csm_tab.update_data(df_filtered)
    #             # Extract the date from the data or filename
    #             date_from_file = self.extract_date_from_file(zip_file_path)
    #             # Extract the base name and remove the '.zip' extension
    #             zip_base_name = os.path.basename(zip_file_path).replace('.zip', '')
    #             # Process the ZIP name
    #             processed_zip_name = process_zip_name(zip_base_name)
    #             print(f"Processed ZIP Name: {processed_zip_name}")
    #             # Pass the processed ZIP name to the CSMTab instance
    #             self.csm_tab.set_processed_zip_name(processed_zip_name)

               
    #             # Update and show the date label
    #             self.date_label.setText(f"IHD: {date_from_file}")
    #             self.date_label.adjustSize()  # Adjust size for text
    #             self.date_label.show()  # Show the date label
    #             self.resizeEvent(None)  # Reposition the label after updating

    #             self.feedback_label.setText("File uploaded and data processed successfully!")
    #             self.feedback_label.setStyleSheet("color: green;")

    #             # Load SkidTags.pdf if it exists
    #             extracted_path = "data/extracted"
    #             skid_tags_pdf_path = os.path.join(extracted_path, "Reports", "SkidTags.pdf")
    #             if os.path.exists(skid_tags_pdf_path):
    #                 self.skid_tags_tab.load_pdf(skid_tags_pdf_path)
    #                 self.feedback_label.setText("ZIP file uploaded and data processed successfully!")
    #                 self.feedback_label.setStyleSheet("color: green;")
    #             else:
    #                 self.feedback_label.setText("SkidTags.pdf not found in the extracted ZIP file.")
    #                 self.feedback_label.setStyleSheet("color: red;")

    #             # Load TrayTags.pdf if it exists
    #             tray_tags_pdf_path = os.path.join(extracted_path, "Reports", "TrayTags.pdf")
    #             if os.path.exists(tray_tags_pdf_path):
    #                 self.tray_tags_tab.load_pdf(tray_tags_pdf_path)
    #                 self.feedback_label.setText("ZIP file uploaded and data processed successfully!")
    #                 self.feedback_label.setStyleSheet("color: green;")
    #             else:
    #                 self.feedback_label.setText("TrayTags.pdf not found in the extracted ZIP file.")
    #                 self.feedback_label.setStyleSheet("color: red;")

    #         except Exception as e:
    #             self.feedback_label.setText(f"Error processing ZIP file: {e}")
    #             self.feedback_label.setStyleSheet("color: red;")

    # def extract_date_from_file(self, file_path):
    #     """Extract the date from the file name in MM-DD-YY format."""
    #     try:
    #         # Extracting date part (assuming format: 'MailDate MM-DD-YY_...')
    #         file_name = os.path.basename(file_path)
    #         date_part = file_name.split(" ")[1].split("_")[0]  # Get '12-13-24'
    #         file_date = datetime.strptime(date_part, "%m-%d-%y").strftime("%B %d, %Y")
    #         return file_date
    #     except Exception:
    #         return "Unknown Date"
        



class MainApp(QMainWindow):
    """Main application window with tabbed navigation."""

    def __init__(self):
        super().__init__()
        print("DEBUG: Initializing MainApp...")
        self.setWindowTitle("PostFlow - Mail Data Management")
        
        # Load the application stylesheet
        self.load_stylesheet()
        
        # Ensure the window size fits within the screen dimensions
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Set the window size relative to the screen size (e.g., 80% width and height)
        self.resize(int(screen_width * 0.8), int(screen_height * 0.8))

        # Add the app version to the status bar
        self.statusBar().showMessage(f"Version: {__version__}")

        # Initialize the StatusIndicator and add it to the status bar
        self.status_indicator = StatusIndicator(self)
        self.statusBar().addPermanentWidget(self.status_indicator)
        print("DEBUG: StatusIndicator added to status bar.")

        # Create a modern layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        # Create app header with logo
        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        # App title
        self.app_title = QLabel("PostFlow")
        self.app_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #0066cc;")
        self.header_layout.addWidget(self.app_title)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #cccccc;")
        self.header_layout.addWidget(separator)
        
        self.main_layout.addWidget(self.header_widget)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # More modern look for tabs
        self.main_layout.addWidget(self.tab_widget)

        # Create the tabs
        self.csm_tab = CSMTab(pd.DataFrame())  # Use the existing implementation of CSMTab
        self.skid_tags_tab = PrintSkidTagsTab(self.status_indicator)
        self.tray_tags_tab = PrintTrayTagsTab(self.status_indicator)
        self.money_tab = MoneyTab(rptlist)
        self.trucking_tab = TruckingTab()
        self.main_tab = MainTab(self.status_indicator, self.csm_tab, self.skid_tags_tab, self.tray_tags_tab, self.money_tab, self.trucking_tab)

        # Add tabs to the application with icons (text-based for now)
        self.tab_widget.addTab(self.main_tab, "🏠 Home")
        self.tab_widget.addTab(self.csm_tab, "📋 CSM")
        self.tab_widget.addTab(self.skid_tags_tab, "🏷️ Print Skid Tags")
        self.tab_widget.addTab(self.tray_tags_tab, "🏷️ Print Tray Tags")
        self.tab_widget.addTab(self.money_tab, "💰 USPS $")
        self.tab_widget.addTab(self.trucking_tab, "🚚 Trucking")
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def load_stylesheet(self):
        """Load the application stylesheet."""
        self.stylesheet_loaded = False
        try:
            # Try multiple potential stylesheet locations
            stylesheet_paths = [
                "styles.qss",  # Current directory
                os.path.join(os.path.dirname(__file__), "styles.qss"),  # Script directory
                os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "styles.qss"),  # Executable directory
                os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(__file__)), "styles.qss")  # PyInstaller bundle
            ]
            
            for stylesheet_path in stylesheet_paths:
                if os.path.exists(stylesheet_path):
                    with open(stylesheet_path, "r") as f:
                        style_content = f.read()
                        self.setStyleSheet(style_content)  # Apply globally
                        self.main_tab.setStyleSheet(style_content)  # Apply to main tab
                    print(f"DEBUG: Loaded stylesheet from {stylesheet_path}")
                    self.stylesheet_loaded = True
                    break
            
            if not self.stylesheet_loaded:
                print("WARNING: Could not find stylesheet file in any expected location")
        except Exception as e:
            print(f"DEBUG: Error loading stylesheet: {e}")
            
    def on_tab_changed(self, index):
        """Handle tab change events."""
        current_tab = self.tab_widget.widget(index)
        # Refresh or update the current tab if needed
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
        
        # Update window title to include current tab name
        tab_name = self.tab_widget.tabText(index)
        self.setWindowTitle(f"PostFlow - {tab_name}")

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
        
        # Set application-wide attributes
        app.setStyle('Fusion')  # Use Fusion style for a modern look
        
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

        # Create and show main window
        print("DEBUG: Initializing MainApp.")
        main_window = MainApp()
        
        # Check for stylesheet loading and ensure it's applied
        # First try to find the stylesheet in various locations
        stylesheet_found = False
        stylesheet_paths = [
            "styles.qss",  # Current directory
            os.path.join(os.path.dirname(__file__), "styles.qss"),  # Script directory
            os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "styles.qss"),  # Executable directory
            os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(__file__)), "styles.qss")  # PyInstaller bundle
        ]
        
        for path in stylesheet_paths:
            if os.path.exists(path):
                print(f"DEBUG: Found stylesheet at: {path}")
                try:
                    with open(path, "r") as f:
                        style_content = f.read()
                        app.setStyleSheet(style_content)  # Apply globally
                        main_window.setStyleSheet(style_content)  # Apply to main window
                    print(f"DEBUG: Successfully applied stylesheet from {path}")
                    stylesheet_found = True
                    break
                except Exception as e:
                    print(f"DEBUG: Error loading stylesheet from {path}: {e}")
        
        if not stylesheet_found:
            print("WARNING: Could not find stylesheet file in any expected location")
            
        # Finish splash and show main window
        splash.finish(main_window)
        main_window.show()
        print("DEBUG: MainApp shown and running.")
        
        # Check for updates
        updater.check_for_updates()

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
        "Initializing application...",
        "Loading resources...",
        "Connecting to services...",
        "Setting up interface...",
        "Finalizing setup..."
    ]

    # Style the splash screen text
    splash.setStyleSheet("""
        QSplashScreen {
            color: white;
            font-size: 14pt;
            font-weight: bold;
        }
    """)

    for i, task in enumerate(tasks):
        progress = int((i + 1) / len(tasks) * 100)
        message = f"{task} ({progress}%)"
        print(f"DEBUG: {message}")
        splash.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        QApplication.processEvents()  # Allow UI updates during long-running tasks
        sleep(0.8)  # Shorter delay for a more responsive feel



if __name__ == "__main__":
    main()
    # print(f"DEBUG: StatusIndicator geometry: {main.status_indicator.geometry()}")
         
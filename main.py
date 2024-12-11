import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
from csmController import CSMTab, parse_zip_and_prepare_data # Import the tab from csmController
from printController import PrintSkidTagsTab  # Import the tab from printController
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    # main_window.show()
    # Show the window maximized (full-screen mode)
    main_window.showMaximized()
    sys.exit(app.exec())


    # TODO: Implement print display and actually print
    # TODO: should we clear data on exit?
    # TODO: Display IHD on main page after data is uploaded so when moving back and forth its relavant also maybe put it in the status bar!!!
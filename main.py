import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
from csmController import CSMTab, df_filtered  # Import the CSMTab class and df_filtered


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.setWindowTitle("Mail Data Management System")
        self.resize(1000, 700)  # Initial size if not full-screen

        # Main layout: Tabs as Top Navigation
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Add tabs
        self.tab_widget.addTab(CSMTab(df_filtered), "CSM")  # Pass df_filtered to the CSMTab
        self.tab_widget.addTab(self.create_print_skid_tags_tab(), "Print Skid Tags")  # Add placeholder tab

    def create_print_skid_tags_tab(self):
        """Create the Print Skid Tags placeholder tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Print Skid Tags Content Here"))
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()

    # Show the window maximized (full-screen mode)
    main_window.showMaximized()

    sys.exit(app.exec())
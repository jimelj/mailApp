import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QLabel, QListWidget, QStackedWidget
)
from PySide6.QtCore import Qt
from csmController import CSMTab  # Import the CSM tab logic


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.setWindowTitle("Mail Data Management System")
        self.resize(1000, 700)

        # Main layout: Sidebar + Content
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Sidebar (Left Navigation)
        self.sidebar = QListWidget()
        self.sidebar.addItem("CSM")
        self.sidebar.addItem("Print Skid Tags")
        self.sidebar.currentRowChanged.connect(self.change_tab)
        self.sidebar.setMaximumWidth(200)

        # Content Area
        self.content = QStackedWidget()

        # Add tabs
        self.tabs = {
            "CSM": CSMTab(),
            "Print Skid Tags": QLabel("Print Skid Tags Content Here"),  # Placeholder
        }
        for tab in self.tabs.values():
            self.content.addWidget(tab)

        # Add to layout
        main_layout.addWidget(self.sidebar, alignment=Qt.AlignLeft)
        main_layout.addWidget(self.content)

        # Show the first tab
        self.sidebar.setCurrentRow(0)

    def change_tab(self, index):
        """Switch content based on sidebar selection."""
        self.content.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
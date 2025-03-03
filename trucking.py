# trucking.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QColor, QBrush, QFont
import requests
import os
from dotenv import load_dotenv

class TruckingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("Trucking 🚚 - Data from Capstone API")
        self.layout.addWidget(self.info_label)

        self.fetch_button = QPushButton("Fetch Trucking Data")
        self.fetch_button.clicked.connect(self.fetch_data)
        self.layout.addWidget(self.fetch_button)

        # Initialize table widget
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        # Configure table headers
        headers = [
            "ID", "Barcode","Destination", "Scan Status", "Last Scanned", 
            "Address Name", "Scanned Address", "POD"
        ]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def fetch_data(self):
        try:
            load_dotenv()
            api_url = os.getenv("CAPSTONE_API_URL")
            response = requests.get(f"{api_url}/parcelsweek")
            response.raise_for_status()
            parcels = response.json()

            self.table_widget.setRowCount(len(parcels))

            for row, parcel in enumerate(parcels):
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(parcel.get('id'))))
                self.table_widget.setItem(row, 1, QTableWidgetItem(parcel.get('barcode')))
                self.table_widget.setItem(row, 2, QTableWidgetItem(parcel.get('destination_name')))
                
                scan_status_item = QTableWidgetItem(parcel.get('scan_status'))
                scan_status = parcel.get('scan_status').lower()

                # Conditional formatting based on scan status
                if scan_status == "delivered":
                    scan_status_item.setBackground(QBrush(QColor("green")))
                    scan_status_item.setForeground(QBrush(QColor("white")))
                    scan_status_item.setFont(QFont("", weight=QFont.Bold))
                elif scan_status == "picked up":
                    scan_status_item.setBackground(QBrush(QColor("orange")))
                    scan_status_item.setForeground(QBrush(QColor("black")))
                    scan_status_item.setFont(QFont("", weight=QFont.Bold))

                self.table_widget.setItem(row, 3, scan_status_item)

                self.table_widget.setItem(row, 4, QTableWidgetItem(parcel.get('last_scanned_when')))
                self.table_widget.setItem(row, 5, QTableWidgetItem(parcel.get('address_name')))

                # Combine address fields into one string
                scanned_address = ", ".join(filter(None, [
                    parcel.get('address1'),
                    parcel.get('address2'),
                    parcel.get('city'),
                    parcel.get('state'),
                    parcel.get('zip')
                ]))

                self.table_widget.setItem(row, 6, QTableWidgetItem(scanned_address))
                self.table_widget.setItem(row, 7, QTableWidgetItem(parcel.get('pod')))

            # Resize columns again after populating to ensure full value visibility
            self.table_widget.resizeColumnsToContents()

        except Exception as e:
            print(f"Error fetching data: {e}")
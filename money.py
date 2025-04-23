import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtCore import Qt

class MoneyTab(QWidget):
    def __init__(self, report_file):
        super().__init__()
        self.current_report_file = report_file
        self.init_ui()
        self.load_report()  # Load initial report if provided

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.table_display = QTableWidget()
        self.table_display.setObjectName("moneyTableWidget") # For specific styling
        self.layout.addWidget(self.table_display)
        
        # Add label for skipped lines if any
        self.skipped_label = QLabel("")
        self.skipped_label.setStyleSheet("color: orange;")
        self.skipped_label.setVisible(False)
        self.layout.addWidget(self.skipped_label)

    def reload_report(self, report_file):
        """Reloads the report data from the specified file path."""
        self.current_report_file = report_file
        self.load_report()

    def load_report(self):
        """Loads and processes the report file to display in the table."""
        if not self.current_report_file or not os.path.exists(self.current_report_file):
            print(f"DEBUG: Report file does not exist or not specified: {self.current_report_file}")
            self.table_display.clear()
            self.table_display.setRowCount(0)
            self.table_display.setColumnCount(0)
            self.skipped_label.setText("Report file (RptList.txt) not found.")
            self.skipped_label.setVisible(True)
            return

        try:
            from util import process_single_rptlist # Import the processing function
            data, report_totals, headers, skipped_lines = process_single_rptlist(self.current_report_file)
            
            # Add the totals row extracted from the report itself
            if report_totals['copies'] > 0: # Check if totals were found
                cpm = (report_totals['postage'] / report_totals['copies']) * 1000 if report_totals['copies'] != 0 else 0
                piece_weight = (report_totals['weight'] / report_totals['copies']) * 16 if report_totals['copies'] != 0 else 0
                totals_row = [
                    "Report Totals:", 
                    "", 
                    report_totals['copies'], 
                    report_totals['weight'], 
                    f"${report_totals['postage']:.2f}", 
                    f"${cpm:.2f}", 
                    f"{piece_weight:.2f} oz"
                ]
                data.append(totals_row)
            
            self.populate_table(data, headers)

            if skipped_lines:
                self.skipped_label.setText(f"Skipped {len(skipped_lines)} lines during processing. Check logs for details.")
                self.skipped_label.setVisible(True)
                print("Skipped lines:")
                for line in skipped_lines:
                    print(line)
            else:
                self.skipped_label.setVisible(False)
        except Exception as e:
            print(f"Error loading or processing report {self.current_report_file}: {e}")
            self.table_display.clear()
            self.table_display.setRowCount(1)
            self.table_display.setColumnCount(1)
            self.table_display.setItem(0, 0, QTableWidgetItem(f"Error processing report: {e}"))
            self.skipped_label.setVisible(False)

    def load_batch_report(self, combined_data, headers):
        """Loads combined data from batch processing into the table."""
        self.populate_table(combined_data, headers)
        # Optionally handle skipped lines if provided differently for batch
        self.skipped_label.setVisible(False) # Hide skipped label for batch summary

    def populate_table(self, data, headers):
        """Populates the QTableWidget with parsed data and auto-resizes columns."""
        self.table_display.setColumnCount(len(headers))
        self.table_display.setHorizontalHeaderLabels(headers)
        self.table_display.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                self.table_display.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        # Resize columns to show full content.
        self.table_display.resizeColumnsToContents()

    def reset(self):
        """Clears the table and resets the state."""
        self.table_display.clear()
        self.table_display.setRowCount(0)
        self.table_display.setColumnCount(0)
        self.skipped_label.setVisible(False)
        print("MoneyTab reset.")
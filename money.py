import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel

class MoneyTab(QWidget):
    def __init__(self, report_file):
        super().__init__()
        self.report_file = report_file
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Label to display status messages.
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Table widget to display report data.
        self.table_display = QTableWidget()
        layout.addWidget(self.table_display)

        self.setLayout(layout)

    def reload_report(self, report_file):
        """Reloads the report file and updates the display."""
        self.report_file = report_file
        self.load_report()

    def load_report(self):
        """Reads the report file and displays formatted data in a table."""
        if not os.path.exists(self.report_file):
            self.status_label.setText("Report file not found.")
            return

        data, headers, skipped_lines = self.process_report(self.report_file)

        if data:
            self.populate_table(data, headers)
            if len(skipped_lines) > 0:
                self.status_label.setText(f"Skipped {len(skipped_lines)} lines.")
            else:
                self.status_label.setText("")  # Show nothing if no lines were skipped.
        else:
            self.table_display.clear()
            self.status_label.setText("No valid data found.")

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

    @staticmethod
    def process_report(file_path):
        """
        Processes the report file and returns structured data and headers.

        For regular data rows:
        - Lines starting with "DDU-" or "SCF-" are processed.
        - The entry point name is determined dynamically (collecting tokens until the first numeric token).
        - From the numeric tokens, only the following three fields are kept:
            • Total Copies (token index 9; converted to int)
            • Total Weight (token index 10)
            • Total Postage (token index 11)
        - The drop site key is captured from the following line and inserted as the second column.
        - Two new columns are calculated:
                • CPM = (Total Postage / Total Copies) * 1000  
                • Piece Weight = (Total Weight / Total Copies)
        For the totals row:
        - A line starting with "Report Totals:" is processed similarly, and the extra columns are appended.
        """
        data = []
        headers = ["Entry Point Name", "Drop Site Key", "Total Copies", "Total Weight", "Total Postage", "CPM", "AVR Piece Weight"]
        skipped_lines = []

        with open(file_path, "r") as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip irrelevant lines.
            if not line or line.startswith(("", "Summary", "Page", "CBA", "-------")):
                i += 1
                continue

            # Process the totals row.
            if line.startswith("Report Totals:"):
                parts = line.split(":", 1)
                if len(parts) < 2:
                    skipped_lines.append(f"Malformed totals line: {line}")
                    i += 1
                    continue
                totals_line = parts[1].strip()
                tokens = totals_line.split()
                # Filter out stray "$" tokens.
                tokens = [t for t in tokens if t != "$"]
                if len(tokens) < 12:
                    skipped_lines.append(f"Insufficient tokens in totals line: {line}")
                    i += 1
                    continue
                try:
                    total_copies = int(float(tokens[9]))   # Token 9: Total Copies.
                    total_weight = float(tokens[10])
                    total_postage = float(tokens[11])
                except ValueError as e:
                    skipped_lines.append(f"Error converting totals tokens in line: {line} | {e}")
                    i += 1
                    continue

                if total_copies != 0:
                    cpm = (total_postage / total_copies) * 1000
                    piece_weight = total_weight / total_copies
                else:
                    cpm = 0
                    piece_weight = 0

                totals_row = [
                    "Report Totals:", 
                    "", 
                    total_copies, 
                    total_weight, 
                    f"${total_postage:.2f}", 
                    f"${cpm:.2f}", 
                    f"{piece_weight:.2f}"
                ]
                data.append(totals_row)
                i += 1
                continue

            # Process regular data lines.
            if line.startswith("DDU-") or line.startswith("SCF-"):
                parts = line.split()

                # Dynamically determine the entry point name by collecting tokens until a numeric token is found.
                name_tokens = []
                numeric_start_index = None
                for idx, token in enumerate(parts):
                    if token == "$":
                        continue
                    try:
                        float(token.replace("$", ""))
                        numeric_start_index = idx
                        break
                    except ValueError:
                        name_tokens.append(token)
                if numeric_start_index is None:
                    skipped_lines.append(f"Could not find numeric data in line: {line}")
                    i += 1
                    continue

                entry_point_name = " ".join(name_tokens)
                numerical_data = parts[numeric_start_index:]
                numerical_data = [p for p in numerical_data if p != "$"]

                if len(numerical_data) < 12:
                    skipped_lines.append(f"Insufficient numeric tokens in line: {line}")
                    i += 1
                    continue

                try:
                    total_copies = int(float(numerical_data[9]))
                    total_weight = float(numerical_data[10])
                    total_postage = float(numerical_data[11])
                except ValueError as e:
                    skipped_lines.append(f"Error converting numeric tokens in line: {line} | {e}")
                    i += 1
                    continue

                if total_copies != 0:
                    cpm = (total_postage / total_copies) * 1000
                    piece_weight = total_weight / total_copies * 16
                else:
                    cpm = 0
                    piece_weight = 0

                # Look ahead for the drop site key.
                drop_site_key = None
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith("-------"):
                        if next_line.startswith("Drop Site Key:"):
                            drop_site_key = next_line.split(":", 1)[1].strip()
                        break
                    j += 1
                i = j + 1

                formatted_row = [
                    entry_point_name,
                    drop_site_key,
                    total_copies,
                    total_weight,
                    f"${total_postage:.2f}",
                    f"${cpm:.2f}",
                    f"{piece_weight:.2f}"
                ]
                data.append(formatted_row)
            else:
                i += 1

        return data, headers, skipped_lines

    # @staticmethod
    # def process_report(file_path):
    #     """
    #     Processes the report file and returns structured data and headers.

    #     For regular data rows:
    #       - Lines starting with "DDU-" or "SCF-" are processed.
    #       - The entry point name is determined dynamically (collecting tokens until the first numeric token).
    #       - From the numeric tokens, only the following three fields are kept:
    #           • Total Copies (token index 9; converted to int)
    #           • Total Weight (token index 10)
    #           • Total Postage (token index 11, formatted with a '$')
    #       - The drop site key is captured from the following line and inserted as the second column.

    #     For the totals row:
    #       - A line starting with "Report Totals:" is processed similarly.
    #       - The resulting row uses "Report Totals:" as the entry point name, an empty drop site key,
    #         and then the three totals fields (with Total Postage formatted with a '$').
    #     """
    #     data = []
    #     headers = ["Entry Point Name", "Drop Site Key", "Total Copies", "Total Weight", "Total Postage"]
    #     skipped_lines = []

    #     with open(file_path, "r") as file:
    #         lines = file.readlines()

    #     i = 0
    #     while i < len(lines):
    #         line = lines[i].strip()

    #         # Skip lines that are clearly not part of the data.
    #         if not line or line.startswith(("", "Summary", "Page", "CBA", "-------")):
    #             i += 1
    #             continue

    #         # Process the totals row.
    #         if line.startswith("Report Totals:"):
    #             parts = line.split(":", 1)
    #             if len(parts) < 2:
    #                 skipped_lines.append(f"Malformed totals line: {line}")
    #                 i += 1
    #                 continue
    #             totals_line = parts[1].strip()
    #             tokens = totals_line.split()
    #             # Filter out stray "$" tokens.
    #             tokens = [t for t in tokens if t != "$"]
    #             if len(tokens) < 12:
    #                 skipped_lines.append(f"Insufficient tokens in totals line: {line}")
    #                 i += 1
    #                 continue
    #             try:
    #                 total_copies = int(float(tokens[9]))   # Token 9: Total Copies.
    #                 total_weight = float(tokens[10])
    #                 total_postage = float(tokens[11])
    #             except ValueError as e:
    #                 skipped_lines.append(f"Error converting totals tokens in line: {line} | {e}")
    #                 i += 1
    #                 continue
    #             totals_row = ["Report Totals:", "", total_copies, total_weight, f"${total_postage:.2f}"]
    #             data.append(totals_row)
    #             i += 1
    #             continue

    #         # Process regular data lines.
    #         if line.startswith("DDU-") or line.startswith("SCF-"):
    #             parts = line.split()
    #             # Dynamically determine the entry point name by collecting tokens until a numeric token is found.
    #             name_tokens = []
    #             numeric_start_index = None
    #             for idx, token in enumerate(parts):
    #                 if token == "$":
    #                     continue
    #                 try:
    #                     float(token.replace("$", ""))
    #                     numeric_start_index = idx
    #                     break
    #                 except ValueError:
    #                     name_tokens.append(token)
    #             if numeric_start_index is None:
    #                 skipped_lines.append(f"Could not find numeric data in line: {line}")
    #                 i += 1
    #                 continue

    #             entry_point_name = " ".join(name_tokens)
    #             numerical_data = parts[numeric_start_index:]
    #             numerical_data = [p for p in numerical_data if p != "$"]

    #             if len(numerical_data) < 12:
    #                 skipped_lines.append(f"Insufficient numeric tokens in line: {line}")
    #                 i += 1
    #                 continue

    #             try:
    #                 total_copies = int(float(numerical_data[9]))
    #                 total_weight = float(numerical_data[10])
    #                 total_postage = float(numerical_data[11])
    #             except ValueError as e:
    #                 skipped_lines.append(f"Error converting numeric tokens in line: {line} | {e}")
    #                 i += 1
    #                 continue

    #             # Look ahead for the drop site key.
    #             drop_site_key = None
    #             j = i + 1
    #             while j < len(lines):
    #                 next_line = lines[j].strip()
    #                 if next_line and not next_line.startswith("-------"):
    #                     if next_line.startswith("Drop Site Key:"):
    #                         drop_site_key = next_line.split(":", 1)[1].strip()
    #                     break
    #                 j += 1
    #             i = j + 1

    #             formatted_row = [entry_point_name, drop_site_key, total_copies, total_weight, f"${total_postage:.2f}"]
    #             data.append(formatted_row)
    #         else:
    #             i += 1

    #     return data, headers, skipped_lines
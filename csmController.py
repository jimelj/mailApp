import zipfile
import os
import math
import pandas as pd
from tabulate import tabulate
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView


# Path to the zip file and extraction folder
zip_file_path = os.path.expanduser('~/Downloads/MailDate 12-10-24_241205-104038.zip')  # Update with your path
extracted_folder = 'data/extracted'  # Update with your path

# Extract the zip file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extracted_folder)

# Find the CSM file in the extracted directory
maildat_folder = os.path.join(extracted_folder, 'MailDats')
csm_files = [file for file in os.listdir(maildat_folder) if file.endswith('.csm')]

# Check if we have a CSM file
if not csm_files:
    raise Exception("No CSM file found in the extracted data.")

# Read the CSM file (we assume it's the first one found)
csm_file_path = os.path.join(maildat_folder, csm_files[0])

# Define all fields based on the specification
fields_positions = [
    ("Job ID", 1, 8),
    ("Segment ID", 9, 12),
    ("Container Type", 13, 14),
    ("Container ID", 15, 20),
    ("Display Container ID", 21, 26),
    ("Container Destination Zip", 36, 41),
    ("Container Level", 42, 43),
    ("Entry Point - Postal Code", 44, 49),
    ("Entry Point - Facility Type", 50, 51),
    ("Entry Point - Actual/Delivery Locale Key", 52, 60),
    ("Entry Point - Actual Postal Code", 61, 69),
    ("Parent Container Reference ID", 70, 75),
    ("Truck or Dispatch Number", 76, 95),
    ("Stop Designator", 96, 97),
    ("Reservation Number", 98, 112),
    ("Actual Container Ship Date", 113, 120),
    ("Actual Container Ship Time", 121, 125),
    ("Scheduled Pick Up Date", 126, 133),
    ("Scheduled Pick Up Time", 134, 138),
    ("Scheduled In-Home Date", 139, 146),
    ("Additional In-Home Range", 147, 147),
    ("Scheduled Induction Start Date", 148, 155),
    ("Scheduled Induction Start Time", 156, 160),
    ("Scheduled Induction End Date", 161, 168),
    ("Scheduled Induction End Time", 169, 173),
    ("Actual Induction Date", 174, 181),
    ("Actual Induction Time", 182, 186),
    ("Postage Statement Mailing Date", 187, 194),
    ("Postage Statement Mailing Time", 195, 199),
    ("Number of Copies", 200, 207),
    ("Number of Pieces", 208, 215),
    ("Total Weight", 216, 227),
    ("Container Status", 240, 240),
    ("Included in Other Documentation", 241, 241),
    ("Tray Preparation Type", 242, 242),
    ("Trans-Ship Bill of Lading Number", 243, 252),
    ("Sibling Container Indicator", 253, 253),
    ("Sibling Container Reference ID", 254, 259),
    ("Postage Grouping ID", 260, 267),
    ("Container Gross Weight", 268, 279),
    ("Container Height", 280, 282),
    ("EMD ASN Barcode", 283, 302),
    ("Transportation Carrier ID", 303, 317),
    ("FAST Content ID", 318, 326),
    ("FAST Scheduler ID", 327, 338),
    ("USPS Pick Up", 339, 339),
    ("CSA Separation ID", 340, 342),
    ("Scheduled Ship Date", 343, 350),
    ("Scheduled Ship Time", 351, 355),
    ("DMM Section Defining Container Preparation", 356, 367),
    ("Label: IM™ Container - Final", 368, 391),
    ("Label: IM™ Container - Original", 392, 415),
    ("Label: Destination Line 1", 416, 445),
    ("Label: Destination Line 2", 446, 475),
    ("Label: Contents - Line 1", 476, 505),
    ("Label: Contents - Line 2", 506, 525),
    ("Label: Entry Point Line", 526, 555),
    ("Label: User Information Line 1", 556, 595),
    ("Label: User Information Line 2", 596, 635),
    ("Label: Container Label CIN Code", 636, 639),
    ("eInduction Indicator", 660, 660),
    ("CSA Agreement ID", 661, 670),
    ("Presort Labeling List Effective Date", 671, 678),
    ("Last Used Labeling List Effective Date", 679, 686),
    ("Presort City-State Publication Date", 687, 694),
    ("Last Used City-State Publication Date", 695, 702),
    ("Presort Zone Chart Matrix Publication Date", 703, 710),
    ("Last Used Zone Chart Matrix Publication Date", 711, 718),
    ("Last Used Mail Direction Publication Date", 719, 726),
    ("Supplemental Physical Container ID", 727, 732),
    ("Accept Misshipped", 733, 733),
    ("Referenceable Mail Start Date", 734, 741),
    ("Referenceable Mail End Date", 742, 749),
    ("CSM Record Status", 750, 750),
    ("Reserve", 751, 789),
    ("Closing Character", 790, 790)
]

# Helper function to convert weight to pounds
def convert_weight(weight_field):
    if weight_field:
        # Convert to a floating-point number and round up to the nearest whole number
        return math.ceil(float(f"{weight_field[:-4]}.{weight_field[-4:]}"))
    return None

# Helper function to format dates
def format_date(date_field):
    try:
        if not date_field or len(date_field) != 8:
            return None  # Return None for empty or invalid date fields
        return datetime.strptime(date_field, "%Y%m%d").strftime("%m-%d-%Y")
    except ValueError:
        return None  # Handle any other parsing errors

# Parse all records from the CSM file
parsed_records = []
with open(csm_file_path, 'r') as file:
    for record in file.readlines():
        parsed_record = {field[0]: record[field[1]-1:field[2]].strip() for field in fields_positions if record[field[1]-1:field[2]].strip()}

     # Convert Total Weight to pounds
        if "Total Weight" in parsed_record:
            parsed_record["Total Weight"] = convert_weight(parsed_record["Total Weight"])
        
        # Format Scheduled Induction Start Date
        if "Scheduled Induction Start Date" in parsed_record:
            parsed_record["Scheduled Induction Start Date"] = format_date(parsed_record["Scheduled Induction Start Date"])
        
        # Ensure Number of Pieces is represented properly
        if "Number of Pieces" in parsed_record:
            parsed_record["Number of Pieces"] = int(parsed_record["Number of Pieces"]) if parsed_record["Number of Pieces"].isdigit() else None
        
       


        parsed_records.append(parsed_record)


# Create the full DataFrame
df_csm = pd.DataFrame(parsed_records)

# Save the full data to a CSV file
df_csm.to_csv('data/parsed_csm.csv', index=False)

# Display the full dataset in the terminal
print("\nFull Parsed Data (Terminal):")
print(tabulate(df_csm, headers='keys', tablefmt='pretty', showindex=False))

# Filtered fields for app visualization
app_display_fields = [
    "Job ID",
    "Display Container ID",
    "Container Destination Zip",
    "Label: Destination Line 1",
    "Scheduled Induction Start Date",
    "Number of Pieces",
    "Total Weight",
    "Label: IM™ Container - Final"
]

df_filtered = df_csm[app_display_fields]

# Display app-specific fields in the terminal
print("\nFiltered Data for App Display:")
print(tabulate(df_filtered, headers='keys', tablefmt='pretty', showindex=False))


from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
import pandas as pd


class CSMTab(QWidget):
    def __init__(self, df_filtered):
        super().__init__()
        self.df_filtered = df_filtered  # Use the provided DataFrame
        self.layout = QVBoxLayout(self)

        if self.df_filtered.empty:
            # Show message if no data is available
            self.layout.addWidget(QLabel("No CSM data available. Please process data first."))
        else:
            # Create table
            self.create_table()

    def create_table(self):
        """Create a table widget to display the DataFrame."""
        table = QTableWidget()
        table.setRowCount(len(self.df_filtered))
        table.setColumnCount(len(self.df_filtered.columns))
        table.setHorizontalHeaderLabels(self.df_filtered.columns)

        # Populate the table with data
        for row_idx, row in self.df_filtered.iterrows():
            for col_idx, value in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        # Explicitly resize columns based on content and header
        header = table.horizontalHeader()
        for col in range(len(self.df_filtered.columns)):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        # Add the table to the layout
        self.layout.addWidget(table)
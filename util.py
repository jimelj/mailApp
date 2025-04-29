import fitz
import pycurl
from io import BytesIO
import paramiko
import os
import shutil
from urllib.parse import quote
import re
import posixpath
import pandas as pd
from pathlib import Path
import logging
from tqdm import tqdm
import zipfile
from datetime import datetime

# def upload_to_ftps(file_path, host, username, password, remote_dir, port):
#     # port = int(port)
#     print(file_path)
#     """
#     Uploads a file to an FTPS server with progress feedback.

#     Args:
#         file_path (str): Path to the file to upload.
#         host (str): FTPS server hostname.
#         username (str): FTPS username.
#         password (str): FTPS password.
#         remote_dir (str): Directory on the server where the file will be uploaded.
#         port (int): FTPS port number (default: 990).
#     """
#     try:
#         # Validate file existence
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File not found: {file_path}")
        
#         # Encode the file name to handle special characters
#         remote_file_name = quote(os.path.basename(file_path))
#         # Encode the password for safe transmission
#         file_path = os.path.normpath(file_path)


#         file_size = os.path.getsize(file_path)

#         def progress(download_total, downloaded, upload_total, uploaded):
#             if upload_total > 0:  # Avoid division by zero
#                 percent_complete = int((uploaded / upload_total) * 100)
#                 print(f"Uploading... {percent_complete}% ({uploaded}/{upload_total} bytes)", end="\r")

#         # Construct the FTPS URL
#         ftps_url = f"ftps://{host}:{port}{remote_dir}/{remote_file_name}"
#         print(f"FTPS URL: {ftps_url}")        

#         # Prepare the cURL handle
#         c = pycurl.Curl()
#         c.setopt(c.URL, ftps_url)
#         c.setopt(c.USERPWD, f"{username}:{password}")
#         c.setopt(c.UPLOAD, 1)
#         c.setopt(c.SSL_VERIFYPEER, 0)
#         c.setopt(c.SSL_VERIFYHOST, 0)
#         c.setopt(c.READFUNCTION, open(file_path, "rb").read)
#         c.setopt(c.INFILESIZE, file_size)
#         c.setopt(c.NOPROGRESS, 0)  # Enable progress meter
#         c.setopt(c.XFERINFOFUNCTION, progress)  # Progress callback
#         # Explicit FTPS
#         c.setopt(c.FTP_SSL, pycurl.FTPSSL_ALL)
#         c.setopt(c.VERBOSE, True)

#         # Capture the response
#         response_buffer = BytesIO()
#         c.setopt(c.WRITEDATA, response_buffer)

#         print(f"Starting upload to {host}:{port}{remote_dir}...")
#         c.perform()  # Perform the upload

#         # Get the response code before closing the handle
#         response_code = c.getinfo(c.RESPONSE_CODE)
#         c.close()

#         # Check the response
#         if response_code == 226:  # 226 indicates successful upload
#             print("\nFile uploaded successfully.")
#             return "File uploaded successfully."
#         else:
#             raise Exception(f"Upload failed with response code: {response_code}")

#     except Exception as e:
#         print(f"\nError during FTPS upload: {e}")
#         return f"FTPS upload failed: {e}"
# 


def upload_to_ftps(file_path, host, username, password, remote_dir, port):
    try:
        # Validate file existence
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add host keys

        # Connect to the server
        print(f"Connecting to {host}:{port}...")
        ssh.connect(hostname=host, port=port, username=username, password=password)
        
        # Open SFTP session
        sftp = ssh.open_sftp()

        # # Normalize remote path
        # remote_path = os.path.join(remote_dir, os.path.basename(file_path))

        # Use POSIX-style path formatting
        remote_path = posixpath.join(remote_dir, os.path.basename(file_path))
        print(f"DEBUG: Uploading to remote path: '{remote_path}'")

        # Upload file
        print(f"Uploading {file_path} to {remote_path} on {host}...")
        sftp.put(file_path, remote_path)

        print("Upload successful!")
        sftp.close()
        ssh.close()
        return f"File {file_path} uploaded successfully to {remote_dir}"
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Error during SFTP upload: {e}")


import pycurl
from io import BytesIO
import os


def fetch_latest_ftp_files():
    """
    Fetch the latest 6 ZIP files from an FTPS server using PycURL.
    """
    ftp_host = os.getenv("HOSTNAME1")
    ftp_user = os.getenv("FTP_USERNAME1")
    ftp_pass = os.getenv("FTP_SECRET1")
    remote_dir = os.getenv("REMOTEDIR1")
    port = int(os.getenv("PORT1", 990))

    try:
        buffer = BytesIO()
        ftps_url = f"ftps://{ftp_host}:{port}{remote_dir}/"
        print(f"DEBUG: FTP URL: {ftps_url}")

        c = pycurl.Curl()
        c.setopt(c.URL, ftps_url)
        c.setopt(c.USERPWD, f"{ftp_user}:{ftp_pass}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.SSL_VERIFYPEER, 0)  # Disable peer verification for testing
        c.setopt(c.SSL_VERIFYHOST, 0)  # Disable host verification for testing
        c.setopt(c.FTP_SSL, pycurl.FTPSSL_ALL)  # Enable implicit FTPS
        c.setopt(c.FTP_USE_EPSV, 1)  # Enable passive mode
        c.setopt(c.VERBOSE, False)  # Enable verbose output for debugging
        c.setopt(c.CUSTOMREQUEST, "NLST")  # Use NLST to list file names

        c.perform()

        # Check the response code
        response_code = c.getinfo(c.RESPONSE_CODE)
        if response_code != 226:  # 226 is the success code for directory listing
            raise RuntimeError(f"Unexpected response code: {response_code}")

        c.close()

        # # Decode the response and parse file names
        # response = buffer.getvalue().decode("utf-8")
        # print(f"DEBUG: FTP Response:\n{response}")
        # files = response.splitlines()
        # print(f"DEBUG: Parsed files:\n{files}")
        # zip_files = [f.strip() for f in files if f.strip().lower().endswith(".zip")]
        # print(f"DEBUG: Filtered ZIP files:\n{zip_files}")
        # zip_files.sort(reverse=True)  # Sort to get the latest files first
        # print(f"DEBUG: Sorted ZIP files:\n{zip_files}")
        # print(f"DEBUG: Returning latest ZIP files:\n{zip_files[:6]}")
        # return zip_files[:6]  # Return the latest 6 ZIP files

        # def parse_date_from_filename(filename):
        #     """Extract the date part from the filename."""
        #     match = re.search(r"\d{2}-\d{2}-\d{2}_\d{6}-\d{6}", filename)
        #     if match:
        #         # Convert the date portion into a sortable format
        #         return match.group(0)
        #     return None

        # # Decode the response and parse file names
        # response = buffer.getvalue().decode("utf-8")
        # print(f"DEBUG: FTP Response:\n{response}")

        # # Split the response into lines and filter ZIP files
        # files = response.splitlines()
        # print(f"DEBUG: Parsed files:\n{files}")

        # # Clean up filenames and filter for ZIP files
        # zip_files = [f.strip() for f in files if f.strip().lower().endswith(".zip")]
        # print(f"DEBUG: Filtered ZIP files:\n{zip_files}")

        # # Sort ZIP files by the extracted date
        # zip_files.sort(key=parse_date_from_filename, reverse=True)  # Sort by date in descending order
        # print(f"DEBUG: Sorted ZIP files:\n{zip_files}")

        # # Return the latest 6 ZIP files
        # latest_zip_files = zip_files[:6]
        # print(f"DEBUG: Returning latest ZIP files:\n{latest_zip_files}")
        # return latest_zip_files

        def parse_date_from_filename(filename):
            """Extract the date in the YYYYMMDD format (e.g., 250118) from the filename."""
            match = re.search(r"_\d{6}-", filename)
            if match:
                # Extract the 6-digit date (YYYYMMDD format) and return it
                return match.group(0).strip("_-")
            return None

        # Decode the response and parse file names
        response = buffer.getvalue().decode("utf-8")
        print(f"DEBUG: FTP Response:\n{response}")

        # Split the response into lines and filter ZIP files
        files = response.splitlines()
        print(f"DEBUG: Parsed files:\n{files}")

        # Clean up filenames and filter for ZIP files
        zip_files = [f.strip() for f in files if f.strip().lower().endswith(".zip")]
        print(f"DEBUG: Filtered ZIP files:\n{zip_files}")

        # Sort ZIP files by the extracted date
        zip_files.sort(key=parse_date_from_filename, reverse=True)  # Sort by date in descending order
        print(f"DEBUG: Sorted ZIP files:\n{zip_files}")

        # Return the latest 6 ZIP files
        latest_zip_files = zip_files[:8]
        print(f"DEBUG: Returning latest ZIP files:\n{latest_zip_files}")
        return latest_zip_files

    except pycurl.error as e:
        raise RuntimeError(f"Failed to fetch files from FTP: {e}")


def download_file_from_ftp(filename):
    """
    Download a specific ZIP file from the FTPS server using PycURL.

    Args:
        filename (str): The name of the file to download.

    Returns:
        str: The local path to the downloaded file.
    """
    ftp_host = os.getenv("HOSTNAME1")
    ftp_user = os.getenv("FTP_USERNAME1")
    ftp_pass = os.getenv("FTP_SECRET1")
    remote_dir = os.getenv("REMOTEDIR1").rstrip("/")  # Remove trailing slash if present
    port = os.getenv("PORT1", 990)
    local_dir = "data"

    try:
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        # Encode the file name to handle special characters
        encoded_filename = quote(filename)
        ftps_url = f"ftps://{ftp_host}:{port}{remote_dir}/{encoded_filename}"
        print(f"DEBUG: FTP URL for download: {ftps_url}")

        with open(local_path, "wb") as f:
            c = pycurl.Curl()
            c.setopt(c.URL, ftps_url)
            c.setopt(c.USERPWD, f"{ftp_user}:{ftp_pass}")
            c.setopt(c.WRITEDATA, f)
            c.setopt(c.SSL_VERIFYPEER, 0)  # Disable peer verification for testing
            c.setopt(c.SSL_VERIFYHOST, 0)  # Disable host verification for testing
            c.setopt(c.FTP_SSL, pycurl.FTPSSL_ALL)  # Enable implicit FTPS
            c.setopt(c.FTP_USE_EPSV, 1)  # Enable passive mode
            c.setopt(c.VERBOSE, True)  # Enable verbose output for debugging

            c.perform()

            # Check the response code
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code not in (226, 250):  # 226 and 250 indicate successful transfers
                raise RuntimeError(f"Unexpected response code: {response_code}")

            c.close()

        print(f"DEBUG: File downloaded successfully to {local_path}")
        return local_path

    except pycurl.error as e:
        raise RuntimeError(f"Failed to download file {filename} from FTP: {e}")
# def upload_to_sftp(file_path, sftp_host, sftp_user, sftp_password, remote_dir="/"):
#     """
#     Uploads a file to an SFTP server.

#     Parameters:
#         file_path (str): Path to the file to be uploaded.
#         sftp_host (str): SFTP server hostname or IP address.
#         sftp_user (str): SFTP username.
#         sftp_password (str): SFTP password.
#         remote_dir (str): Directory on the SFTP server where the file will be uploaded. Defaults to root.
#     """
#     try:
#         # Connect to the SFTP server
#         transport = paramiko.Transport((sftp_host, 22))  # Default SFTP port is 22
#         transport.connect(username=sftp_user, password=sftp_password)
#         sftp = paramiko.SFTPClient.from_transport(transport)
#         print(f"Connected to SFTP server: {sftp_host}")

#         # Change to the remote directory
#         if remote_dir and remote_dir != "/":
#             sftp.chdir(remote_dir)
#             print(f"Changed directory to: {remote_dir}")

#         # Upload the file
#         remote_file_path = f"{remote_dir}/{os.path.basename(file_path)}"
#         sftp.put(file_path, remote_file_path)
#         print(f"Uploaded file: {file_path} to {remote_file_path}")

#         # Close the SFTP connection
#         sftp.close()
#         transport.close()
#         print("SFTP connection closed.")

#     except Exception as e:
#         print(f"Error uploading file to SFTP: {e}")

# def process_zip_name(zip_name):
#     """
#     Extracts the relevant part of the ZIP file name by removing 'MailDate'.
    
#     Args:
#         zip_name (str): The name of the uploaded ZIP file.

#     Returns:
#         str: The processed file name without 'MailDate'.
#     """
#     if zip_name.startswith("MailDate " or "maildate "):
#         return zip_name.replace("MailDate ", "", 1).strip()
#     return zip_name.strip()

def process_zip_name(zip_name):
    """
    Extracts the relevant part of the ZIP file name by removing 'MailDate' (case-insensitive).

    Args:
        zip_name (str): The name of the uploaded ZIP file.

    Returns:
        str: The processed file name without 'MailDate'.
    """
    # Normalize to lowercase for case-insensitive comparison
    if zip_name.lower().startswith("maildate "):
        return zip_name[9:].strip()  # Remove 'MailDate ' (9 characters)
    return zip_name.strip()

def clean_backend_files():
    """Delete all backend files and folders to reset the application state."""
    paths_to_clean = [
        "data/extracted",         # Folder where ZIP files are extracted
        "data/parsed_csm.csv",    # Parsed CSM data
    ]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    os.remove(path)  # Remove file
                    print(f"Deleted file: {path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)  # Remove directory
                    print(f"Deleted directory: {path}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")
        else:
            print(f"Path does not exist: {path}")

    


import logging



logging.basicConfig(level=logging.DEBUG)

from datetime import datetime


def close_and_remove_pdf(file_path):
    """Ensure the PDF file is closed before deletion."""
    try:
        if os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
            with fitz.open(file_path) as doc:  # Use context manager to ensure proper closure
                logging.debug(f"Closed PDF file: {file_path}")
    except Exception as e:
        logging.error(f"Error closing or handling PDF {file_path}: {e}")


def move_and_rename_locked_file(file_path, locked_files_dir):
    """Move and rename a locked file to the locked_files directory."""
    os.makedirs(locked_files_dir, exist_ok=True)  # Ensure the locked files directory exists
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp
    new_name = f"{os.path.basename(file_path)}_{timestamp}"  # Append timestamp to file name
    temp_path = os.path.join(locked_files_dir, new_name)
    try:
        shutil.move(file_path, temp_path)
        logging.debug(f"Moved and renamed locked file to: {temp_path}")
    except Exception as e:
        logging.error(f"Failed to move and rename locked file {file_path}: {e}")





def clean_backend_files_with_move(directory):
    """Cleans all files and subdirectories in a directory, moving and renaming locked files."""
    locked_files_dir = os.path.join("data", "locked_files")  # Define the directory for locked files

    if os.path.exists(directory):
        logging.debug(f"Starting cleanup of directory: {directory}")
        
        for root, dirs, files in os.walk(directory, topdown=False):  # Bottom-up traversal
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # If it's a PDF, ensure it's closed
                    if file.lower().endswith(".pdf"):
                        close_and_remove_pdf(file_path)

                    os.unlink(file_path)  # Attempt to delete the file
                    logging.debug(f"Deleted file: {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete file {file_path}: {e}")
                    move_and_rename_locked_file(file_path, locked_files_dir)  # Move and rename locked file

            for dir_ in dirs:
                dir_path = os.path.join(root, dir_)
                try:
                    os.rmdir(dir_path)  # Attempt to remove the directory
                    logging.debug(f"Deleted directory: {dir_path}")
                except Exception as e:
                    logging.error(f"Failed to delete directory {dir_path}: {e}")

        try:
            os.rmdir(directory)  # Finally, remove the root directory
            logging.debug(f"Deleted root directory: {directory}")
        except Exception as e:
            logging.error(f"Failed to delete root directory {directory}: {e}")

        # Inform the user about moved and renamed locked files
        if os.path.exists(locked_files_dir) and os.listdir(locked_files_dir):
            logging.warning(f"Locked files moved to: {locked_files_dir}")
    else:
        logging.warning(f"Directory {directory} does not exist.")

class DDUSCFSearch:
    def __init__(self, zips_file_path):
        """
        Initialize the search utility with the path to the ZIP data file.
        :param zips_file_path: Path to the Excel file containing ZIP data.
        """
        self.zips_file_path = Path(zips_file_path)

    def load_zips_data(self, sheet_name="Data"):
        """
        Load ZIP data from the Excel file.
        :param sheet_name: The name of the sheet in the Excel file to load.
        :return: A pandas DataFrame containing the ZIP data.
        """
        try:
            zips_df = pd.read_excel(self.zips_file_path, sheet_name=sheet_name)
            zips_df["zip"] = zips_df["zip"].astype(str)
            return zips_df
        except Exception as e:
            print(f"Error loading ZIP data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error

    def merge_zip_data(self, main_df, column_to_merge_on="Container Destination Zip", zips_sheet_name="Data"):
        """
        Merge the main DataFrame with ZIP data from the Excel file.
        :param main_df: The main DataFrame to merge.
        :param column_to_merge_on: Column in the main DataFrame to merge on.
        :param zips_sheet_name: Sheet name to load ZIP data from.
        :return: A merged pandas DataFrame.
        """
        try:
            # Load the ZIP data
            zips_df = self.load_zips_data(sheet_name=zips_sheet_name)

            # Ensure proper data types
            main_df[column_to_merge_on] = main_df[column_to_merge_on].astype(str)

            # Perform the merge
            merged_df = pd.merge(
                main_df,
                zips_df[["zip", "truckload", "ratedesc"]],
                left_on=column_to_merge_on,
                right_on="zip",
                how="left"
            )

            return merged_df
        except Exception as e:
            print(f"Error merging ZIP data: {e}")
            return main_df  # Return the original DataFrame if merge fails

# Add function to fetch backup files from the Backup folder
def fetch_backup_ftp_files():
    """
    Fetch ZIP files from the backup folder on the FTPS server.
    """
    ftp_host = os.getenv("HOSTNAME1")
    ftp_user = os.getenv("FTP_USERNAME1")
    ftp_pass = os.getenv("FTP_SECRET1")
    # Use posixpath.join for FTP paths
    base_remote_dir = os.getenv("REMOTEDIR1", "/").rstrip("/")
    remote_backup_dir = posixpath.join(base_remote_dir, "Backup")
    port = int(os.getenv("PORT1", 990))

    try:
        buffer = BytesIO()
        # Ensure the URL ends with a slash for directory listing
        ftps_url = f"ftps://{ftp_host}:{port}{remote_backup_dir}/"
        print(f"DEBUG: Backup FTP URL: {ftps_url}")

        c = pycurl.Curl()
        c.setopt(c.URL, ftps_url)
        c.setopt(c.USERPWD, f"{ftp_user}:{ftp_pass}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.SSL_VERIFYPEER, 0)
        c.setopt(c.SSL_VERIFYHOST, 0)
        c.setopt(c.FTP_SSL, pycurl.FTPSSL_ALL)
        c.setopt(c.FTP_USE_EPSV, 1)
        c.setopt(c.VERBOSE, False)
        c.setopt(c.CUSTOMREQUEST, "NLST")

        c.perform()

        # Check the response code
        response_code = c.getinfo(c.RESPONSE_CODE)
        if response_code != 226:
            raise RuntimeError(f"Unexpected response code: {response_code}")

        c.close()

        def parse_date_from_filename(filename):
            """Extract the date in the YYYYMMDD format from the filename."""
            match = re.search(r"_\d{6}-", filename)
            if match:
                return match.group(0).strip("_-")
            return None

        # Decode the response and parse file names
        response = buffer.getvalue().decode("utf-8")
        print(f"DEBUG: Backup FTP Response:\n{response}")

        # Split the response into lines and filter ZIP files
        files = response.splitlines()
        
        # Clean up filenames and filter for ZIP files
        zip_files = [f.strip() for f in files if f.strip().lower().endswith(".zip")]
        print(f"DEBUG: Filtered Backup ZIP files:\n{zip_files}")

        # Sort ZIP files by the extracted date
        zip_files.sort(key=parse_date_from_filename, reverse=True)
        
        # Return all backup ZIP files
        return zip_files

    except pycurl.error as e:
        raise RuntimeError(f"Failed to fetch backup files from FTP: {e}")

# Add function to download a file from the backup folder
def download_file_from_backup_ftp(filename):
    """
    Download a specific ZIP file from the backup folder on the FTPS server.

    Args:
        filename (str): The name of the file to download.

    Returns:
        str: The local path to the downloaded file.
    """
    ftp_host = os.getenv("HOSTNAME1")
    ftp_user = os.getenv("FTP_USERNAME1")
    ftp_pass = os.getenv("FTP_SECRET1")
    # Use posixpath.join for FTP paths
    base_remote_dir = os.getenv("REMOTEDIR1", "/").rstrip("/")
    remote_backup_dir = posixpath.join(base_remote_dir, "Backup")
    port = os.getenv("PORT1", 990)
    local_dir = "data"

    try:
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        # Encode the file name to handle special characters
        encoded_filename = quote(filename)
        # Construct the full file path using posixpath.join
        remote_file_path = posixpath.join(remote_backup_dir, encoded_filename)
        ftps_url = f"ftps://{ftp_host}:{port}{remote_file_path}"
        print(f"DEBUG: Backup FTP URL for download: {ftps_url}")

        with open(local_path, "wb") as f:
            c = pycurl.Curl()
            c.setopt(c.URL, ftps_url)
            c.setopt(c.USERPWD, f"{ftp_user}:{ftp_pass}")
            c.setopt(c.WRITEDATA, f)
            c.setopt(c.SSL_VERIFYPEER, 0)
            c.setopt(c.SSL_VERIFYHOST, 0)
            c.setopt(c.FTP_SSL, pycurl.FTPSSL_ALL)
            c.setopt(c.FTP_USE_EPSV, 1)
            c.setopt(c.VERBOSE, True)

            c.perform()

            # Check the response code
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code not in (226, 250):
                raise RuntimeError(f"Unexpected response code: {response_code}")

            c.close()

        print(f"DEBUG: Backup file downloaded successfully to {local_path}")
        return local_path

    except pycurl.error as e:
        raise RuntimeError(f"Failed to download backup file {filename} from FTP: {e}")

# Add function to download and process all ZIP files
def download_and_process_all_files(callback_fn=None):
    """
    Downloads and processes all available ZIP files from the FTP server.
    Returns a tuple containing:
    - combined_df: The merged DataFrame containing all processed data
    - processed_zip_files: List of processed ZIP file paths
    - report_file_paths: List of processed report file paths
    - error_messages: List of any error messages encountered
    - merged_pdfs: Dictionary of merged PDF file paths
    """
    print("DEBUG: Starting download_and_process_all_files")
    zip_files = fetch_latest_ftp_files()
    print(f"DEBUG: Found {len(zip_files)} ZIP files to process")
    
    all_dataframes = []
    all_zip_file_paths = []
    all_report_file_paths = []
    error_messages = []
    skid_tags_pdfs = []
    tray_tags_pdfs = []
    
    # Create temporary directories for PDFs and reports
    temp_pdf_dir = "data/temp_pdfs"
    temp_report_dir = "data/temp_reports"
    os.makedirs(temp_pdf_dir, exist_ok=True)
    os.makedirs(temp_report_dir, exist_ok=True)
    
    # Process each ZIP file
    for i, zip_file in enumerate(zip_files):
        print(f"DEBUG: Processing file {i+1}/{len(zip_files)}: {zip_file}")
        if callback_fn:
            callback_fn(f"Processing file {i+1} of {len(zip_files)}: {zip_file}", (i / len(zip_files)) * 100)
            
        try:
            # Download the ZIP file
            local_file_path = download_file_from_ftp(zip_file)
            all_zip_file_paths.append(local_file_path)
            
            # Extract and process the ZIP file
            from csmController import parse_zip_and_prepare_data
            # Get the unique extraction path used by parse_zip_and_prepare_data
            zip_name = os.path.basename(local_file_path)
            unique_extracted_folder = os.path.join("data", "extracted", f"extract_{zip_name}")
            
            # Now call parse_zip_and_prepare_data which extracts to the unique folder
            df = parse_zip_and_prepare_data(local_file_path)

            print(f"DEBUG: Processed DataFrame shape: {df.shape}")
            print(f"DEBUG: DataFrame columns: {df.columns.tolist()}")
            
            # Add the source file name to identify the data source
            df['Source_ZIP'] = zip_file
            
            # Add DataFrame to the list
            all_dataframes.append(df)
            print(f"DEBUG: Added DataFrame to list. Total DataFrames: {len(all_dataframes)}")
            
            # Check for SkidTags.pdf, TrayTags.pdf, and RptList.txt in the unique extracted path
            reports_subpath = os.path.join(unique_extracted_folder, "Reports") # Use the unique path
            zip_name_base = os.path.splitext(zip_file)[0]
            
            # Copy SkidTags.pdf to temp directory with unique name
            skid_tags_path = os.path.join(reports_subpath, "SkidTags.pdf")
            if os.path.exists(skid_tags_path):
                temp_skid_path = os.path.join(temp_pdf_dir, f"SkidTags_{zip_name_base}.pdf")
                shutil.copy2(skid_tags_path, temp_skid_path)
                skid_tags_pdfs.append(temp_skid_path)
            
            # Copy TrayTags.pdf to temp directory with unique name
            tray_tags_path = os.path.join(reports_subpath, "TrayTags.pdf")
            if os.path.exists(tray_tags_path):
                temp_tray_path = os.path.join(temp_pdf_dir, f"TrayTags_{zip_name_base}.pdf")
                shutil.copy2(tray_tags_path, temp_tray_path)
                tray_tags_pdfs.append(temp_tray_path)

            # Copy RptList.txt to temp directory with unique name
            report_list_path = os.path.join(reports_subpath, "RptList.txt")
            if os.path.exists(report_list_path):
                temp_report_path = os.path.join(temp_report_dir, f"RptList_{zip_name_base}.txt")
                shutil.copy2(report_list_path, temp_report_path)
                all_report_file_paths.append(temp_report_path)
            
            if callback_fn:
                callback_fn(f"Successfully processed {zip_file}", ((i + 0.5) / len(zip_files)) * 100)
                
        except Exception as e:
            error_msg = f"Error processing {zip_file}: {str(e)}"
            error_messages.append(error_msg)
            print(f"ERROR: {error_msg}")
            if callback_fn:
                callback_fn(error_msg, ((i + 0.5) / len(zip_files)) * 100)
    
    # Merge PDF files
    merged_pdfs = {}
    if callback_fn: callback_fn("Merging PDF files...", 95)
    
    # Define final merged PDF paths within a dedicated directory
    final_merged_dir = "data/merged_reports"
    os.makedirs(final_merged_dir, exist_ok=True)
    
    if skid_tags_pdfs:
        merged_skid_path = os.path.join(final_merged_dir, "SkidTags_Merged.pdf")
        if merge_pdf_files(skid_tags_pdfs, merged_skid_path):
            merged_pdfs["SkidTags"] = merged_skid_path
    
    if tray_tags_pdfs:
        merged_tray_path = os.path.join(final_merged_dir, "TrayTags_Merged.pdf")
        if merge_pdf_files(tray_tags_pdfs, merged_tray_path):
            merged_pdfs["TrayTags"] = merged_tray_path
    
    # Combine all DataFrames if we have any
    if all_dataframes:
        print("DEBUG: Starting DataFrame concatenation")
        print(f"DEBUG: Number of DataFrames to merge: {len(all_dataframes)}")
        for i, df in enumerate(all_dataframes):
            print(f"DEBUG: DataFrame {i+1} shape: {df.shape}")
            print(f"DEBUG: DataFrame {i+1} columns: {df.columns.tolist()}")
        
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"DEBUG: Combined DataFrame shape: {combined_df.shape}")
        print(f"DEBUG: Combined DataFrame columns: {combined_df.columns.tolist()}")
        print(f"DEBUG: Number of unique Source_ZIP values: {combined_df['Source_ZIP'].nunique()}")
        
        if callback_fn: callback_fn("All files processed and combined", 100)
        return combined_df, all_zip_file_paths, all_report_file_paths, error_messages, merged_pdfs
    else:
        print("DEBUG: No DataFrames to combine")
        return pd.DataFrame(), all_zip_file_paths, all_report_file_paths, error_messages, merged_pdfs


# Add function to merge DataFrames from multiple CSM files
def merge_csm_dataframes(dataframes):
    """
    Merge multiple CSM DataFrames into a single DataFrame.
    
    Args:
        dataframes (list): List of DataFrames to merge
        
    Returns:
        DataFrame: The merged DataFrame
    """
    if not dataframes:
        return pd.DataFrame()
    
    # Combine all DataFrames, removing duplicates based on container ID
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Remove duplicates based on container ID if it exists
    if 'Container ID' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset='Container ID')
    
    return combined_df

# Add a function to merge multiple PDF files
def merge_pdf_files(pdf_paths, output_path):
    """
    Merge multiple PDF files into a single PDF file.
    
    Args:
        pdf_paths (list): List of paths to PDF files to merge
        output_path (str): Path to save the merged PDF file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not pdf_paths:
            logging.warning("No PDF files to merge")
            return False
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create a new PDF document
        merged_pdf = fitz.open()
        
        # Track page hashes to detect duplicates
        page_hashes = set()
        duplicate_count = 0
        
        # Add each PDF file to the merged document
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                try:
                    pdf_document = fitz.open(pdf_path)
                    
                    # Detect "TrayTags" in the filename - special handling for duplicates
                    is_tray_tags = "TrayTags" in os.path.basename(pdf_path)
                    
                    # Process each page
                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        
                        # For tray tags, create a hash of the page content to detect duplicates
                        if is_tray_tags:
                            # Extract text as a simple way to compare content
                            page_text = page.get_text()
                            # Create a hash of the text content
                            page_hash = hash(page_text)
                            
                            # Skip if this page content already exists
                            if page_hash in page_hashes:
                                duplicate_count += 1
                                print(f"Skipping duplicate page {page_num+1} in {pdf_path}")
                                continue
                                
                            # Add this page's hash to the set
                            page_hashes.add(page_hash)
                        
                        # Insert the page to the merged document
                        merged_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                    
                    pdf_document.close()
                    logging.info(f"Added {pdf_path} to merged PDF")
                except Exception as e:
                    logging.error(f"Error adding {pdf_path} to merged PDF: {e}")
        
        # Save the merged PDF
        if merged_pdf.page_count > 0:
            merged_pdf.save(output_path)
            if duplicate_count > 0:
                logging.info(f"Removed {duplicate_count} duplicate pages from the merged PDF")
            merged_pdf.close()
            logging.info(f"Merged PDF saved to {output_path}")
            return True
        else:
            logging.warning("No pages were added to the merged PDF")
            merged_pdf.close()
            return False
            
    except Exception as e:
        logging.error(f"Error merging PDF files: {e}")
        return False

# Function to process a single RptList.txt file
def process_single_rptlist(file_path):
    """
    Processes a single RptList.txt file and returns structured data and totals.
    
    Returns:
        tuple: (data_rows, report_totals, headers, skipped_lines)
               - data_rows: List of processed data rows (DDU/SCF)
               - report_totals: Dictionary containing 'copies', 'weight', 'postage'
               - headers: List of column headers
               - skipped_lines: List of lines that were skipped during processing
    """
    data_rows = []
    headers = ["Entry Point Name", "Drop Site Key", "Total Copies", "Total Weight", "Total Postage", "CPM", "AVR Piece Weight"]
    skipped_lines = []
    report_totals = {'copies': 0, 'weight': 0.0, 'postage': 0.0}

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return [], report_totals, headers, [f"File not found: {file_path}"]
    except Exception as e:
        return [], report_totals, headers, [f"Error opening file {file_path}: {e}"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip irrelevant lines
        if not line or line.startswith(("", "Summary", "Page", "CBA", "-------")):
            i += 1
            continue

        # Process the totals row
        if line.startswith("Report Totals:"):
            parts = line.split(":", 1)
            if len(parts) < 2:
                skipped_lines.append(f"Malformed totals line: {line}")
                i += 1
                continue
            totals_line = parts[1].strip()
            tokens = totals_line.split()
            tokens = [t for t in tokens if t != "$"] # Filter out stray '$'
            if len(tokens) < 12:
                skipped_lines.append(f"Insufficient tokens in totals line: {line}")
                i += 1
                continue
            try:
                report_totals['copies'] = int(float(tokens[9]))
                report_totals['weight'] = float(tokens[10])
                report_totals['postage'] = float(tokens[11])
            except ValueError as e:
                skipped_lines.append(f"Error converting totals tokens in line: {line} | {e}")
            i += 1 # Move past the totals line
            continue # Totals are extracted, move to next line

        # Process regular data lines (DDU/SCF)
        if line.startswith("DDU-") or line.startswith("SCF-"):
            parts = line.split()
            name_tokens = []
            numeric_start_index = None
            for idx, token in enumerate(parts):
                if token == "$": continue
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

            # Calculate CPM and AVR Piece Weight
            cpm = (total_postage / total_copies) * 1000 if total_copies != 0 else 0
            piece_weight = (total_weight / total_copies) * 16 if total_copies != 0 else 0 # Assuming weight is in lbs, convert to oz

            # Look ahead for the drop site key
            drop_site_key = None
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith("-------"):
                    if next_line.startswith("Drop Site Key:"):
                        drop_site_key = next_line.split(":", 1)[1].strip()
                    break # Found relevant next line or key
                j += 1
            i = j + 1 # Move main loop index past the key line

            formatted_row = [
                entry_point_name,
                drop_site_key,
                total_copies,
                total_weight,
                f"${total_postage:.2f}",
                f"${cpm:.2f}",
                f"{piece_weight:.2f} oz" # Add unit for clarity
            ]
            data_rows.append(formatted_row)
        else:
            i += 1 # Move to the next line if it's not DDU/SCF/Total

    return data_rows, report_totals, headers, skipped_lines

# Function to process multiple RptList.txt files for batch mode
def process_batch_rptlist(report_paths):
    """
    Processes multiple RptList.txt files, combines the data, and calculates grand totals.
    
    Args:
        report_paths (list): List of paths to RptList.txt files.
        
    Returns:
        tuple: (combined_data, headers, all_skipped_lines)
               - combined_data: List of all data rows plus a calculated grand total row.
               - headers: List of column headers.
               - all_skipped_lines: List of all skipped lines from all files.
    """
    combined_data_rows = []
    grand_total_copies = 0
    grand_total_weight = 0.0
    grand_total_postage = 0.0
    all_skipped_lines = []
    headers = []

    if not report_paths:
        return [], ["Entry Point Name", "Drop Site Key", "Total Copies", "Total Weight", "Total Postage", "CPM", "AVR Piece Weight"], ["No report files provided for batch processing."]

    for report_path in report_paths:
        data_rows, report_totals, current_headers, skipped_lines = process_single_rptlist(report_path)
        
        combined_data_rows.extend(data_rows)
        grand_total_copies += report_totals['copies']
        grand_total_weight += report_totals['weight']
        grand_total_postage += report_totals['postage']
        all_skipped_lines.extend(skipped_lines)
        
        if not headers: # Capture headers from the first processed file
            headers = current_headers

    # Calculate grand total CPM and Average Piece Weight
    grand_cpm = (grand_total_postage / grand_total_copies) * 1000 if grand_total_copies != 0 else 0
    grand_piece_weight = (grand_total_weight / grand_total_copies) * 16 if grand_total_copies != 0 else 0

    # Create the grand total row
    grand_total_row = [
        "Grand Totals:",
        "",
        grand_total_copies,
        grand_total_weight,
        f"${grand_total_postage:.2f}",
        f"${grand_cpm:.2f}",
        f"{grand_piece_weight:.2f} oz"
    ]
    
    combined_data_rows.append(grand_total_row)

    return combined_data_rows, headers, all_skipped_lines

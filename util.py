import fitz
import pycurl
from io import BytesIO
import paramiko
import os
import shutil
from urllib.parse import quote

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

        # Normalize remote path
        remote_path = os.path.join(remote_dir, os.path.basename(file_path))

        # Upload file
        print(f"Uploading {file_path} to {remote_path} on {host}...")
        sftp.put(file_path, remote_path)

        print("Upload successful!")
        sftp.close()
        ssh.close()

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
        c.setopt(c.VERBOSE, True)  # Enable verbose output for debugging
        c.setopt(c.CUSTOMREQUEST, "NLST")  # Use NLST to list file names

        c.perform()

        # Check the response code
        response_code = c.getinfo(c.RESPONSE_CODE)
        if response_code != 226:  # 226 is the success code for directory listing
            raise RuntimeError(f"Unexpected response code: {response_code}")

        c.close()

        # Decode the response and parse file names
        response = buffer.getvalue().decode("utf-8")
        print(f"DEBUG: FTP Response:\n{response}")
        files = response.splitlines()
        zip_files = [f for f in files if f.lower().endswith(".zip")]
        zip_files.sort(reverse=True)  # Sort to get the latest files first
        return zip_files[:6]  # Return the latest 6 ZIP files

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
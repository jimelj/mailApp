import pycurl
from io import BytesIO
import os

def upload_to_ftps(file_path, host, username, password, remote_dir="/", port=990):
    """
    Uploads a file to an FTPS server with progress feedback.

    Args:
        file_path (str): Path to the file to upload.
        host (str): FTPS server hostname.
        username (str): FTPS username.
        password (str): FTPS password.
        remote_dir (str): Directory on the server where the file will be uploaded.
        port (int): FTPS port number (default: 990).
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)

        def progress(download_total, downloaded, upload_total, uploaded):
            if upload_total > 0:  # Avoid division by zero
                percent_complete = int((uploaded / upload_total) * 100)
                print(f"Uploading... {percent_complete}% ({uploaded}/{upload_total} bytes)", end="\r")

        # Prepare the cURL handle
        c = pycurl.Curl()
        c.setopt(c.URL, f"ftps://{host}:{port}{remote_dir}/{os.path.basename(file_path)}")
        c.setopt(c.USERPWD, f"{username}:{password}")
        c.setopt(c.UPLOAD, 1)
        c.setopt(c.SSL_VERIFYPEER, 0)
        c.setopt(c.SSL_VERIFYHOST, 0)
        c.setopt(c.READFUNCTION, open(file_path, "rb").read)
        c.setopt(c.INFILESIZE, file_size)
        c.setopt(c.NOPROGRESS, 0)  # Enable progress meter
        c.setopt(c.XFERINFOFUNCTION, progress)  # Progress callback

        # Capture the response
        response_buffer = BytesIO()
        c.setopt(c.WRITEDATA, response_buffer)

        print(f"Starting upload to {host}:{port}{remote_dir}...")
        c.perform()  # Perform the upload

        # Get the response code before closing the handle
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        # Check the response
        if response_code == 226:  # 226 indicates successful upload
            print("\nFile uploaded successfully.")
            return "File uploaded successfully."
        else:
            raise Exception(f"Upload failed with response code: {response_code}")

    except Exception as e:
        print(f"\nError during FTPS upload: {e}")
        return f"FTPS upload failed: {e}"


#         # import paramiko

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
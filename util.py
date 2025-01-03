import pycurl
from io import BytesIO

def upload_to_ftps(file_path, host, username, password, remote_dir="/", port=990):
    """
    Upload a file to an FTPS server using pycurl.

    Parameters:
    - file_path (str): Local path to the file to upload.
    - host (str): FTPS server hostname.
    - username (str): FTPS username.
    - password (str): FTPS password.
    - remote_dir (str): Remote directory path.
    - port (int): Port number (default: 990).
    """
    try:
        file_name = file_path.split("/")[-1]
        ftps_url = f"ftps://{host}:{port}{remote_dir}/{file_name}"
        print(f"Uploading to: {ftps_url}")

        with open(file_path, "rb") as f:
            c = pycurl.Curl()
            c.setopt(c.URL, ftps_url)
            c.setopt(c.USERPWD, f"{username}:{password}")
            c.setopt(c.UPLOAD, 1)
            c.setopt(c.READFUNCTION, f.read)
            c.setopt(c.SSL_VERIFYHOST, 0)  # Disable SSL hostname verification
            c.setopt(c.SSL_VERIFYPEER, 0)  # Disable SSL peer verification
            c.perform()
            c.close()

        print("FTPS upload successful.")
        return "File uploaded successfully."

    except pycurl.error as e:
        print(f"FTPS upload failed: {e}")
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
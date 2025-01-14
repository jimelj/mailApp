import requests
from PySide6.QtWidgets import QMessageBox
import os
import platform


class UpdateApp:
    def __init__(self, current_version):
        self.current_version = current_version
        print("Current version:", self.current_version)

    def fetch_latest_version_info(self):
        url = "https://raw.githubusercontent.com/jimelj/mailApp/main/latest_version.json"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            # print("the repsonse")
            # print(response.json())
            return response.json()
        
        except requests.RequestException as e:
            print(f"Failed to fetch version info: {e}")
            return None

    def check_for_updates(self):
        latest_version_info = self.fetch_latest_version_info()
        if not latest_version_info:
            return  # Failed to fetch updates

        latest_version = latest_version_info["version"]

        print(f"DEBUG: Current Version: {self.current_version}, Latest Version: {latest_version}")


        if latest_version > self.current_version:
            self.notify_update(latest_version_info)
        else:
            print("You are using the latest version.")

    # def notify_update(self, latest_version_info):
    #     changelog = latest_version_info.get("changelog", "No details provided.")
    #     download_url = latest_version_info["download_url"].get(platform.system().lower())
        
    #     msg_box = QMessageBox()
    #     msg_box.setWindowTitle("Update Available")
    #     msg_box.setText(f"A new version {latest_version_info['version']} is available!")
    #     msg_box.setInformativeText(f"Changelog:\n{changelog}")
    #     msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #     if msg_box.exec() == QMessageBox.Ok:
    #         self.download_update(download_url)

    def notify_update(self, latest_version_info):
        print(f"DEBUG: Update available. Info: {latest_version_info}")
        changelog = latest_version_info.get("changelog", "No details provided.")
        print(f"DEBUG: Current Platform: {platform.system().lower()}")
        download_url = latest_version_info["download_url"].get(platform.system().lower())
        
        if not download_url:
            print(f"DEBUG: No download URL for this platform.")
            return

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Update Available")
        msg_box.setText(f"A new version {latest_version_info['version']} is available!")
        msg_box.setInformativeText(f"Changelog:\n{changelog}")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if msg_box.exec() == QMessageBox.Ok:
            self.download_update(download_url)

    def download_update(self, url):
        filename = os.path.basename(url)
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded update to: {filename}")
            print(f"Downloading from {url} to {filename}")
            self.install_update(filename)
        except Exception as e:
            print(f"Failed to download update: {e}")

    def install_update(self, filename):
        if platform.system() == "Windows":
            os.startfile(filename)  # Launch installer
        elif platform.system() == "Darwin":
            os.system(f"open {filename}")  # Open DMG file
        else:
            print("Installer not supported for this OS.")
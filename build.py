

# # Get version from Git or fallback to VERSION file
# version=$(git describe --tags --abbrev=0 2>/dev/null || cat VERSION)

# # Build the app with PyInstaller
# pyinstaller --onefile --noconsole --add-data ".env:." --add-data "facilityReport.xlsx:." --add-data "Zips by Address File Group.xlsx:." --name "PostFlow-v1.0.0" main.py   

# # Notify the user
# echo "Build completed: MyApp-$version"

# Get version from Git or fallback to VERSION file
# version=$(git describe --tags --abbrev=0 2>/dev/null || cat VERSION)

# # Run PyInstaller with dynamic version in the app name
# pyinstaller --onefile --noconsole \
#   --add-data ".env;." \
#   --add-data "facilityReport.xlsx;." \
#   --add-data "Zips by Address File Group.xlsx;." \
#   --add-data "VERSION;." \
#   --name "PostFlow-$version" main.py

#   # Notify the user
# echo "Build completed: MyApp-$version"


import subprocess
import os
import platform
import logging
import shutil

def get_version():
    """
    Get the version from Git tags or fallback to VERSION file.
    """
    try:
        # Try to get version from Git tags
        version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL)
        return version.decode("utf-8").strip()
    except Exception:
        # Fallback to VERSION file if Git tags are unavailable
        version_file_path = os.path.join(os.path.dirname(__file__), "VERSION")
        if os.path.exists(version_file_path):
            with open(version_file_path, "r") as version_file:
                return version_file.read().strip()
        else:
            raise FileNotFoundError("No Git tags found and VERSION file is missing.")

def clean_previous_builds():
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            logging.info(f"Deleted previous build folder: {folder}")
    for file in os.listdir("."):
        if file.endswith(".spec"):
            os.remove(file)
            logging.info(f"Deleted previous spec file: {file}")

def build_app():
    logging.basicConfig(
        filename="build.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Starting build process...")
    # Get version dynamically
    try:
        version = get_version()
        logging.info(f"App version: {version}")
    except Exception as e:
        logging.error(f"Failed to retrieve version: {e}")
        return
    # Determine the correct separator for the --add-data flag based on the OS
    if platform.system() == "Windows":
        separator = ";"
        icon_path = "icon.ico"  # Use .ico for Windows
    else:
        separator = ":"
        icon_path = "icon.icns"  # Use .icns for macOS

    required_files = [".env", "facilityReport.xlsx", "Zips by Address File Group.xlsx", "VERSION", icon_path]
    for file in required_files:
        if not os.path.exists(file):
            logging.error(f"Required file is missing: {file}")
            return
    # Check if the icon file exists
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon file not found: {icon_path}")

    clean_previous_builds()
    

    # Build the PyInstaller command
    pyinstaller_command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--add-data=.env{separator}.",
        f"--add-data=facilityReport.xlsx{separator}.",
        f"--add-data=Zips by Address File Group.xlsx{separator}.",
        f"--add-data=VERSION{separator}.",
        f"--add-data=resources/splash.png{separator}resources",
        f"--icon={icon_path}",  # Add the icon file
        f"--name=PostFlow-{version}",
        "main.py"
    ]

    # Print the command for debugging purposes
    print("Running PyInstaller command:")
    print(" ".join(pyinstaller_command))

    # Run the PyInstaller command
    try:
        subprocess.run(pyinstaller_command, check=True)
        logging.info("Build completed successfully!")
        output_path = os.path.join("dist", f"PostFlow-{version}")
        if os.path.exists(output_path):
            logging.info(f"Build output located at: {output_path}")
        else:
            logging.error("Build completed but output directory is missing.")
    except subprocess.CalledProcessError as e:
        logging.error(f"PyInstaller build failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    build_app()
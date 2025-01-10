

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

def build_app():
    # Get version dynamically
    version = get_version()

    # Determine the correct separator for the --add-data flag based on the OS
    if platform.system() == "Windows":
        separator = ";"
    else:
        separator = ":"

    # Build the PyInstaller command
    pyinstaller_command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--add-data=.env{separator}.",
        f"--add-data=facilityReport.xlsx{separator}.",
        f"--add-data=Zips by Address File Group.xlsx{separator}.",
        f"--add-data=VERSION{separator}.",
        f"--name=PostFlow-{version}",
        "main.py"
    ]

    # Print the command for debugging purposes
    print("Running PyInstaller command:")
    print(" ".join(pyinstaller_command))

    # Run the PyInstaller command
    try:
        subprocess.run(pyinstaller_command, check=True)
        print("Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    build_app()
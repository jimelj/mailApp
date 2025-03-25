# PostFlow

A comprehensive desktop application for managing postal and shipping operations with multiple specialized features including CSM data processing, label printing, and financial tracking.

## Features

- **CSM Data Processing**: Parse and process CSM (Customer Service Management) data files
- **Skid Tag Printing**: Generate and print skid tags for shipments
- **Tray Tag Management**: Handle tray tag printing and organization
- **Financial Tracking**: Monitor and manage financial aspects of shipping operations
- **Trucking Operations**: Manage trucking-related logistics
- **Status Monitoring**: Real-time status indicators for various operations
- **Multi-platform Support**: Works on both Windows and macOS

## System Requirements

- Python 3.x
- Qt 6 (PySide6)
- Operating System: Windows or macOS

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate     # On Windows
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

Key dependencies include:
- PySide6 - GUI framework
- pandas - Data processing
- openpyxl - Excel file handling
- PyMuPDF - PDF processing
- requests - HTTP requests
- python-dotenv - Environment variable management
- paramiko - SFTP operations
- And more (see requirements.txt for complete list)

## Project Structure

- `main.py` - Main application entry point and GUI initialization
- `csmController.py` - CSM data processing and management
- `printController.py` - Printing functionality management
- `trayController.py` - Tray tag operations
- `money.py` - Financial tracking and management
- `trucking.py` - Trucking operations management
- `util.py` - Utility functions and helpers
- `StatusIndicator.py` - Status monitoring system
- `update.py` - Application update functionality

## Configuration

1. Create a `.env` file in the root directory
2. Configure necessary environment variables (refer to `.env.example` if available)
3. Ensure all required data files are in place

## Usage

Run the application:
```bash
python main.py
```

The application provides a tabbed interface with different functionality:
1. Main Tab - Overview and file management
2. CSM Tab - Process CSM data files
3. Print Tags Tab - Generate and print shipping tags
4. Tray Tags Tab - Manage tray tag operations
5. Money Tab - Financial tracking
6. Trucking Tab - Manage trucking operations

## Building

To build the executable:
```bash
python build.py
```

The built application will be available in the `dist` directory.

## Error Handling

- Application logs are stored in `error.log`
- Build logs are stored in `build.log`
- The application includes comprehensive error handling and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Support

For support, please JJOSEPH@cbaol.com

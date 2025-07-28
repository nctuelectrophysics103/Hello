# Pad to Pin Number Mapping Tool

A comprehensive Visual Studio Code compatible tool for managing IC pad to pin number mappings with a modern GUI interface.

## Features

- **Modern GUI Interface**: Built with tkinter for cross-platform compatibility
- **Comprehensive Mapping Management**: Add, edit, delete, and search pin mappings
- **Data Validation**: Built-in validation for pad numbers, pin numbers, and signal names
- **Multiple Export Formats**: JSON, CSV, and text reports
- **Import/Export**: Load and save mapping configurations
- **Search and Filter**: Real-time search across all mapping fields
- **Conflict Detection**: Automatically detect duplicate mappings
- **VS Code Integration**: Optimized for Visual Studio Code development environment

## Installation

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup

1. Clone or download this repository
2. Install optional dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### VS Code Setup

This project includes VS Code configuration files for optimal development experience:

- **Settings**: Python-specific IDE configuration
- **Tasks**: Quick run and build commands
- **Launch**: Debug configurations
- **Extensions**: Recommended Python extensions

## Usage

### Running the Application

#### From VS Code:
1. Open the project in VS Code
2. Press `F5` to run with debugging, or
3. Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Pad Pin Mapper"

#### From Terminal:
```bash
python3 pad_pin_mapper.py
```

### Basic Operations

1. **Adding Mappings**: Fill in the form fields and click "Add"
2. **Editing Mappings**: Double-click a row to load it into the form, modify, and click "Update"
3. **Deleting Mappings**: Select a row and click "Delete"
4. **Searching**: Type in the search box to filter mappings in real-time

### File Operations

- **New**: Create a new mapping file
- **Open**: Load existing JSON mapping files
- **Save/Save As**: Save current mappings to JSON format
- **Export CSV**: Export to CSV format for Excel compatibility
- **Import CSV**: Import mappings from CSV files

## Data Format

### JSON Format
```json
{
  "metadata": {
    "created": "2024-01-01T12:00:00",
    "version": "1.0",
    "tool": "Pad to Pin Mapper"
  },
  "mappings": [
    {
      "pad_number": "A1",
      "pin_number": "1",
      "signal_name": "VCC",
      "pin_type": "POWER",
      "description": "Power supply"
    }
  ]
}
```

### CSV Format
```csv
Pad Number,Pin Number,Signal Name,Pin Type,Description
A1,1,VCC,POWER,Power supply
A2,2,GND,GROUND,Ground
```

## Pin Types

The tool supports the following predefined pin types:
- `INPUT`: Input signals
- `OUTPUT`: Output signals  
- `BIDIRECTIONAL`: Bidirectional I/O
- `POWER`: Power supply pins
- `GROUND`: Ground pins
- `NC`: No connection

## Validation Rules

### Pad Numbers
- Format: Letter(s) followed by number(s) (e.g., A1, B12, AA1)
- Must be unique within a mapping set
- Cannot be empty

### Pin Numbers
- Must contain at least one digit
- Can include letters (e.g., 1, A1, 12B)
- Must be unique within a mapping set
- Cannot be empty

### Signal Names
- Optional field
- Should follow identifier conventions (letters, numbers, underscore)
- Should be unique for clarity

## Keyboard Shortcuts

- `F5`: Run application (in VS Code)
- `Ctrl+N`: New mapping file
- `Ctrl+O`: Open file
- `Ctrl+S`: Save file
- `Delete`: Delete selected mapping
- `Escape`: Clear form
- `Enter`: Add mapping (when in form fields)

## Development

### Project Structure
```
.
├── pad_pin_mapper.py      # Main application
├── pin_mapper_utils.py    # Utility functions
├── requirements.txt       # Python dependencies
├── .vscode/              # VS Code configuration
│   ├── settings.json     # IDE settings
│   ├── launch.json       # Debug configurations
│   └── tasks.json        # Build tasks
└── README.md             # This file
```

### VS Code Tasks

- **Run Pad Pin Mapper**: Execute the main application
- **Install Python Dependencies**: Install required packages
- **Python: Format Code**: Format code with Black
- **Python: Lint Code**: Run pylint on all Python files

### Code Quality

The project includes configuration for:
- **Black**: Code formatting
- **Pylint**: Code linting and style checking
- **Flake8**: Additional style checking
- **MyPy**: Type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Run the linting tools to ensure code quality
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **tkinter not found**: Install tkinter using your system package manager
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # CentOS/RHEL
   sudo yum install tkinter
   ```

2. **Permission errors**: Ensure you have write permissions to the directory where you're saving files

3. **Display issues**: If running in a remote environment, ensure X11 forwarding is enabled

### VS Code Integration Issues

1. **Python interpreter not found**: Check that the Python path in `.vscode/settings.json` matches your system
2. **Tasks not working**: Verify that Python 3 is in your system PATH
3. **Debugging issues**: Ensure the Python extension is installed in VS Code

## License

This project is open source and available under the MIT License.

## Version History

- **1.0.0**: Initial release with core functionality
  - GUI interface with tkinter
  - JSON and CSV import/export
  - Real-time search and validation
  - VS Code integration

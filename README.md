# Log Cleaner

A Python utility for cleaning and reformatting log files containing email:password combinations.

## Features

- Remove duplicate entries
- Reformat various formats to Email:Pass
- Remove whitespaces and clean up formatting
- GUI file picker for easy file selection
- Automatic logging of operations

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)

## Installation

1. Clone or download this repository
2. No additional dependencies required - uses Python standard library only

## Usage

Run the script:

```bash
python main.py
```

The program will display a menu with the following options:

1. Remove duplicates
2. Reformat to Email:Pass
3. Remove whitespaces
4. Run all (1-3)
5. Exit

After selecting an option, you'll be prompted to:
- Select an input log file
- Select an output directory

The cleaned file will be saved as `[original_filename]_cleaned.txt` in your chosen output directory.

## Logs

Operation logs are automatically saved to the `logs/` directory with timestamps.

## License

This project is provided as-is for educational purposes.

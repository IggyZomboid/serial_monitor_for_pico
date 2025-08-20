# Iggys Serial Monitor for Pi Pico

A simple serial monitor intended for use with the Raspberry Pi Pico and Debug-probe. As these use the same baud rate and setting each time config is kept to a minimum.

## Features

- Lists available COM ports and allows selection
- Connects/disconnects to the selected serial port
- Displays incoming serial data in a scrollable text area
- Supports baud rate selection (default: 115200)
- Allows refreshing the COM port list
- Remembers last selected port and settings between sessions

## Requirements

- Python 3.x
- PyQt5
- pyserial

## Installation

1. Clone this repository:

    ```sh
    git clone https://github.com/yourusername/iggys-serial-monitor.git
    cd iggys-serial-monitor
    ```

2. Install dependencies:

    ```sh
    pip install pyqt5 pyserial
    ```

## Usage

1. Run the application:

    ```sh
    python main.py
    ```

2. Select the desired COM port and baud rate.
3. Click "Connect" to start monitoring serial data from your Raspberry Pi Pico.
4. Use "Refresh" to update the list of available COM ports.

## UI

The interface is defined in `MainForm.ui` and features:

- A main window titled "Iggy Serial Monitor"
- A combo box for COM port selection
- A combo box for baud rate selection
- A text area for displaying serial output
- Buttons for connecting, refreshing ports, and clearing output

## License

MIT

## Author

IggyZomboid

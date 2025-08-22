# Iggy's Serial Monitor for Pi Pico

A simple serial monitor designed for use with the Raspberry Pi Pico and Debug-probe. This application minimizes configuration by using a consistent baud rate and settings.

## Features

- Lists available COM ports and allows selection.
- Connects/disconnects to the selected serial port.
- Displays incoming serial data in a scrollable text area.
- Supports baud rate selection (default: 115200).
- Allows refreshing the COM port list.
- Remembers the last selected port and settings between sessions.
- Provides a separate data view window for advanced data visualization.

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
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:

    ```sh
    python main.py
    ```

2. Select the desired COM port and baud rate.
3. Click "Connect" to start monitoring serial data from your Raspberry Pi Pico.
4. Use "Refresh" to update the list of available COM ports.
5. Click "Data View" to open the advanced data view window.

## Project Structure

<<<<<<< HEAD
The interface is defined in `MainForm.ui` and features:

- A main window titled "Iggy Serial Monitor"
- A combo box for COM port selection
- A combo box for baud rate selection
- A text area for displaying serial output
- Buttons for connecting, refreshing ports, and clearing output
=======
```md
serial_monitor_for_pico/
├── app_config/
│   ├── __init__.py
│   ├── app_config.py
├── com_port/
│   ├── __init__.py
│   ├── com_port.py
├── serial_reader/
│   ├── __init__.py
│   ├── SerialReaderThread.py
├── views/
│   ├── __init__.py
│   ├── Data_View_Window.py
│   ├── Main_Window.py
├── UI/
│   ├── Data_view_window.ui
│   ├── MainForm.ui
├── settings.ini
├── LICENSE
├── main.py
├── readme.md
├── requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Iggy Zomboid

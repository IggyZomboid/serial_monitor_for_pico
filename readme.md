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
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
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
5. Click "Data View" to open the advanced data view window, where you can register data points and visualize tabular data.

## Project Structure

```md
serial_monitor_for_pico/
├── app_config/
│   ├── [__init__.py](http://_vscodecontentref_/0)
│   ├── [app_config.py](http://_vscodecontentref_/1)
├── com_port/
│   ├── [__init__.py](http://_vscodecontentref_/2)
│   ├── [com_port.py](http://_vscodecontentref_/3)
├── serial_reader/
│   ├── [__init__.py](http://_vscodecontentref_/4)
│   ├── [SerialReaderThread.py](http://_vscodecontentref_/5)
├── views/
│   ├── [__init__.py](http://_vscodecontentref_/6)
│   ├── [Data_View_Window.py](http://_vscodecontentref_/7)
│   ├── [Main_Window.py](http://_vscodecontentref_/8)
├── UI/
│   ├── [Data_view_window.ui](http://_vscodecontentref_/9)
│   ├── [MainForm.ui](http://_vscodecontentref_/10)
├── [settings.ini](http://_vscodecontentref_/11)
├── LICENSE
├── [main.py](http://_vscodecontentref_/12)
├── [readme.md](http://_vscodecontentref_/13)
├── [requirements.txt](http://_vscodecontentref_/14)
```

## Interface

The interface is defined in `MainForm.ui` and features:

- A main window titled "Iggy Serial Monitor"
- A combo box for COM port selection
- A combo box for baud rate selection
- A text area for displaying serial output
- Buttons for connecting, refreshing ports, and clearing output

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Iggy Zomboid

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

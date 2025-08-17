import sys
import glob
import serial
import threading
import configparser
from PyQt5 import QtWidgets, uic, QtCore
from serial.tools import list_ports
from datetime import datetime

# Constants
class AppConfig:
    def __init__(self):
        self.baudrates = ['300', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '57600', '115200', '230400', '250000']
        self.line_endings = ['None', 'CR', 'LF', 'CRLF']
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        
        # Set default values for user settings
        self.last_selected_port = 0
        self.last_selected_view_mode = 0
        self.last_selected_line_ending = 0
        self.last_selected_baudrate = 0
        
        if 'user_settings' in self.config:
            # Convert values to integers where necessary
            self.last_selected_port = int(self.config['user_settings'].get('selected_port', 0))
            print(f"Last selected port: {self.last_selected_port}")

            self.last_selected_view_mode = int(self.config['user_settings'].get('selected_view_mode', 0))
            print(f"Last selected view mode: {self.last_selected_view_mode}")

            self.last_selected_line_ending = int(self.config['user_settings'].get('selected_line_ending', 0))
            print(f"Last selected line ending: {self.last_selected_line_ending}")

            self.last_selected_baudrate = int(self.config['user_settings'].get('selected_baudrate', 0))
            print(f"Last selected baudrate: {self.last_selected_baudrate}")
    
    def save_user_settings(self):
        """
        Saves the current user settings to 'settings.ini'.
        """
        print("Saving user settings...")  # Debug statement

        if 'user_settings' not in self.config:
            self.config['user_settings'] = {}

        # Convert all values to strings before saving
        self.config['user_settings']['selected_port'] = str(self.last_selected_port)
        self.config['user_settings']['selected_view_mode'] = str(self.last_selected_view_mode)
        self.config['user_settings']['selected_line_ending'] = str(self.last_selected_line_ending)
        self.config['user_settings']['selected_baudrate'] = str(self.last_selected_baudrate)

        # Debug print to verify the values being saved
        print("Config to save:", dict(self.config['user_settings']))

        # Write the settings to the file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        print("Settings saved!")  # Debug statement
            
# Create a global instance
app_config = AppConfig()


# COM Port Class
class com_port:
    def __init__(self, comport):
        self.device = comport.device
        self.name = comport.name
        self.description = comport.description
        self.hwid = comport.hwid
        self.vid = comport.vid
        self.pid = comport.pid
        self.serial_number = comport.serial_number
        self.location = comport.location
        self.manufacturer = comport.manufacturer
        self.product = comport.product
        self.interface = comport.interface

    @property
    def UIString(self):
        return f"{self.name} - {self.description}"


# Global COM Ports Dictionary
com_ports = {}


# Serial Reader Thread
class SerialReaderThread(threading.Thread):
    """
    A thread class for reading data from a serial port in the background.

    This class continuously reads data from the provided serial port and sends
    the received data to a callback function for further processing or display.
    It runs in a separate thread to avoid blocking the main application.

    Attributes:
        serial_port (serial.Serial): The serial port object to read data from.
        callback (function): A function to handle the received data (e.g., update the UI).
        running (bool): A flag to control the thread's execution.
    """
    def __init__(self, serial_port, callback):
        """
        Initializes the SerialReaderThread.

        Args:
            serial_port (serial.Serial): The serial port object to read data from.
            callback (function): A function to handle the received data.
        """
        super().__init__()
        self.serial_port = serial_port
        self.callback = callback  # Function to send data back to the UI
        self.running = True       # Flag to control the thread

    def run(self):
        """
        The main logic of the thread.

        This method runs in a loop, continuously reading data from the serial port
        while the thread is running and the serial port is open. It decodes the received
        data and sends it to the callback function. If an error occurs, it sends the
        error message to the callback and stops the thread.
        """
        while self.running and self.serial_port.is_open:
            try:
                # Read a line of data from the serial port
                raw_line = self.serial_port.readline()

                # Attempt to decode the data using UTF-8 encoding
                try:
                    line = raw_line.decode('utf-8').strip()
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    # If UTF-8 decoding fails, fall back to ASCII encoding
                    line = raw_line.decode('ascii', errors='ignore').strip()
                    encoding = 'ascii'

                # If the line is not empty, pass it to the callback function
                if line:
                    self.callback(f"{line}")
            except Exception as e:
                # If an error occurs, send the error message to the callback
                self.callback(f"Error: {str(e)}")
                break

    def stop(self):
        """
        Stops the thread and closes the serial port.

        This method sets the running flag to False, which causes the thread's loop
        to exit. It also closes the serial port if it is still open.
        """
        self.running = False
        if self.serial_port.is_open:
            self.serial_port.close()


# Main Window Class
class MainWindow(QtWidgets.QMainWindow):
    """
    MainWindow is the primary GUI class for the serial monitor application. It provides
    an interface for interacting with serial ports, including connecting, disconnecting,
    refreshing available ports, and displaying messages from the serial port.
    Attributes:
        port_comboBox (QtWidgets.QComboBox): Dropdown for selecting available COM ports.
        baud_comboBox (QtWidgets.QComboBox): Dropdown for selecting baud rates.
        lineEnding_comboBox (QtWidgets.QComboBox): Dropdown for selecting line endings.
        view_radio_buttons_group (QtWidgets.QButtonGroup): Group of radio buttons for view options.
        view_radio_buttons (list): List of radio buttons in the view group.
        connect_button (QtWidgets.QPushButton): Button to connect to the selected COM port.
        refresh_ports_Button (QtWidgets.QPushButton): Button to refresh the list of available COM ports.
        clear_button (QtWidgets.QPushButton): Button to clear the output text area.
        output_text (QtWidgets.QTextEdit): Text area for displaying messages and logs.
        ser (serial.Serial or None): Serial port object for communication.
        serial_thread (SerialReaderThread or None): Thread for reading data from the serial port.
    Methods:
        __init__():
            Initializes the MainWindow, sets up the UI, and connects button actions to their handlers.
        disconnect_port():
            Disconnects from the currently connected serial port, if any, and stops the serial reader thread.
        refresh_ports():
            Refreshes the list of available COM ports and disconnects from the current port if connected.
        output_UI_message(message):
            Displays a formatted UI message in the output text area.
        output_Port_message(message):
            Displays a formatted message received from the serial port in the output text area.
        connect_port():
            Connects to the selected COM port with the specified baud rate and starts the serial reader thread.
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainForm.ui', self)

        # Get all UI elements
        self.port_comboBox = self.findChild(QtWidgets.QComboBox, 'port_comboBox')
        self.baud_comboBox = self.findChild(QtWidgets.QComboBox, 'baud_comboBox')
        self.lineEnding_comboBox = self.findChild(QtWidgets.QComboBox, 'lineEnding_comboBox')
        self.view_radio_buttons_group = self.findChild(QtWidgets.QButtonGroup, 'view_radio_buttons_group')
        self.view_radio_buttons = self.view_radio_buttons_group.buttons()
        self.connect_button = self.findChild(QtWidgets.QPushButton, 'connect_button')
        self.refresh_ports_Button = self.findChild(QtWidgets.QPushButton, 'refresh_ports_Button')
        self.clear_button = self.findChild(QtWidgets.QPushButton, 'clear_button')
        self.output_text = self.findChild(QtWidgets.QTextEdit, 'output_text')
        
        #update AppConfig fields when values change
        self.port_comboBox.currentTextChanged.connect(lambda: setattr(app_config, 'last_selected_port', self.port_comboBox.currentIndex()))
        self.baud_comboBox.currentTextChanged.connect(lambda: setattr(app_config, 'last_selected_baudrate', self.baud_comboBox.currentIndex()))
        self.lineEnding_comboBox.currentTextChanged.connect(lambda: setattr(app_config, 'last_selected_line_ending', self.lineEnding_comboBox.currentIndex()))
        self.view_radio_buttons[0].toggled.connect(
            lambda checked: setattr(app_config, 'last_selected_view_mode', 0 if checked else 1)
        )

        # Connect buttons to their handlers
        self.refresh_ports_Button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_port)
        self.clear_button.clicked.connect(self.output_text.clear)  # Clear output text area

        # Serial port placeholder
        self.ser = None

        # Temporarily block signals during initialization
        self.port_comboBox.blockSignals(True)
        self.baud_comboBox.blockSignals(True)
        self.lineEnding_comboBox.blockSignals(True)

        # Set initial values
        self.port_comboBox.setCurrentText(app_config.last_selected_port)
        self.baud_comboBox.setCurrentText(app_config.last_selected_baudrate)
        self.lineEnding_comboBox.setCurrentText(app_config.last_selected_line_ending)

        # Re-enable signals
        self.port_comboBox.blockSignals(False)
        self.baud_comboBox.blockSignals(False)
        self.lineEnding_comboBox.blockSignals(False)
                
        self.show()

    # Disconnect from the serial port
    def disconnect_port(self):
        if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join()  # Wait for the thread to finish
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.output_UI_message("Disconnected from the serial port.")

    # Refresh the list of COM ports
    def refresh_ports(self):
        if self.ser and self.ser.is_open:
            self.disconnect_port()  # Disconnect if a port is currently open
            self.ser = None  # Close the serial port if it's open
        self.output_UI_message("Refreshing COM ports...")
        get_com_ports(self)  # Refresh the list of COM ports

    # Output a UI message
    def output_UI_message(self, message):
        inChevons = "&gt;&gt;&gt;&gt;&gt;&gt;&gt;"
        outChevrons = "&lt;&lt;&lt;&lt;&lt;&lt;&lt;"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ui_message = f'<span style="color:green;">[{timestamp}] - {inChevons} UI Message Start {outChevrons} <br>{message}<br>{inChevons} UI Message End {outChevrons}</span>'
        self.output_text.append(ui_message)  # Append the message to the output text area
        self.output_text.ensureCursorVisible()  # Scroll to the latest message

    # Output a message from the serial port
    def output_Port_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ui_message = f'<span style="color:blue;">[{timestamp}] - {message}</span>'
        self.output_text.append(ui_message)  # Append the message to the output text area
        self.output_text.ensureCursorVisible()  # Scroll to the latest message

    # Connect to the selected serial port
    def connect_port(self):
        selected_port = self.port_comboBox.currentText()
        selected_baud = self.baud_comboBox.currentText()

        port_info = com_ports.get(selected_port, None)

        if not selected_port:
            self.output_UI_message("No COM port selected.")
            return

        try:
            # Open the serial port
            self.ser = serial.Serial(port_info.name, baudrate=int(selected_baud), timeout=1)
            self.output_UI_message(f"Connected to {selected_port} at {selected_baud} baud.")

            # Start the serial reader thread
            self.serial_thread = SerialReaderThread(self.ser, self.output_Port_message)
            self.serial_thread.start()

        except Exception as e:
            self.output_UI_message(f"Error connecting to {selected_port}: {str(e)}")

    # Handle window close event saving user settings to settings.ini
    def closeEvent(self, event):
        """
        Handles the window close event to save user settings to 'settings.ini'.

        This method is called when the main window is closed. It ensures that any user-specific
        settings are saved before the application exits.

        Args:
            event: The close event object, which can be used to control the closing behavior.
        """
        # Save user settings
        app_config.save_user_settings()

        # Disconnect from the serial port
        self.disconnect_port()
       

# Get COM Ports
def get_com_ports(window):
    """
    Scans for available COM ports, updates the global `com_ports` dictionary, 
    and displays the found ports in the provided window.

    Args:
        window: An object that provides a method `output_UI_message` to display 
                messages in the user interface.

    Functionality:
        - Uses the `list_ports.comports()` function to retrieve a list of available COM ports.
        - Clears the global `com_ports` dictionary to ensure it only contains the latest data.
        - Iterates through the list of ports, creating a `com_port` object for each port.
        - Adds each `com_port` object to the `com_ports` dictionary using its `UIString` as the key.
        - Constructs a string containing all found COM ports and their details.
        - Displays the total number of found ports and their details in the user interface.

    Notes:
        - The `com_ports` dictionary is assumed to be a global variable.
        - The `com_port` class or function is assumed to be defined elsewhere in the codebase.
        - The `UIString` attribute of `com_port` objects is used as a unique identifier for each port.

    Example:
        If 3 COM ports are found, the function will display a message like:
        "Found 3 COM ports:
        COM1<br>COM2<br>COM3<br>"
    """
    ports = list_ports.comports()
    com_ports.clear()  # Clear the list before adding new ports
    portsfound = ""
    for port in ports:
        new_port = com_port(port)
        com_ports[new_port.UIString] = new_port
        portsfound += f"{new_port.UIString}<br>"
    window.output_UI_message(f"Found {len(ports)} COM ports:<br>{portsfound}")


# Main Entry Point
def main():
    """
    The main function initializes and runs the GUI application for the serial monitor.

    This function performs the following steps:
    1. Creates a QApplication instance, which is required for any PyQt5 application.
    2. Initializes the main window of the application.
    3. Retrieves available COM ports and populates the port selection dropdown.
    4. Populates the baud rate and line ending dropdowns with predefined options.
    5. Sets the default selection for radio buttons, if available.
    6. Starts the application's event loop to handle user interactions.

    Note:
    - Ensure that the `QtWidgets`, `sys`, and other required modules are imported.
    - The `get_com_ports`, `com_ports`, `baudrates`, and `line_endings` variables or functions 
      must be defined elsewhere in the code for this function to work correctly.
    - The `MainWindow` class should be implemented to define the GUI layout and components.

    Raises:
        SystemExit: Exits the application when the event loop ends.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    get_com_ports(window)
    window.port_comboBox.addItems(com_ports.keys())
    window.baud_comboBox.addItems(app_config.baudrates)
    window.lineEnding_comboBox.addItems(app_config.line_endings)  # Example items
    print(f"Type of app_config.last_selected_port: {type(app_config.last_selected_port)}")
    print(f"app_config.last_selected_baudrate: {app_config.last_selected_port}")
    window.port_comboBox.setCurrentIndex(app_config.last_selected_port)
    window.baud_comboBox.setCurrentIndex(app_config.last_selected_baudrate)
    window.lineEnding_comboBox.setCurrentIndex(app_config.last_selected_line_ending)
        
    if window.view_radio_buttons:
        if app_config.last_selected_view_mode == 'Text':
            window.view_radio_buttons[0].setChecked(True)  # Default first item to checked
        else:
            window.view_radio_buttons[1].setChecked(True)  # Default first item to checked
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import sys
import glob
import serial
import threading
import configparser
from PyQt5 import QtWidgets, uic, QtCore
from serial.tools import list_ports
from datetime import datetime
import re

BAUD_RATE = 115200

# Constants
class AppConfig:
    """
    A class to manage application configuration and user settings.

    This class uses the `configparser` module to read and write user settings
    to a configuration file named 'settings.ini'. It provides functionality
    to load settings on initialization and save updated settings back to the file.

    Attributes:
        config (ConfigParser): An instance of ConfigParser to manage configuration data.
        last_selected_port (int): The last selected port, defaulting to 0 if not specified in the configuration.

    Methods:
        __init__():
            Initializes the AppConfig instance, loads settings from 'settings.ini',
            and sets default values for user settings if not present.
        save_user_settings():
            Saves the current user settings to 'settings.ini'.
    """
    def __init__(self):
        """
        Initializes the AppConfig instance.

        This method reads the configuration file 'settings.ini' and loads user settings.
        If the file or specific settings are not present, it sets default values.
        """
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        
        # Set default values for user settings
        self.last_selected_port = 0
        
        if 'user_settings' in self.config:
            # Convert values to integers where necessary
            self.last_selected_port = int(self.config['user_settings'].get('selected_port', 0))
            # print(f"Last selected port: {self.last_selected_port}")
    
    def save_user_settings(self):
        """
        Saves the current user settings to 'settings.ini'.

        This method updates the configuration file with the latest user settings,
        ensuring that all values are converted to strings before saving.
        """
        # print("Saving user settings...")  # Debug statement

        if 'user_settings' not in self.config:
            self.config['user_settings'] = {}

        # Convert all values to strings before saving
        self.config['user_settings']['selected_port'] = str(self.last_selected_port)

        # Debug # print to verify the values being saved
        # print("Config to save:", dict(self.config['user_settings']))

        # Write the settings to the file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        # print("Settings saved!")  # Debug statement
    # Removed duplicate __init__ method to avoid overriding the first implementation.
    
    def save_user_settings(self):
        """
        Saves the current user settings to 'settings.ini'.
        """
        # print("Saving user settings...")  # Debug statement

        if 'user_settings' not in self.config:
            self.config['user_settings'] = {}

        # Convert all values to strings before saving
        self.config['user_settings']['selected_port'] = str(self.last_selected_port)

        # Debug # print to verify the values being saved
        # print("Config to save:", dict(self.config['user_settings']))

        # Write the settings to the file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        # print("Settings saved!")  # Debug statement
            
# Create a global instance
app_config = AppConfig()


# COM Port Class
class com_port:
    """
    A class to represent a COM port and its associated details.

    This class encapsulates the properties of a COM port, such as its name, description,
    hardware ID, vendor ID, product ID, and other metadata. It provides a convenient way
    to access and display information about a COM port.

    Attributes:
        device (str): The device path of the COM port.
        name (str): The name of the COM port.
        description (str): A brief description of the COM port.
        hwid (str): The hardware ID of the COM port.
        vid (int): The vendor ID of the COM port.
        pid (int): The product ID of the COM port.
        serial_number (str): The serial number of the COM port.
        location (str): The physical location of the COM port.
        manufacturer (str): The manufacturer of the COM port.
        product (str): The product name of the COM port.
        interface (str): The interface type of the COM port.

    Methods:
        UIString:
            Returns a formatted string representation of the COM port for display in the UI.
    """
    def __init__(self, comport):
        """
        Initializes a com_port instance with the details of the provided COM port.

        Args:
            comport: An object representing a COM port, typically obtained from `list_ports.comports()`.
        """
        self.device = comport.device  # The device path (e.g., COM3)
        self.name = comport.name  # The name of the COM port
        self.description = comport.description  # A description of the COM port
        self.hwid = comport.hwid  # The hardware ID of the COM port
        self.vid = comport.vid  # The vendor ID of the COM port
        self.pid = comport.pid  # The product ID of the COM port
        self.serial_number = comport.serial_number  # The serial number of the COM port
        self.location = comport.location  # The physical location of the COM port
        self.manufacturer = comport.manufacturer  # The manufacturer of the COM port
        self.product = comport.product  # The product name of the COM port
        self.interface = comport.interface  # The interface type of the COM port

    @property
    def UIString(self):
        """
        Returns a formatted string representation of the COM port for display in the UI.

        The string includes the name and description of the COM port, making it easier
        for users to identify the port in a dropdown or list.

        Returns:
            str: A formatted string combining the name and description of the COM port.
        """
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
        self.serial_port = serial_port  # Serial port to read data from
        self.callback = callback  # Function to send data back to the UI
        self.running = True  # Flag to control the thread's execution

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
                    line = raw_line.decode('utf-8').strip()  # Decode using UTF-8
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    # If UTF-8 decoding fails, fall back to ASCII encoding
                    line = raw_line.decode('ascii', errors='ignore').strip()
                    encoding = 'ascii'

                # If the line is not empty, pass it to the callback function
                if line:
                    self.callback(f"{line}")  # Send the decoded line to the callback
            except Exception as e:
                # If an error occurs, send the error message to the callback
                self.callback(f"Error: {str(e)}")
                break  # Exit the loop on error

    def stop(self):
        """
        Stops the thread and closes the serial port.

        This method sets the running flag to False, which causes the thread's loop
        to exit. It also closes the serial port if it is still open.
        """
        self.running = False  # Stop the thread's execution
        if self.serial_port.is_open:
            self.serial_port.close()  # Close the serial port if open

class Data_View_Window(QtWidgets.QMainWindow):
    """
    A class to represent a data view window in the application.

    This class is intended to provide a separate window for displaying data
    from the serial port or other sources. It inherits from QMainWindow and
    can be customized with additional UI elements and functionality.

    Attributes:
        None (currently, but can be extended with UI elements).
    """
    def __init__(self):
        super(Data_View_Window, self).__init__()
        uic.loadUi('Data_view_window.ui', self)
        
        self.input_name_text = self.findChild(QtWidgets.QPlainTextEdit, 'input_name_text')
        self.preview_txt_label = self.findChild(QtWidgets.QLabel, 'preview_txt_label')
        self.input_name_text.textChanged.connect(self.validateNameText)
        self.show()
    
       
    def validateNameText(self):
        """
        Validates the input name text to ensure it is not empty.
        If empty, sets the text to 'Default Name'.
        """
        print("Validating input name text...")
        print(f"Current text: {self.input_name_text.toPlainText()}")
        if not self.input_name_text.toPlainText():
            print("Input name text is empty, setting to 'Default Name'.")
            self.input_name_text.setPlainText('Default Name')
        else:
            print("Input name text is not empty, proceeding with sanitization.")
        # Replace spaces with underscores first
        sanitized_text = self.input_name_text.toPlainText().replace(' ', '_')
        print("Replacing spaces with underscores in input name text...")
        
        # Remove any character that is not alphanumeric, underscore, or hyphen
        sanitized_text = re.sub(r'[^a-zA-Z0-9_-]', '', sanitized_text)
        if sanitized_text != self.input_name_text.toPlainText():
            print(f"Sanitized text: {sanitized_text}")
        
        self.preview_txt_label.setText(sanitized_text)
        
        print(sanitized_text)
               

# Main Window Class
class MainWindow(QtWidgets.QMainWindow):
    """
    MainWindow is the primary GUI class for the serial monitor application. It provides
    an interface for interacting with serial ports, including connecting, disconnecting,
    refreshing available ports, and displaying messages from the serial port.

    Attributes:
        port_comboBox (QtWidgets.QComboBox): Dropdown for selecting available COM ports.
        connect_button (QtWidgets.QPushButton): Button to connect to the selected COM port.
        refresh_ports_Button (QtWidgets.QPushButton): Button to refresh the list of available COM ports.
        clear_button (QtWidgets.QPushButton): Button to clear the output text area.
        data_view_button (QtWidgets.QPushButton): Button to open the data view window.
        output_text (QtWidgets.QTextEdit): Text area for displaying messages and logs.
        ser (serial.Serial or None): Serial port object for communication.
        serial_thread (SerialReaderThread or None): Thread for reading data from the serial port.
        timer (QtCore.QTimer): Timer to periodically check for available COM ports.

    Methods:
        __init__():
            Initializes the MainWindow, sets up the UI, and connects button actions to their handlers.
        data_view_button_clicked():
            Opens the data view window when the data view button is clicked.
        get_com_ports(silent=False):
            Scans for available COM ports and updates the dropdown list.
        port_changed():
            Handles the event when the selected port in the combo box changes and updates the configuration.
        disconnect_port():
            Disconnects from the currently connected serial port, if any, and stops the serial reader thread.
        refresh_ports():
            Refreshes the list of available COM ports and disconnects from the current port if connected.
        output_UI_message(message):
            Displays a formatted UI message in the output text area.
        output_Port_message(message):
            Displays a formatted message received from the serial port in the output text area.
        connect_port():
            Connects to the selected COM port and starts the serial reader thread.
        closeEvent(event):
            Handles the window close event to save user settings and disconnect from the serial port.
    """
    def __init__(self):
        """
        Initializes the MainWindow, sets up the UI, and connects button actions to their handlers.

        - Loads the UI from the 'MainForm.ui' file.
        - Retrieves and initializes UI elements such as buttons, combo boxes, and text areas.
        - Sets up event handlers for button clicks and combo box changes.
        - Starts a timer to periodically check for available COM ports.
        """
        super(MainWindow, self).__init__()
        uic.loadUi('MainForm.ui', self)
        self.get_com_ports()
        # Get all UI elements
        self.port_comboBox = self.findChild(QtWidgets.QComboBox, 'port_comboBox')  
        # print(f"app_config.last_selected_port: {app_config.last_selected_port}")
        # Set the combo box to the last selected port or default to the first item
        if self.port_comboBox.count() > app_config.last_selected_port:
            self.port_comboBox.setCurrentIndex(app_config.last_selected_port)
        else:
            self.port_comboBox.setCurrentIndex(0)
        
        self.connect_button = self.findChild(QtWidgets.QPushButton, 'connect_button')
        self.refresh_ports_Button = self.findChild(QtWidgets.QPushButton, 'refresh_ports_Button')
        self.clear_button = self.findChild(QtWidgets.QPushButton, 'clear_button')
        self.data_view_button = self.findChild(QtWidgets.QPushButton, 'data_view_button')
        self.output_text = self.findChild(QtWidgets.QTextEdit, 'output_text')
        
        # Update AppConfig fields when values change
        self.port_comboBox.currentIndexChanged.connect(self.port_changed)

        # Connect buttons to their handlers
        self.refresh_ports_Button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_port)
        self.clear_button.clicked.connect(self.output_text.clear)  # Clear output text area
        self.data_view_button.clicked.connect(self.data_view_button_clicked)  # Open data view window
        
        # Serial port placeholder
        self.ser = None

        # Timer to check every 2 seconds if the serial port is open
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.get_com_ports(True))
        self.timer.start(2000)
        
        self.show()

    def data_view_button_clicked(self):
        """
        Opens the data view window when the data view button is clicked.
        """
        self.datawindow = Data_View_Window()
        
    def get_com_ports(self, silent=False):
        """
        Scans for available COM ports, updates the global `com_ports` dictionary, 
        and updates the UI with the found ports.

        Args:
            silent (bool): If True, suppresses UI messages about found ports.

        Functionality:
            - Uses `list_ports.comports()` to retrieve a list of available COM ports.
            - Updates the global `com_ports` dictionary and the UI dropdown only if the list of ports has changed.
            - Restores the previously selected port in the dropdown if it still exists.
        """
        ports = list_ports.comports()
        temp_com_ports = {}
        portsfound = ""
        for port in ports:
            new_port = com_port(port)
            # print(f"Device: {new_port.device}, Name: {new_port.name}, Description: {new_port.description}, "
                  # f"HWID: {new_port.hwid}, VID: {new_port.vid}, PID: {new_port.pid}, "
                  # f"Serial Number: {new_port.serial_number}, Location: {new_port.location}, "
                  # f"Manufacturer: {new_port.manufacturer}, Product: {new_port.product}, "
                  # f"Interface: {new_port.interface}")
            temp_com_ports[new_port.UIString] = new_port
            if not silent:
                portsfound += f"{new_port.UIString}<br>"
        if not silent:
            self.output_UI_message(f"Found {len(ports)} COM ports:<br>{portsfound}")
        if set(temp_com_ports.keys()) != set(com_ports.keys()):
            # Only update if the list of ports has changed
            com_ports.clear()
            com_ports.update(temp_com_ports)
            # print(f"temp_com_ports: {len(temp_com_ports)}")
            # print(f"com_ports: {len(com_ports)}")
            # Block signals to avoid triggering events during updates
            self.port_comboBox.blockSignals(True)
            temp_selected_port = self.port_comboBox.currentText()  # Store the current port text
            self.port_comboBox.clear()  # Clear the current combo box items
            self.port_comboBox.addItems(com_ports.keys()) 
            # Restore the last selected index
            if temp_selected_port in com_ports.keys():
                temp_selected_index = list(com_ports.keys()).index(temp_selected_port)
                self.port_comboBox.setCurrentIndex(temp_selected_index)
            else:
                self.port_comboBox.setCurrentIndex(0)
            self.port_comboBox.blockSignals(False)
            # print(f"COM ports updated: {list(com_ports.keys())}")
            
    def port_changed(self):
        """
        Updates AppConfig with the newly selected COM port index and saves settings.

        Triggered when the user selects a different COM port from the dropdown.
        """
        app_config.last_selected_port = self.port_comboBox.currentIndex()
        app_config.save_user_settings()
        # print(f"Port changed to: {self.port_comboBox.currentText()} (Index: {app_config.last_selected_port})")

    def disconnect_port(self):
        """
        Stops the serial reader thread and closes the serial port connection.

        Also displays a message in the UI.
        """
        if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.output_UI_message("Disconnected from the serial port.")

    def refresh_ports(self):
        """
        Refreshes the list of available COM ports in the dropdown.

        Disconnects from the current port if connected, updates the UI, and repopulates the combo box.
        """
        if self.ser and self.ser.is_open:
            self.disconnect_port()
            self.ser = None
        self.output_UI_message("Refreshing COM ports...")
        self.get_com_ports()
        self.port_comboBox.clear()
        self.port_comboBox.addItems(com_ports.keys())

    def output_UI_message(self, message):
        """
        Displays a formatted UI message in the output text area and scrolls to the latest entry.

        Args:
            message (str): The message to display in the UI.
        """
        inChevons = "&gt;&gt;&gt;&gt;&gt;&gt;&gt;"
        outChevrons = "&lt;&lt;&lt;&lt;&lt;&lt;&lt;"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ui_message = f'<span style="color:green;">[{timestamp}] - {inChevons} UI Message Start {outChevrons} <br>{message}<br>{inChevons} UI Message End {outChevrons}</span>'
        self.output_text.append(ui_message)
        self.output_text.ensureCursorVisible()

    def output_Port_message(self, message):
        """
        Displays a formatted message received from the serial port in the output text area and scrolls to the latest entry.

        Args:
            message (str): The message received from the serial port.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ui_message = f'<span style="color:blue;">[{timestamp}] - {message}</span>'
        self.output_text.append(ui_message)
        self.output_text.ensureCursorVisible()

    def connect_port(self):
        """
        Connects to the selected COM port and starts the serial reader thread.

        Displays connection status or error messages in the UI.
        """
        selected_port = self.port_comboBox.currentText()
        port_info = com_ports.get(selected_port, None)

        if not selected_port:
            self.output_UI_message("No COM port selected.")
            return

        try:
            self.ser = serial.Serial(port_info.name, baudrate=BAUD_RATE, timeout=1)
            self.output_UI_message(f"Connected to {selected_port} at {BAUD_RATE} baud.")
            self.serial_thread = SerialReaderThread(self.ser, self.output_Port_message)
            self.serial_thread.start()
        except Exception as e:
            self.output_UI_message(f"Error connecting to {selected_port}: {str(e)}")

    def closeEvent(self, event):
        """
        Handles the window close event.

        Saves user settings and disconnects from the serial port before exiting.
        """
        app_config.save_user_settings()
        self.disconnect_port()
        self.datawindow.close() if hasattr(self, 'datawindow') else None




# Main Entry Point
def main():
    """
    Initializes and runs the serial monitor GUI application.

    - Creates the QApplication instance required for PyQt5.
    - Instantiates the MainWindow, which sets up the UI and logic.
    - Starts the application's event loop to handle user interaction.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Launch the application if this script is run directly
    main()

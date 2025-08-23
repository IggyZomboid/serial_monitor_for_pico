from PyQt5 import QtWidgets, uic, QtCore, QtGui
import serial
from serial.tools import list_ports
from datetime import datetime
from com_port.com_port import ComPort
from serial_reader.SerialReaderThread import SerialReaderThread
from .Data_View_Window import DataViewWindow

# Main Window Class
class MainWindow(QtWidgets.QMainWindow):
    """
    MainWindow Class

    This class represents the main window of the serial monitor application. It initializes the UI, sets up event handlers, and manages the application's main functionality.

    Attributes:
        shared_config (SharedConfig): Shared configuration object containing application-wide settings.
        serial_thread (Thread): Placeholder for the serial reader thread.
        port_comboBox (QtWidgets.QComboBox): Dropdown for selecting available COM ports.
        connect_button (QtWidgets.QPushButton): Button to connect to the selected COM port.
        refresh_ports_Button (QtWidgets.QPushButton): Button to refresh the list of available COM ports.
        clear_button (QtWidgets.QPushButton): Button to clear the output text area.
        data_view_button (QtWidgets.QPushButton): Button to open the data view window.
        output_text (QtWidgets.QTextEdit): Text area for displaying messages and logs.
        timer (QtCore.QTimer): Timer to periodically check for available COM ports.

    Methods:
        __init__(shared_config):
            Initializes the MainWindow, sets up the UI, and connects button actions to their handlers.

            - Loads the UI from the 'MainForm.ui' file.
            - Retrieves and initializes UI elements such as buttons, combo boxes, and text areas.
            - Sets up event handlers for button clicks and combo box changes.
            - Starts a timer to periodically check for available COM ports.

        port_changed():
            Updates the shared configuration when the selected port changes.

        refresh_ports():
            Refreshes the list of available COM ports in the dropdown.

        connect_port():
            Connects to the selected COM port.

        output_text.clear():
            Clears the output text area.

        data_view_button_clicked():
            Opens the data view window.

        get_com_ports(force_refresh=False):
            Retrieves the list of available COM ports. If force_refresh is True, refreshes the list.
    """
    def __init__(self, shared_config):
        """
        Initializes the MainWindow, sets up the UI, and connects button actions to their handlers.

        - Loads the UI from the 'MainForm.ui' file.
        - Retrieves and initializes UI elements such as buttons, combo boxes, and text areas.
        - Sets up event handlers for button clicks and combo box changes.
        - Starts a timer to periodically check for available COM ports.
        """
        super(MainWindow, self).__init__()
        uic.loadUi('UI/MainForm.ui', self)
        font = QtGui.QFont("Arial", 10)

        # Initialize shared configuration and serial thread
        self.shared_config = shared_config
        self.serial_thread = None  # Placeholder for the serial reader thread

        # Retrieve available COM ports
        self.get_com_ports()

        # Initialize UI elements
        self.port_comboBox = self.findChild(QtWidgets.QComboBox, 'port_comboBox')  
        # Set the combo box to the last selected port or default to the first item
        if self.port_comboBox.count() > self.shared_config.last_selected_port:
            self.port_comboBox.setCurrentIndex(self.shared_config.last_selected_port)
        else:
            self.port_comboBox.setCurrentIndex(0)

        self.connect_button = self.findChild(QtWidgets.QPushButton, 'connect_button')
        self.refresh_ports_Button = self.findChild(QtWidgets.QPushButton, 'refresh_ports_Button')
        self.clear_button = self.findChild(QtWidgets.QPushButton, 'clear_button')
        self.data_view_button = self.findChild(QtWidgets.QPushButton, 'data_view_button')
        self.output_text = self.findChild(QtWidgets.QTextEdit, 'output_text')

        # Set font for the output text area
        self.output_text.setFont(font)

        # Connect signals to their handlers
        self.port_comboBox.currentIndexChanged.connect(self.port_changed)
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
        self.datawindow = DataViewWindow(self.shared_config)
        
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
            new_port = ComPort(port)
            temp_com_ports[new_port.UIString] = new_port
            if not silent:
                portsfound += f"{new_port.UIString}<br>"
        if not silent:
            self.output_UI_message(f"Found {len(ports)} COM ports:<br>{portsfound}")
        if set(temp_com_ports.keys()) != set(self.shared_config.com_ports.keys()):
            
            # Only update if the list of ports has changed
            self.shared_config.com_ports.clear()
            self.shared_config.com_ports.update(temp_com_ports)
            # Block signals to avoid triggering events during updates
            self.port_comboBox.blockSignals(True)
            temp_selected_port = self.port_comboBox.currentText()  # Store the current port text
            self.port_comboBox.clear()  # Clear the current combo box items
            self.port_comboBox.addItems(self.shared_config.com_ports.keys()) 
            # Restore the last selected index
            if temp_selected_port in self.shared_config.com_ports.keys():
                temp_selected_index = list(self.shared_config.com_ports.keys()).index(temp_selected_port)
                self.port_comboBox.setCurrentIndex(temp_selected_index)
            else:
                self.port_comboBox.setCurrentIndex(0)
            self.port_comboBox.blockSignals(False)
            
    def port_changed(self):
        """
        Updates UserConfig with the newly selected COM port index and saves settings.

        Triggered when the user selects a different COM port from the dropdown.
        """

        self.shared_config.last_selected_port = self.port_comboBox.currentIndex()
        self.shared_config.app_config.save_user_last_port_settings()

    def disconnect_port(self):
        """
        Stops the serial reader thread and closes the serial port connection.

        Also displays a message in the UI.
        """
        if self.serial_thread and self.serial_thread.is_alive():
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
        self.port_comboBox.addItems(self.shared_config.com_ports.keys())

    def output_UI_message(self, message):
        """
        Displays a formatted UI message in the output text area and scrolls to the latest entry.

        Args:
            message (str): The message to display in the UI.
        """
        inChevons = "&gt;&gt;&gt;&gt;&gt;&gt;&gt;"
        outChevrons = "&lt;&lt;&lt;&lt;&lt;&lt;&lt;"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}]")  # Print to console for debugging
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
        port_info = self.shared_config.com_ports.get(selected_port, None)

        if port_info:
            self.output_UI_message(f"Port Info:\nDevice: {port_info.device}\nName: {port_info.name}\nDescription: {port_info.description}\n"
                       f"HWID: {port_info.hwid}\nVID: {port_info.vid}\nPID: {port_info.pid}\nSerial Number: {port_info.serial_number}\n"
                       f"Location: {port_info.location}\nManufacturer: {port_info.manufacturer}\nProduct: {port_info.product}\n"
                       f"Interface: {port_info.interface}")
        
        if not selected_port:
            self.output_UI_message("No COM port selected.")
            return

        try:
            self.ser = serial.Serial(port_info.name, baudrate=self.shared_config.BAUD_RATE, timeout=1)
            self.output_UI_message(f"Connected to {selected_port} at {self.shared_config.BAUD_RATE} baud.")
            self.serial_thread = SerialReaderThread(self.shared_config, self.ser, self.output_Port_message)
            self.serial_thread.start()
        except Exception as e:
            self.output_UI_message(f"Error connecting to {selected_port}: {str(e)}")

    def closeEvent(self, event):
        """
        Handles the window close event.

        Saves user settings and disconnects from the serial port before exiting.
        """
        self.shared_config.app_config.save_user_last_port_settings()
        self.disconnect_port()
        self.datawindow.close() if hasattr(self, 'datawindow') else None

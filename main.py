"""
Main Application Entry Point

This script initializes and runs the serial monitor GUI application. It sets up the shared configuration, the main window, and starts the application's event loop.

Classes:
    SharedConfig:
        A centralized class for storing application-wide settings and shared objects.

Functions:
    main():
        Initializes the application and starts the event loop.

Attributes:
    shared_config (SharedConfig): Instance of SharedConfig used to share data across components.
"""

import sys
from PyQt5 import QtGui, QtWidgets
from app_config import UserConfig
from views.Main_Window import MainWindow
from table_model.table_model import tracked_data_table_model

# Shared Configuration Class
class SharedConfig:
    """
    SharedConfig Class

    This class provides a centralized location for storing shared data such as the baud rate,
    COM port information, and application configuration. It is passed to various components
    of the application to ensure consistent access to shared resources.

    Attributes:
        BAUD_RATE (int): Default baud rate for serial communication.
        date_queue_dict (dict): Dictionary for storing timestamped serial data.
        app_config (UserConfig): Instance of the UserConfig class for managing user settings.
        com_ports (dict): Dictionary for storing available COM ports and their details.
        dataPointNames (list): List to store names of data points.
        last_selected_port (int): Index of the last selected COM port.
        tracked_data_table_model (tracked_data_table_model): Table model for tracking data points.
    """
    def __init__(self):
        """
        Initializes the SharedConfig instance.

        - Sets default values for baud rate, COM ports, and other shared settings.
        - Creates an instance of UserConfig for managing user-specific settings.
        - Initializes the tracked data table model for storing and visualizing data points.
        """
        self.BAUD_RATE = 115200  # Default baud rate
        self.date_queue_dict = {}  # Dictionary for timestamped serial data        
        self.com_ports = {}  # Dictionary for available COM ports
        self.dataPointNames = []  # List to store names of data points
        self.last_selected_port = 0  # Last selected COM port index
        self.app_config = UserConfig(self)  # User configuration instance
        self.tracked_data_table_model = tracked_data_table_model()  # Table model for tracking data points

# Create a shared configuration instance
shared_config = SharedConfig()

# Main Entry Point
def main():
    """
    Initializes and runs the serial monitor GUI application.

    - Creates the QApplication instance required for PyQt5.
    - Instantiates the MainWindow, which sets up the UI and logic.
    - Starts the application's event loop to handle user interaction.
    """
    app = QtWidgets.QApplication(sys.argv)  # Create the PyQt5 application instance
    window = MainWindow(shared_config)  # Instantiate the main window with shared configuration
    sys.exit(app.exec_())  # Start the application's event loop

if __name__ == "__main__":
    # Launch the application if this script is run directly
    main()

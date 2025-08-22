import sys
from PyQt5 import QtWidgets
from app_config import UserConfig
from views.Main_Window import MainWindow

# Shared Configuration Class
class SharedConfig:
    """
    SharedConfig is a class that holds application-wide settings and shared objects.

    This class provides a centralized location for storing shared data such as the baud rate,
    COM port information, and application configuration. It is passed to various components
    of the application to ensure consistent access to shared resources.

    Attributes:
        BAUD_RATE (int): Default baud rate for serial communication.
        date_queue_dict (dict): Dictionary for storing timestamped serial data.
        app_config (UserConfig): Instance of the UserConfig class for managing user settings.
        com_ports (dict): Dictionary for storing available COM ports and their details.
    """
    def __init__(self):
        self.BAUD_RATE = 115200  # Default baud rate
        self.date_queue_dict = {}  # Dictionary for timestamped serial data
        self.app_config = UserConfig()  # User configuration instance
        self.com_ports = {}  # Dictionary for available COM ports

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

# Import necessary modules
import configparser

# User Configuration Class
class UserConfig:
    """
    UserConfig is a class that manages user-specific settings for the serial monitor application.

    This class provides functionality to store, retrieve, and update user settings such as the last selected
    COM port, baud rate, and other preferences. It interacts with a configuration file to persist these settings
    across sessions.

    Attributes:
        config_file (str): Path to the configuration file used to store user settings.
        last_selected_port (int): Index of the last selected COM port.
        baud_rate (int): Baud rate for serial communication.
        other_settings (dict): Additional user-specific settings.

    Methods:
        __init__():
            Initializes the UserConfig instance and loads settings from the configuration file.
        save_user_settings():
            Saves the current user settings to the configuration file.
        load_user_settings():
            Loads user settings from the configuration file.
        update_setting(key, value):
            Updates a specific setting and saves it to the configuration file.
    """
    def __init__(self):
        """
        Initializes the UserConfig instance and loads settings from the configuration file.

        - Sets default values for user settings.
        - Attempts to load settings from the configuration file.
        """
        self.config_file = "settings.ini"  # Path to the configuration file
        self.last_selected_port = 0  # Default index for the last selected COM port
        self.baud_rate = 115200  # Default baud rate for serial communication
        self.other_settings = {}  # Dictionary for additional settings
        self.load_user_settings()

    def save_user_settings(self):
        """
        Saves the current user settings to the configuration file.

        - Writes settings such as last selected port and baud rate to the file.
        - Ensures settings are persisted across application sessions.
        """
        # Example implementation for saving settings
        pass

    def load_user_settings(self):
        """
        Loads user settings from the configuration file.

        - Reads settings such as last selected port and baud rate from the file.
        - Updates the instance attributes with the loaded values.
        """
        # Example implementation for loading settings
        pass

    def update_setting(self, key, value):
        """
        Updates a specific setting and saves it to the configuration file.

        Args:
            key (str): The name of the setting to update.
            value: The new value for the setting.

        - Updates the setting in memory.
        - Saves the updated setting to the configuration file.
        """
        self.other_settings[key] = value
        self.save_user_settings()
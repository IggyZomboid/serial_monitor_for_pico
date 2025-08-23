# Import necessary modules
import configparser

# User Configuration Class
class UserConfig:
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

    def __init__(self, shared_config):
        """
        Initializes the AppConfig instance.

        This method reads the configuration file 'settings.ini' and loads user settings.
        If the file or specific settings are not present, it sets default values.
        """
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        
        self.shared_config = shared_config  # Store the shared configuration instance
        
        if 'user_settings' in self.config:
            # Convert values to integers where necessary
            self.shared_config.last_selected_port = int(self.config['user_settings'].get('selected_port', 0))
            print(f"Last selected port: {self.shared_config.last_selected_port}")
            data_point_names = self.config['user_settings'].get('data_point_names', '')
            if data_point_names:
                self.shared_config.dataPointNames = data_point_names.split(',')
            else:
                print("No data point names found in settings, initializing empty list.")

    
    def save_user_last_port_settings(self):
        """
        Saves the current user settings to 'settings.ini'.

        This method updates the configuration file with the latest user settings,
        ensuring that all values are converted to strings before saving.
        """
        print("Saving user settings...")  # Debug statement

        if 'user_settings' not in self.config:
            self.config['user_settings'] = {}

        # Convert all values to strings before saving
        self.config['user_settings']['selected_port'] = str(self.shared_config.last_selected_port)
        self.config['user_settings']['data_point_names'] = ','.join(self.shared_config.dataPointNames)
        # Debug print to verify the values being saved
        print("Config to save:", dict(self.config['user_settings']))

        # Write the settings to the file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        print("Settings saved!") 
    
    def save_data_point_names_settings(self):
        """
        Saves the current user settings to 'settings.ini'.

        This method updates the configuration file with the latest user settings,
        ensuring that all values are converted to strings before saving.
        """
        print("Saving user settings...")  # Debug statement

        if 'user_settings' not in self.config:
            self.config['user_settings'] = {}

        # Convert all values to strings before saving
        self.config['user_settings']['data_point_names'] = ','.join(self.shared_config.dataPointNames)
        # Debug print to verify the values being saved
        print("Config to save:", dict(self.config['user_settings']))

        # Write the settings to the file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        print("Settings saved!") 
    
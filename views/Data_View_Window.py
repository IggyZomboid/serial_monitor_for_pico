import re
from PyQt5 import QtWidgets, uic

# Data View Window Class
class DataViewWindow(QtWidgets.QMainWindow):
    """
    DataViewWindow is a secondary GUI class for the serial monitor application. It provides
    advanced data visualization capabilities for incoming serial data.

    Attributes:
        shared_config (SharedConfig): Shared configuration object containing application-wide settings.
        input_name_text (QtWidgets.QPlainTextEdit): Text area for entering a name or label for the data.
        preview_txt_label (QtWidgets.QLabel): Label for previewing formatted text based on user input.

    Methods:
        __init__(shared_config):
            Initializes the DataViewWindow, sets up the UI, and connects UI elements to their handlers.
        validateNameText():
            Validates the text entered in the input_name_text field and updates the preview label.
    """
    def __init__(self, shared_config):
        """
        Initializes the DataViewWindow, sets up the UI, and connects UI elements to their handlers.

        - Loads the UI from the 'Data_view_window.ui' file.
        - Retrieves and initializes UI elements such as text areas and labels.
        - Sets up event handlers for user input validation.
        """
        super(DataViewWindow, self).__init__()
        uic.loadUi('UI/Data_view_window.ui', self)
        self.shared_config = shared_config
        self.sanitized_text = ''
        
        # Get UI elements
        self.input_name_text = self.findChild(QtWidgets.QPlainTextEdit, 'input_name_text')
        self.preview_txt_label = self.findChild(QtWidgets.QLabel, 'preview_txt_label')
        self.input_name_text.textChanged.connect(self.validateNameText)
        self.add_name_button = self.findChild(QtWidgets.QPushButton, 'add_name_button')
        self.add_name_button.clicked.connect(self.addDataPoint)
        self.show()

    def validateNameText(self):
        """
        Validates the text entered in the input_name_text field and updates the preview label.

        - Ensures the text is not empty.
        - Updates the preview_txt_label with the formatted text.
        """
        print("Validating input name text...")
        print(f"Current text: {self.input_name_text.toPlainText()}")
        if not self.input_name_text.toPlainText():
            print("Input name text is empty, setting to 'Default Name'.")
            self.input_name_text.setPlainText('Default Name')
        else:
            print("Input name text is not empty, proceeding with sanitization.")
        # Replace spaces with underscores first
        self.sanitized_text = self.input_name_text.toPlainText().replace(' ', '_')
        print("Replacing spaces with underscores in input name text...")
        
        # Remove any character that is not alphanumeric, underscore, or hyphen
        self.sanitized_text = re.sub(r'[^a-zA-Z0-9_-]', '', self.sanitized_text)
        if self.sanitized_text != self.input_name_text.toPlainText():
            print(f"Sanitized text: {self.sanitized_text}")
        
        self.preview_txt_label.setText(self.sanitized_text)
        
        print(self.sanitized_text)
    
    def addDataPoint(self):
        
        if not self.sanitized_text:
            print("No valid data point name provided.")
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid Data Point",
                "Please provide a valid name for the data point before proceeding."
            )
            return
        else:
            print(f"Adding data point: {self.sanitized_text}")
            

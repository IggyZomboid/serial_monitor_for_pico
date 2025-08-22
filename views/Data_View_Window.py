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

        # Get UI elements
        self.input_name_text = self.findChild(QtWidgets.QPlainTextEdit, 'input_name_text')
        self.preview_txt_label = self.findChild(QtWidgets.QLabel, 'preview_txt_label')

        # Connect text change event to validation method
        self.input_name_text.textChanged.connect(self.validateNameText)

    def validateNameText(self):
        """
        Validates the text entered in the input_name_text field and updates the preview label.

        - Ensures the text is not empty.
        - Updates the preview_txt_label with the formatted text.
        """
        if not self.input_name_text.toPlainText():
            self.preview_txt_label.setText("Default Name")
        else:
            self.preview_txt_label.setText(self.input_name_text.toPlainText())

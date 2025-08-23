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
        self.dataPointName_listWidget = self.findChild(QtWidgets.QListWidget, 'dataPointName_listWidget')
        self.clear_names_button = self.findChild(QtWidgets.QPushButton, 'clear_names_button')
        self.add_name_button = self.findChild(QtWidgets.QPushButton, 'add_name_button')
        self.data_tableView = self.findChild(QtWidgets.QTableView, 'data_tableView')
        self.auto_scroll_checkBox = self.findChild(QtWidgets.QCheckBox, 'auto_scroll_checkBox')
        self.save_data_pushButton = self.findChild(QtWidgets.QPushButton, 'save_data_pushButton')
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')
        
        self.save_data_pushButton.clicked.connect(self.save_data_pushButton_clicked)
        self.input_name_text.textChanged.connect(self.validateNameText)
        self.add_name_button.clicked.connect(self.addDataPointName)
        self.dataPointName_listWidget.clicked.connect(
            lambda: self.clickToDeleteDatapointName(self.dataPointName_listWidget.currentItem())
        )
        self.clear_names_button.clicked.connect(self.clearDataPointNames)
        self.data_tableView.setModel(self.shared_config.tracked_data_table_model)
        self.data_tableView.verticalScrollBar().actionTriggered.connect(self.disableAutoScroll)
        self.data_tableView.verticalScrollBar().valueChanged.connect(self.isScrolledToBottom)
        self.shared_config.tracked_data_table_model.setView(self)
        self.shared_config.tracked_data_table_model.dataChanged.connect(lambda: self.data_tableView.resizeColumnToContents(0))
        self.tabWidget.setCurrentIndex(0)  # Set the first tab as the current tab
        self.show()
        
        self.resetDataPointNames()

    def clickToDeleteDatapointName(self, item):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{item.text()}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            if item.text() in self.shared_config.dataPointNames:
                removedItem = item.text()
                self.shared_config.dataPointNames.remove(removedItem)
                self.resetDataPointNames()
                # if item.text() is a key in date_queue_dict, remove it
                if removedItem in self.shared_config.date_queue_dict:
                    print(f"Removing '{removedItem}' from date_queue_dict")
                    del self.shared_config.date_queue_dict[removedItem]
            
    def validateNameText(self):
        """
        Validates the text entered in the input_name_text field and updates the preview label.

        - Ensures the text is not empty.
        - Updates the preview_txt_label with the formatted text.
        """
        # Replace spaces with underscores first
        self.sanitized_text = self.input_name_text.toPlainText().replace(' ', '_')
        
        # Remove any character that is not alphanumeric, underscore, or hyphen
        self.sanitized_text = re.sub(r'[^a-zA-Z0-9_-]', '', self.sanitized_text)
        self.preview_txt_label.setText(self.sanitized_text)
        
    def addDataPointName(self):
        """
        Adds a new data point name to the list of data points.

        Args:
            data_point_name (str): The name of the data point to be added.
        """
        if self.sanitized_text not in self.shared_config.dataPointNames:
            self.shared_config.dataPointNames.append(self.sanitized_text)
            self.resetDataPointNames()
            self.input_name_text.clear()
            self.preview_txt_label.clear()
            self.sanitized_text = ''
        elif self.sanitized_text != '':
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid Data Point",
                f"Data point '{self.sanitized_text}' already exists."
            )
   
    def clearDataPointNames(self):
        """
        Clears all data point names from the list.
        """
        self.shared_config.dataPointNames.clear()
        self.dataPointName_listWidget.clear()
                
    def resetDataPointNames(self):
        """
        Resets the list of data point names to an empty state.

        Returns:
            str: A message indicating that the data points have been reset.
        """
        self.dataPointName_listWidget.clear()
        count = len(self.shared_config.dataPointNames)
        if count != 0:
            self.dataPointName_listWidget.addItems(self.shared_config.dataPointNames)
        
    def closeEvent(self, event):
        """
        Handles the window close event.

        Saves user settings and disconnects from the serial port before exiting.
        """
        self.shared_config.app_config.save_user_last_port_settings()
        
    def autoScroll(self):
        """
        Automatically scrolls the data table view to the bottom.

        This method is called when new data is added to ensure the latest data is visible.
        """
        if self.auto_scroll_checkBox.isChecked():
            print("Auto-scrolling to bottom of data table view.")
            self.data_tableView.scrollToBottom()

    def disableAutoScroll(self):
        """
        Disables the auto-scroll checkbox when the scroll bar is manually triggered.
        """
        if not self.isScrolledToBottom():
            print("Scroll bar is at the bottom, enabling auto-scroll.")
            self.auto_scroll_checkBox.setChecked(False)
        

    def save_data_pushButton_clicked(self):
        """
        Handles the save data button click event.

        Saves the current data in the table view to a file.
        """
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self.shared_config.tracked_data_table_model.saveDataToFile(file_name)
            QtWidgets.QMessageBox.information(self, "Save Data", f"Data saved to {file_name}")
            
    def isScrolledToBottom(self):
        """
        Checks if the data_tableView is scrolled to the bottom.

        Returns:
            bool: True if the scroll bar is at the bottom, False otherwise.
        """
        vertical_scroll_bar = self.data_tableView.verticalScrollBar()
        if vertical_scroll_bar.value() == vertical_scroll_bar.maximum():
            self.auto_scroll_checkBox.setChecked(True)
            return True
        else:
            return False
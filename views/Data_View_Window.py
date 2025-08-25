import re
from PyQt5 import QtWidgets, uic
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QPainter

# Data View Window Class
class DataViewWindow(QtWidgets.QMainWindow):
    """
    DataViewWindow Class

    This class represents the secondary window for advanced data visualization in the serial monitor application. It provides functionality for viewing, saving, and interacting with tabular data.

    Attributes:
        shared_config (SharedConfig): Shared configuration object containing application-wide settings.
        data_tableView (QtWidgets.QTableView): Table view for displaying tabular data.
        auto_scroll_checkBox (QtWidgets.QCheckBox): Checkbox to enable or disable auto-scrolling.
        save_data_pushButton (QtWidgets.QPushButton): Button to save the current data to a file.

    Methods:
        autoScroll():
            Automatically scrolls the data_tableView to the bottom if auto-scroll is enabled.

        disableAutoScroll():
            Disables the auto-scroll checkbox when the scroll bar is manually triggered.

        save_data_pushButton_clicked():
            Handles the save data button click event and saves the current data in the table view to a file.

        isScrolledToBottom():
            Checks if the data_tableView is scrolled to the bottom.

            Returns:
                bool: True if the scroll bar is at the bottom, False otherwise.
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
        self.Data_Points_comboBox = self.findChild(QtWidgets.QComboBox, 'Data_Points_comboBox')
        self.container = self.findChild(QtWidgets.QWidget, "chart_placeholder_widget")
        
        # make a chart widget
        self.chart = QChart()
        self.chart.setTitle("Data Visualization")
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.chart_view.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.chart_view)
        
        self.populateChartFromTableModel()
        
        
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
        self.shared_config.tracked_data_table_model.dataChanged.connect(lambda: (
            self.data_tableView.resizeColumnToContents(0),
            self.populateChartFromTableModel()
        ))
        self.shared_config.tracked_data_table_model.chartDataUpdated.connect(self.populateChartFromTableModel)
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

        Clears the dataPointName_listWidget and Data_Points_comboBox then repopulates them with the current data point names from shared_config.
        """
        self.dataPointName_listWidget.clear()
        self.Data_Points_comboBox.clear()
        count = len(self.shared_config.dataPointNames)
        if count != 0:
            self.dataPointName_listWidget.addItems(self.shared_config.dataPointNames)
            self.Data_Points_comboBox.addItems(self.shared_config.dataPointNames)
        
    def closeEvent(self, event):
        """
        Handles the window close event.

        Saves user settings and disconnects from the serial port before exiting.
        """
        self.shared_config.app_config.save_user_last_port_settings()
        

    def autoScroll(self):
        """
        Automatically scrolls the data_tableView to the bottom.

        This method is called when new data is added to ensure the latest data is visible.
        """
        if self.auto_scroll_checkBox.isChecked():
            print("Auto-scrolling to bottom of data table view.")
            self.data_tableView.scrollToBottom()

    def disableAutoScroll(self):
        """
        Disables the auto-scroll checkbox when the scroll bar is manually triggered.

        If the scroll bar is not at the bottom, auto-scroll is disabled.
        """
        if not self.isScrolledToBottom():
            print("Scroll bar is at the bottom, enabling auto-scroll.")
            self.auto_scroll_checkBox.setChecked(False)

    def save_data_pushButton_clicked(self):
        """
        Handles the save data button click event.

        Opens a file dialog to select the save location and saves the current data in the table view to a CSV file.
        Displays a confirmation message upon successful save.
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
    
   
    def populateChartFromTableModel(self, visible_range=10):
        """
        Populates the chart using data from the table model.

        - Uses the 'Timestamp' column as the X-axis.
        - Plots each other column as a separate line series on the chart.
        - Makes the chart scrollable by showing only the last `visible_range` values.
        - Displays timestamps as human-readable date and time on the X-axis.

        Args:
            visible_range (int): The number of recent values to display on the chart.
        """
        # Clear existing series from the chart
        self.chart.removeAllSeries()

        # Get the table model
        model = self.shared_config.tracked_data_table_model

        # Ensure the model has data
        if len(model._rows) == 0 or len(model._headers) < 2:
            print("No data available in the table model to populate the chart.")
            return

        # Find the index of the 'Timestamp' column
        try:
            timestamp_index = model._headers.index("Timestamp")
        except ValueError:
            print("'Timestamp' column not found in the table model.")
            return

        print(f"Headers: {model._headers}")
        print(f"Timestamp Index: {timestamp_index}")

        # Iterate through the columns (excluding the 'Timestamp' column)
        for column_index in range(len(model._headers)):
            if column_index == timestamp_index:
                continue  # Skip the 'Timestamp' column

            # Create a new line series for the current column
            series = QLineSeries()
            series.setName(model._headers[column_index])  # Use the column header as the series name

            # Populate the series with data
            timestamps = []
            values = []
            for row_index, row in enumerate(model._rows):
                print(f"Row Count: {len(model._rows)}, Current Row Index: {row_index}")
                timestamp = row[timestamp_index]
                value = row[column_index]

                # Ensure both timestamp and value are valid
                if timestamp is not None and value is not None:
                    try:
                        timeVal = QDateTime.fromString(timestamp, "yyyy-MM-dd HH:mm:ss.zzz").toMSecsSinceEpoch()
                        timestamps.append(timeVal)
                        values.append(float(value))
                        series.append(timeVal, float(value))
                    except ValueError as e:
                        print(f"Error processing data at row {row_index}, column {column_index}: {timestamp}, {value}. Exception: {e}")

            # Add the series to the chart
            self.chart.addSeries(series)

        # Create default axes based on the series data
        self.chart.createDefaultAxes()

        # Replace the default X-axis with a QDateTimeAxis for human-readable timestamps
        axisX = QDateTimeAxis()
        axisX.setTitleText("Timestamp")
        axisX.setFormat("yyyy-MM-dd HH:mm:ss")  # Format for displaying date and time
        axisX.setTickCount(visible_range + 1)

        # Set the range to show only the last `visible_range` values
        if len(timestamps) > visible_range:
            axisX.setRange(QDateTime.fromMSecsSinceEpoch(timestamps[-visible_range]), QDateTime.fromMSecsSinceEpoch(timestamps[-1]))
        else:
            axisX.setRange(QDateTime.fromMSecsSinceEpoch(timestamps[0]), QDateTime.fromMSecsSinceEpoch(timestamps[-1]))

        self.chart.setAxisX(axisX)

        # Rotate the labels by 45 degrees
        axisX.setLabelsAngle(45)  # You can adjust the angle as needed

        # Optionally set Y-axis titles
        self.chart.axisY().setTitleText("Values")

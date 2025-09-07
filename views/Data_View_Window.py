import re
from PyQt5 import QtWidgets, uic
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt, QDateTime, QTimer
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

        # Scroll controls (from your UI)
        self.scroll_back_button = self.findChild(QtWidgets.QPushButton, 'Scroll_back_button')
        self.scroll_forward_button = self.findChild(QtWidgets.QPushButton, 'Scroll_forward_button')

        # --- Chart + view
        self.chart = QChart()
        self.chart.setTitle("Data Visualization")
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.chart_view.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.chart_view)

        # --- Live window + scroll state ---
        self.window_duration_ms = 30_000       # 30 seconds visible window
        self.scroll_step_ms = 5_000            # 5 second step per click
        self.window_end_ms = QDateTime.currentMSecsSinceEpoch()
        self.user_scrolled = False             # if True, pause "follow live"

        # --- Axes (create once, reuse) ---
        self.axisX = QDateTimeAxis()
        self.axisX.setTitleText("Timestamp")
        self.axisX.setFormat("yyyy-MM-dd HH:mm:ss")
        self.axisX.setTickCount(11)
        self.axisX.setLabelsAngle(45)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Values")
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        # --- Wire up UI events
        self.save_data_pushButton.clicked.connect(self.save_data_pushButton_clicked)
        self.input_name_text.textChanged.connect(self.validateNameText)
        self.add_name_button.clicked.connect(self.addDataPointName)
        self.dataPointName_listWidget.clicked.connect(
            lambda: self.clickToDeleteDatapointName(self.dataPointName_listWidget.currentItem())
        )
        self.clear_names_button.clicked.connect(self.clearDataPointNames)

        if self.scroll_back_button:
            self.scroll_back_button.clicked.connect(self.on_scroll_back)
        if self.scroll_forward_button:
            self.scroll_forward_button.clicked.connect(self.on_scroll_forward)

        # Table model hookup
        self.data_tableView.setModel(self.shared_config.tracked_data_table_model)
        self.data_tableView.verticalScrollBar().actionTriggered.connect(self.disableAutoScroll)
        self.data_tableView.verticalScrollBar().valueChanged.connect(self.isScrolledToBottom)
        self.shared_config.tracked_data_table_model.setView(self)

        # When data changes, we can resize columns and (optionally) snap to live if user hasn't scrolled
        self.shared_config.tracked_data_table_model.dataChanged.connect(lambda: (
            self.data_tableView.resizeColumnToContents(0),
            self.snap_to_live_if_needed()
        ))
        self.shared_config.tracked_data_table_model.chartDataUpdated.connect(self.snap_to_live_if_needed)

        self.tabWidget.setCurrentIndex(0)  # Set the first tab as the current tab
        self.show()

        self.resetDataPointNames()

        # --- 500 ms refresh timer (updates even with no data) ---
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.refreshChart)
        self.update_timer.start()

    # ---------- Basic UI helpers ----------

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
        """
        # Replace spaces with underscores first
        self.sanitized_text = self.input_name_text.toPlainText().replace(' ', '_')
        # Remove any character that is not alphanumeric, underscore, or hyphen
        self.sanitized_text = re.sub(r'[^a-zA-Z0-9_-]', '', self.sanitized_text)
        self.preview_txt_label.setText(self.sanitized_text)

    def addDataPointName(self):
        """
        Adds a new data point name to the list of data points.
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
        Repopulates the names list and combo from shared_config.
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
        """
        self.shared_config.app_config.save_user_last_port_settings()

    def autoScroll(self):
        """
        Automatically scrolls the data_tableView to the bottom.
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
        Save the current data in the table view to a CSV file.
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
        """
        vertical_scroll_bar = self.data_tableView.verticalScrollBar()
        if vertical_scroll_bar.value() == vertical_scroll_bar.maximum():
            self.auto_scroll_checkBox.setChecked(True)
            return True
        else:
            return False

    # ---------- Chart building + live refresh ----------

    def buildSeriesFromModel(self):
        """
        Rebuilds all series from the table model rows.
        Does NOT create axes. Callers must attach axes after adding series.
        Returns the list of all timestamps (ms since epoch) encountered (sorted).
        """
        self.chart.removeAllSeries()
        model = self.shared_config.tracked_data_table_model

        if len(model._rows) == 0 or len(model._headers) < 2:
            # Still keep axes; no series present
            return []

        # Find the index of the 'Timestamp' column
        try:
            timestamp_index = model._headers.index("Timestamp")
        except ValueError:
            # No timestamp column, cannot plot
            return []

        all_ts = []

        # For each non-Timestamp column, build a line series
        for column_index in range(len(model._headers)):
            if column_index == timestamp_index:
                continue  # Skip the 'Timestamp' column

            series = QLineSeries()
            series.setName(model._headers[column_index])  # Use the column header as the series name

            for row in model._rows:
                timestamp = row[timestamp_index]
                value = row[column_index]
                if timestamp is None or value is None:
                    continue

                # Prefer "yyyy-MM-dd HH:mm:ss.zzz" but also allow without .zzz
                t_ms = QDateTime.fromString(timestamp, "yyyy-MM-dd HH:mm:ss.zzz").toMSecsSinceEpoch()
                if t_ms == 0:
                    t_ms = QDateTime.fromString(timestamp, "yyyy-MM-dd HH:mm:ss").toMSecsSinceEpoch()

                if t_ms > 0:
                    try:
                        v = float(value)
                        series.append(t_ms, v)
                        all_ts.append(t_ms)
                    except Exception:
                        # Non-numeric value; skip
                        pass

            self.chart.addSeries(series)

        # Attach all series to shared axes
        for s in self.chart.series():
            s.attachAxis(self.axisX)
            s.attachAxis(self.axisY)

        all_ts.sort()
        return all_ts

    def refreshChart(self):
        """
        Called by timer every 500 ms.
        - Rebuilds series from the model
        - Advances or holds window end depending on whether user scrolled
        - Updates axis ranges even when there is no data
        """
        timestamps = self.buildSeriesFromModel()

        # Choose a reference "latest" time: last data timestamp or 'now' if no data
        now_ms = QDateTime.currentMSecsSinceEpoch()
        latest_ms = timestamps[-1] if timestamps else now_ms

        # If user hasn't scrolled back, follow live
        if not self.user_scrolled:
            # Follow either the latest data point or the wall clock, whichever is greater
            self.window_end_ms = max(self.window_end_ms, latest_ms, now_ms)

        # Compute window start
        window_start_ms = self.window_end_ms - self.window_duration_ms
        if window_start_ms > self.window_end_ms:
            window_start_ms = self.window_end_ms  # guard

        # Apply range to X axis (updates even with no data)
        self.axisX.setRange(
            QDateTime.fromMSecsSinceEpoch(window_start_ms),
            QDateTime.fromMSecsSinceEpoch(self.window_end_ms),
        )

        # Keep a reasonable Y range (auto from visible points, or default)
        self.updateYAxisRange()

    def updateYAxisRange(self):
        """
        Simple auto-range for Y based on visible points. If no data, default 0..1.
        """
        ymin, ymax = None, None
        x_min = self.axisX.min().toMSecsSinceEpoch()
        x_max = self.axisX.max().toMSecsSinceEpoch()

        for s in self.chart.series():
            # Iterate points to find those within current X window
            for p in s.points():
                t_ms = int(p.x())
                if x_min <= t_ms <= x_max:
                    y = p.y()
                    ymin = y if ymin is None else min(ymin, y)
                    ymax = y if ymax is None else max(ymax, y)

        if ymin is None or ymax is None or ymin == ymax:
            ymin, ymax = 0.0, 1.0
        else:
            pad = (ymax - ymin) * 0.1 if (ymax - ymin) > 0 else 0.5
            ymin -= pad
            ymax += pad

        self.axisY.setRange(ymin, ymax)

    def snap_to_live_if_needed(self):
        """
        Called on data changes to optionally resume live-follow if the user hasn't scrolled,
        or to keep the live window aligned with newest data.
        """
        if not self.user_scrolled:
            self.window_end_ms = max(self.window_end_ms, QDateTime.currentMSecsSinceEpoch())
        # Let the timer handle the actual refresh cadence

    # ---------- Scroll button handlers ----------

    def on_scroll_back(self):
        """
        User moves window left and pauses live-follow.
        """
        self.user_scrolled = True
        self.window_end_ms -= self.scroll_step_ms
        self.refreshChart()

    def on_scroll_forward(self):
        """
        Move window right. If we reach/past 'now', resume live-follow.
        """
        now_ms = QDateTime.currentMSecsSinceEpoch()
        self.window_end_ms += self.scroll_step_ms

        # If we've caught up to "live", resume following
        if self.window_end_ms >= now_ms:
            self.user_scrolled = False
            self.window_end_ms = now_ms

        self.refreshChart()

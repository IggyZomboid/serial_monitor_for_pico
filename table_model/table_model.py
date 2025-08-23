from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QPersistentModelIndex
import csv

class tracked_data_table_model(QAbstractTableModel):
    """
    A custom table model for tracking and displaying data points in a tabular format.

    This model is designed to work with a QTableView and provides functionality for dynamically
    adding headers, rows, and updating data. It also supports saving the data to a CSV file.

    Attributes:
        data (list): A list of lists representing the rows and columns of the table.
        headers (list): A list of strings representing the column headers.
        view (QTableView or None): A reference to the view using this model, allowing callbacks.

    Methods:
        setView(view):
            Sets the view that will use this model.

        rowCount(parent=None):
            Returns the number of rows in the model.

        columnCount(parent=None):
            Returns the number of columns in the model.

        data(index, role=Qt.DisplayRole):
            Returns the data for a specific cell in the model.

        headerData(section, orientation, role=Qt.DisplayRole):
            Returns the header data for a specific row or column.

        addHeader(new_header):
            Dynamically adds a new header and updates the model.
    """
    def __init__(self):
        """
        Initializes the tracked_data_table_model instance.

        - Sets up an empty data structure for rows and columns.
        - Adds a default header for timestamps.
        """
        super(tracked_data_table_model, self).__init__()
        self.data = []  # Initialize an empty list for rows
        self.headers = []  # Initialize an empty list for column headers
        self.addHeader("Timestamp")  # Add a default header for timestamps
        self.view = None  # Placeholder for the view using this model

    def setView(self, view):
        """
        Sets the view that will use this model.

        Args:
            view (QTableView): The view that will use this model.

        This allows the model to notify the view about changes, such as auto-scrolling.
        """
        self.view = view

    def rowCount(self, parent=None):
        """
        Returns the number of rows in the model.

        Args:
            parent (QModelIndex or None): Required by PyQt5 but not used here.

        Returns:
            int: The number of rows in the data.
        """
        return len(self.data)

    def columnCount(self, parent=None):
        """
        Returns the number of columns in the model.

        Args:
            parent (QModelIndex or None): Required by PyQt5 but not used here.

        Returns:
            int: The number of columns in the headers.
        """
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for a specific cell in the model.

        Args:
            index (QModelIndex): The index of the cell.
            role (int): The role for which data is requested (e.g., display role).

        Returns:
            Any: The data for the cell, or None if the role is not Qt.DisplayRole.
        """
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns the header data for a specific row or column.

        Args:
            section (int): The index of the row or column.
            orientation (Qt.Orientation): The orientation (horizontal or vertical).
            role (int): The role for which data is requested (e.g., display role).

        Returns:
            str: The header data for the specified section and orientation.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]  # Return column headers
            else:
                return f"Row {section + 1}"  # Return row numbers as strings
        return None

    def addHeader(self, new_header):
        """
        Dynamically adds a new header and updates the model.

        Args:
            new_header (str): The name of the new header to add.

        - Appends the new header to the headers list.
        - Updates existing rows to include the new column.
        - Emits signals to notify the view about the change.
        """
        print(f"Adding new header: {new_header}")
        try:
            self.headers.append(new_header)
            newColumn = self.columnCount()
            self.beginInsertColumns(QModelIndex(), newColumn, newColumn)
            # update existing data to include the new column
            for row in self.data:
                row.append(None)
            self.endInsertColumns()
            
        except Exception as e:
            print(f"Error adding header: {e}")
        

    def addRow(self, time_stamp, data_point_name, data_value):
        """
        Updates a row with the matching timestamp or adds a new row if no match exists.

        Args:
            time_stamp (str): The timestamp to search for.
            data_point_name (str): The column name to update or add.
            data_value (any): The value to set in the column.
        """
        print(f"Adding/updating row with timestamp: {time_stamp}, data point: {data_point_name}, value: {data_value}")
        
        # Ensure the data_point_name exists in the headers
        if data_point_name not in self.headers:
            print(f"Header '{data_point_name}' not found, adding it.")
            self.addHeader(data_point_name)

        print(f"Current headers: {self.headers}")
        # Search for a row with the matching timestamp
        for row_index, row in enumerate(self.data):
            if row[0] == time_stamp:  # Assuming timestamp is in the first column
                # Update the value in the corresponding column
                column_index = self.headers.index(data_point_name)
                if len(row) <= column_index:
                    row.extend([None] * (column_index - len(row) + 1))  # Extend row if necessary
                row[column_index] = data_value

                # Notify the view about the data change
                top_left = self.index(row_index, column_index)
                bottom_right = self.index(row_index, column_index)
                self.dataChanged.emit(top_left, bottom_right)
                return

        # If no matching row is found, add a new row
        new_row = [None] * len(self.headers)
        new_row[0] = time_stamp  # Set the timestamp in the first column
        column_index = self.headers.index(data_point_name)
        new_row[column_index] = data_value
        self.beginInsertRows(QModelIndex(), len(self.data), len(self.data))
        self.data.append(new_row)
        self.endInsertRows()
        if self.view is not None:
            self.view.autoScroll()
        
        # signal that the layout has changed
        
    def saveDataToFile(self, file_path="data.csv"):
        """
        Saves the current data of the model to a CSV file.

        Args:
            file_path (str): The path to the CSV file. Defaults to 'data.csv'.
        """
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write headers
                writer.writerow(self.headers)
                
                # Write data rows
                for row in self.data:
                    writer.writerow(row)
            
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving data to file: {e}")

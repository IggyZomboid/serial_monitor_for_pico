from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QPersistentModelIndex

class tracked_data_table_model(QAbstractTableModel):
    def __init__(self):
        super(tracked_data_table_model, self).__init__()
        self.data = []
        self.headers = []  # Initial headers
        self.addHeader("Timestamp")  # Add a default header for timestamps


    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.headers)  # Number of headers determines column count

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]  # Return dynamic headers
            else:
                return f"Row {section + 1}"
        return None

    def addHeader(self, new_header):
        """
        Dynamically adds a new header and updates the model.
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
        # signal that the layout has changed

import threading
import serial
from datetime import datetime

# Serial Reader Thread Class
class SerialReaderThread(threading.Thread):
    """
    SerialReaderThread is a background thread responsible for reading data from a serial port
    and passing it to the main application for processing.

    Attributes:
        shared_config (SharedConfig): Shared configuration object containing application-wide settings.
        ser (serial.Serial): Serial port object used for communication.
        running (bool): Flag indicating whether the thread is actively reading data.

    Methods:
        __init__(shared_config, ser):
            Initializes the SerialReaderThread with the shared configuration and serial port object.
        run():
            Continuously reads data from the serial port while the thread is running.
        stop():
            Stops the thread by setting the running flag to False.
    """
    def __init__(self, shared_config, serial_port, callback):
        """
        Initializes the SerialReaderThread with the shared configuration and serial port object.

        - Stores the shared configuration and serial port object.
        - Sets the running flag to True.
        """
        super(SerialReaderThread, self).__init__()
        self.shared_config = shared_config
        self.serial_port = serial_port
        self.running = True
        self.callback = callback  # Callback function to process data if needed
        
        self.dataPointNames = []
        
        print(f"SerialReaderThread initialized with serial port: {self.serial_port.portstr}")

    def run(self):
        """
        Continuously reads data from the serial port while the thread is running.

        - Reads data from the serial port using the `readline` method.
        - Passes the data to the shared configuration's queue or processing method.
        """
        while self.running and self.serial_port.is_open:
            try:
                # Read a line of data from the serial port
                raw_line = self.serial_port.readline()

                # Attempt to decode the data using UTF-8 encoding
                try:
                    line = raw_line.decode('utf-8').strip()  # Decode using UTF-8
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    # If UTF-8 decoding fails, fall back to ASCII encoding
                    line = raw_line.decode('ascii', errors='ignore').strip()
                    encoding = 'ascii'

                # If the line is not empty, pass it to the callback function
                if line:
                    self.callback(f"{line}")  # Send the decoded line to the callback
            except Exception as e:
                # If an error occurs, send the error message to the callback
                self.callback(f"Error: {str(e)}")
                break  # Exit the loop on error

    def stop(self):
        """
        Stops the thread by setting the running flag to False.

        - Ensures the thread exits gracefully.
        """
        self.running = False
    
    
    def addDataPointName(self, data_point_name):
        """
        Adds a new data point name to the list of data points.

        Args:
            data_point_name (str): The name of the data point to be added.
        """
        if data_point_name not in self.dataPointNames:
            self.dataPointNames.append(data_point_name)
            return True, f"Data point '{data_point_name}' added."
        else:
            return False, f"Data point '{data_point_name}' already exists."
    
    def removeDataPointName(self, data_point_name):
        """
        Removes a data point name from the list of data points.

        Args:
            data_point_name (str): The name of the data point to be removed.
        """
        if data_point_name in self.dataPointNames:
            self.dataPointNames.remove(data_point_name)
            return True, f"Data point '{data_point_name}' removed."
        else:
            return False, f"Data point '{data_point_name}' does not exist."
    
    def clearDataPointNames(self):
        """
        Clears all data point names from the list.
        """
        self.dataPointNames.clear()
        return "All data points cleared."
    
    def getDataPointNames(self):
        """
        Returns the list of data point names.

        Returns:
            list: A list of data point names.
        """
        if not self.dataPointNames:
            return False, []
        return True, self.dataPointNames

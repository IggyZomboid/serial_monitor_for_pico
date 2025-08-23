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
                    # Record the data point with a timestamp
                    self.record_data_points(line)  # Record the data point with a timestamp
                    
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
    
    def record_data_points(self, line):
        """
        Records data points with a timestamp.

        - Appends the data to the shared configuration's date_queue_dict with the current timestamp.
        """
        # Only record if there are data point names available
        if len(self.shared_config.dataPointNames) != 0:
            #check if line contians a comma
            if ',' in line:
                data = line.split(',')
                if data[0] in self.shared_config.dataPointNames:
                    found_data_name = data[0]
                    found_data_point = data[1]
                    found_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    
                    print(f"Recording data point: {found_data_name} with value: {found_data_point} at {found_timestamp}")
                    
                    datapoint = {found_data_point, found_timestamp}
                    
                    #if date_queue_dict contains found_data_name as key then update add the datapoint to its' list
                    if found_data_name in self.shared_config.date_queue_dict:
                        self.shared_config.date_queue_dict[found_data_name].append(datapoint)
                    else:
                        self.shared_config.date_queue_dict[found_data_name] = [datapoint]
                        
                    # Update the tracked data table model
                    self.shared_config.tracked_data_table_model.addRow(found_timestamp, found_data_name, found_data_point)
                
    
            


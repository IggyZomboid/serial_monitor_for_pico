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
    def __init__(self, shared_config, ser):
        """
        Initializes the SerialReaderThread with the shared configuration and serial port object.

        - Stores the shared configuration and serial port object.
        - Sets the running flag to True.
        """
        super(SerialReaderThread, self).__init__()
        self.shared_config = shared_config
        self.ser = ser
        self.running = True

    def run(self):
        """
        Continuously reads data from the serial port while the thread is running.

        - Reads data from the serial port using the `readline` method.
        - Passes the data to the shared configuration's queue or processing method.
        """
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                # Example: Add the line to a shared queue for processing
                self.shared_config.date_queue_dict[datetime.now()] = line
            except Exception as e:
                print(f"Error reading from serial port: {e}")

    def stop(self):
        """
        Stops the thread by setting the running flag to False.

        - Ensures the thread exits gracefully.
        """
        self.running = False

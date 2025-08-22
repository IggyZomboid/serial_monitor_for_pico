# COM Port Class
class ComPort:
    """
    A class to represent a COM port and its associated details.

    This class encapsulates the properties of a COM port, such as its name, description,
    hardware ID, vendor ID, product ID, and other metadata. It provides a convenient way
    to access and display information about a COM port.

    Attributes:
        device (str): The device path of the COM port (e.g., COM3).
        name (str): The name of the COM port.
        description (str): A brief description of the COM port.
        hwid (str): The hardware ID of the COM port.
        vid (int or None): The vendor ID of the COM port (if available).
        pid (int or None): The product ID of the COM port (if available).
        serial_number (str or None): The serial number of the COM port (if available).
        location (str or None): The physical location of the COM port (if available).
        manufacturer (str or None): The manufacturer of the COM port (if available).
        product (str or None): The product name of the COM port (if available).
        interface (str or None): The interface type of the COM port (if available).

    Methods:
        UIString():
            Returns a formatted string representation of the COM port for display in the UI.
    """
    def __init__(self, comport):
        """
        Initializes a ComPort instance with the details of the provided COM port.

        Args:
            comport: An object representing a COM port, typically obtained from `list_ports.comports()`.

        Attributes are extracted from the `comport` object and assigned to the instance.
        """
        self.device = comport.device  # The device path (e.g., COM3)
        self.name = comport.name  # The name of the COM port
        self.description = comport.description  # A description of the COM port
        self.hwid = comport.hwid  # The hardware ID of the COM port
        self.vid = comport.vid  # The vendor ID of the COM port
        self.pid = comport.pid  # The product ID of the COM port
        self.serial_number = comport.serial_number  # The serial number of the COM port
        self.location = comport.location  # The physical location of the COM
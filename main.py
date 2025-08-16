import sys
import glob
import serial
from PyQt5 import QtWidgets, uic
from serial.tools import list_ports
baudrates = ['300', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '57600', '115200', '230400', '250000']
line_endings = ['None', 'CR', 'LF', 'CRLF']


class com_port:
    def __init__(self, comport ):
        self.device = comport.device
        self.name = comport.name
        self.description = comport.description
        self.hwid = comport.hwid
        self.vid = comport.vid
        self.pid = comport.pid
        self.serial_number = comport.serial_number
        self.location = comport.location
        self.manufacturer = comport.manufacturer
        self.product = comport.product
        self.interface = comport.interface
    @property
    def UIString(self):
        return f"{self.name} - {self.description}"

        
def disconnect_port():
    print("Dummy disconnect function, implement as needed.")    
    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainForm.ui', self)
        
        # get all combo boxes
        self.port_comboBox = self.findChild(QtWidgets.QComboBox, 'port_comboBox')
        self.baud_comboBox = self.findChild(QtWidgets.QComboBox, 'baud_comboBox')
        self.lineEnding_comboBox = self.findChild(QtWidgets.QComboBox, 'lineEnding_comboBox')
        self.view_radio_buttons_group = self.findChild(QtWidgets.QButtonGroup, 'view_radio_buttons_group')
        self.view_radio_buttons = self.view_radio_buttons_group.buttons()
        self.connect_button = self.findChild(QtWidgets.QPushButton, 'connect_button')
        self.refresh_ports_Button = self.findChild(QtWidgets.QPushButton, 'refresh_ports_Button')
        self.output_text = self.findChild(QtWidgets.QTextEdit, 'output_text')
        self.refresh_ports_Button.clicked.connect(self.refresh_ports)
        
        
        self.show()
        
    def refresh_ports(self):
        self.output_UI_message("Refreshing COM ports...")
        get_com_ports(self)  # Refresh the list of COM ports
    
    def output_UI_message(self, message):
        inChevons = "&gt;&gt;&gt;&gt;&gt;&gt;&gt;"
        outChevrons = "&lt;&lt;&lt;&lt;&lt;&lt;&lt;"
        ui_message = f'<span style="color:green;">{inChevons} UI Message Start {outChevrons} <br>{message}<br>{inChevons} UI Message End {outChevrons}</span>' 
        self.output_text.append(ui_message)  # Append the message to the output text area



com_ports = {}

def get_com_ports(window):
    ports = list_ports.comports()
    com_ports.clear()# clear the list before adding new ports
    portsfound = ""
    for port in ports:
        new_port = com_port(port)
        com_ports[new_port.UIString] = new_port
        portsfound += f"{new_port.UIString}<br>"
    window.output_UI_message(f"Found {len(ports)} COM ports:<br>{portsfound}")    
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    get_com_ports(window)
    window.port_comboBox.addItems(com_ports.keys())
    window.baud_comboBox.addItems(baudrates) 
    window.lineEnding_comboBox.addItems(line_endings)  # Example items 
    if window.view_radio_buttons:
        window.view_radio_buttons[0].setChecked(True) # default first item to checked
    sys.exit(app.exec_())
    


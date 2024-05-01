

import serial 
import serial.tools.list_ports

class SerialDev():
    def __init__(self):
        self.devDescriptor = None

    def listPorts(self):
        """ List all available serial ports """
        return serial.tools.list_ports.comports()

    def open(self, port, baudrate):
        """ Open a serial port """
        self.devDescriptor = serial.Serial(port,
                                   baudrate = baudrate,
                                   bytesize = 7,
                                   parity = 'N',
                                   stopbits = 1
                                   )
        return self.devDescriptor
    
    def write(self, str):
        """ Write to the serial port """
        if self.devDescriptor is not None and self.devDescriptor.is_open():
            self.devDescriptor.write(str)
        else:
            print("Error opening the device")
    def read(self):
        """ Read from the serial port """
        line = self.devDescriptor.readline()
        return line
    
    def close(self, devDescriptor):
        """ Close the serial port """
        if devDescriptor.is_open():
            devDescriptor.close()
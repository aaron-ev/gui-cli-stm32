"""
    Author: Aaron Escoboza
    Github: https://github.com/aaron-ev
    File name: serialDev.py
    Description: Classes to open a serial device in a separate thread.
"""

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal

class ThreadSerialDev(QThread):
    signalDataRead = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.stopped = None
        self.serialDev = None
        self.readStandardOut = False

    def listPorts(self):
        """ List all available serial ports """
        return serial.tools.list_ports.comports()

    def open(self, port, baudrate, dataLen, parity, stopBits):
        """ Open a serial port """
        if parity.lower() == "odd":
            parity = 'O'
        elif parity.lower() == "even":
            parity = 'E'
        else:
            parity = 'N'

        self.serialDev = serial.Serial(port,
                                       baudrate = baudrate,
                                       bytesize = dataLen,
                                       parity = parity,
                                       stopbits = stopBits,
                                       timeout = 1
                                       )

    def write(self, str, enableRead = True):
        """ Write to the serial port. Enable reading is to read the response
            after the write.
        """
        if self.serialDev is not None and self.serialDev.is_open:
            try:
                data = str.encode()
                print(f'SERIAL: {data}')
                self.serialDev.write(data)
            except Exception as e:
                print(f'Error: {e}')
                self.close()
        else:
            raise serial.SerialException("Serial device not opened")

        # Read response is read continuously in the thread run function
        # until is disabled
        if enableRead:
            self.startReading = True
            self.start()

    def run(self):
        """ Run thread responsable to read any response from the
            microcontroller
        """
        while(self.startReading):
            self.readResponseSync()

    def readResponseSync(self, timeout = 1):
        """ Blocking call to read from serial device """
        if self.serialDev is None or not self.serialDev.is_open:
            raise serial.SerialException("Serial device not opened")

        self.serialDev.timeout = timeout
        data = self.serialDev.readline()
        if data:
            self.signalDataRead.emit(data)
            return data
        return b''

    def close(self):
        """ Close the serial port """
        # Close any on going read
        self.startReading = False
        if self.isRunning():
            print("Waiting for thread to finish\n")
            self.wait()

        # Close serial port
        if self.serialDev is not None and self.serialDev.is_open:
            self.serialDev.close()
            if self.serialDev.is_open:
                raise Exception("Serial device could not be closed")

    def stop(self):
        """ Stop the serial thread """
        self.startReading = False
        self.wait()
        print("debug: process stopped\n")

    def isOpen(self):
        """ Check if the serial device is opened """
        if self.serialDev is not None:
            return self.serialDev.is_open
        return False



import serial
import serial.tools.list_ports

import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import time

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

    def write(self, str, enableReading = True):
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

        # Read response if it is enabled
        if enableReading:
            self.startReading = True
            self.start()

    def run(self):
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
        self.startReading = False
        if self.isRunning():
            print("Waiting for thread to finish\n")
            self.wait()
        if self.serialDev is not None and self.serialDev.is_open:
            self.serialDev.close()
            if self.serialDev.is_open:
                raise Exception("Serial device could not be closed")

    def stop(self):
        self.wait()
        self.startReading = False
        print("debug: process stopped\n")

    def isOpen(self):
        if self.serialDev is not None:
            return self.serialDev.is_open
        else:
            return False

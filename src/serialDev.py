

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

    def write(self, str):
        """ Write to the serial port """
        if self.serialDev is not None and self.serialDev.is_open:
            self.start()
            try:
                data = str.encode()
                print(f'SERIAL: {data}')
                self.serialDev.write(data)
            except Exception as e:
                print(f'Error: {e}')
                self.close()
        else:
            raise serial.SerialException("Serial device not opened")

    def run(self):
        self.read()

    def read(self, timeOutS = 3):
        """ Read from the serial port """
        if self.serialDev is None or not self.serialDev.is_open:
            raise serial.SerialException("Serial device not opened")

        data = b''
        startTimeMs = time.time() * 1000 # Convert it to ms
        timeElapsed = 0
        timeOutMs = timeOutS * 1000
        while ("EOT" not in data.decode('utf-8') and timeElapsed < timeOutMs):
            data = self.serialDev.readline()
            self.signalDataRead.emit(data)
            timeElapsed = time.time() * 1000 - startTimeMs
        return data

    def close(self):
        """ Close the serial port """
        if self.isRunning():
            print("Waiting for thread to finish\n")
            self.wait()
        if self.serialDev is not None and self.serialDev.is_open:
            self.serialDev.close()
            if self.serialDev.is_open:
                raise Exception("Serial device could not be closed")

    def stop(self):
        self.wait()
        print("debug: process stopped\n")

    def isOpen(self):
        if self.serialDev is not None:
            return self.serialDev.is_open
        else:
            return False

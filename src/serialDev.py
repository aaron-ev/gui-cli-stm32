

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

    def open(self, port, baudrate):
        """ Open a serial port """
        self.serialDev = serial.Serial(port,
                                       baudrate = baudrate,
                                       bytesize = 8,
                                       parity = 'N',
                                       stopbits = 1,
                                       timeout = 1
                                       )

    def write(self, str):
        self.start()
        """ Write to the serial port """
        if self.serialDev is not None and self.serialDev.is_open:
            try:
                data = str.encode()
                print(f'SERIAL: {data}')
                self.serialDev.write(data)
            except Exception as e:
                print(f'Error: {e}')
                self.close()
        else:
            print("Error opening the device")

    def run(self):
        self.read()

    def read(self, timeOutS = 3):
        """ Read from the serial port """
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
        if self.isRunning():
            print("Waiting for thread to finish\n")
            self.wait()
        """ Close the serial port """
        if self.serialDev is not None and self.serialDev.is_open:
            self.serialDev.close()

    def stop(self):
        self.wait()
        print("debug: process stopped\n")

    def isOpen(self):
        if self.serialDev is not None:
            return self.serialDev.is_open
        else:
            return False

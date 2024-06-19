"""
    Author: Aaron Escoboza
    Github: https://github.com/aaron-ev
    File name: micro.py
    Description: Classes that abstracts the microcontroller to have
                 access to it's features.
"""

from serialDev import ThreadSerialDev

class Micro():
    baudRates = ['1200','2400','4800','9600','38400', '115200', '230400']
    channels = ['1', '2', '3', '4']
    gpios  = ['a','b','c','d','e','h']
    pins = (0, 15)
    cmds = {
            'heap':"heap\n",
            'clk':"clk\n",
            'ticks':"ticks\n",
            'version':"version\n",
            'stats': "stats\n",
            'help': "help\n",
            'stats': "stats\n",
            'gpioWrite': "gpio-w",
            'gpioRead': "gpio-r",
            'rtcSet': "rtc-s",
            'rtcGet': "rtc-g\n",
            'pwmSetFreq': "pwm-f",
            'pwmSetDuty': "pwm-d",
            'pwmMonitor': "pwmMonitor",
            'ping': "ping\n",
            }
    maxFreq =  10000 # In Hz
    maxDutyCycle = 100 # (0 - 100)%
    isMonitoring = False

    def __init__(self, callbackDataRead):
        self.serialDev = None
        # User callback for data received from the microcontroller
        self.callbackDataRead = callbackDataRead

        # Thread for sending command and receiving responses via a serial device
        self.serialThread = ThreadSerialDev()
        self.serialThread.signalDataRead.connect(self.slotDataRead)

    def slotDataRead(self, data):
        """ Slot to receive data read from the microcontroller """
        if self.callbackDataRead is not None:
            dataDecoded = data.decode('utf-8')
            self.callbackDataRead(dataDecoded)

    def getVersion(self):
        """ Get SW version """
        self.serialThread.write(self.cmds['version'])

    def writePin(self, gpio, pin, state):
        """ Write a logical value to a GPIO pin """
        cmd = self.cmds['gpioWrite'] + f' {gpio.lower()} {pin} {state}\n'
        self.serialThread.write(cmd)

    def readPin(self, gpio, pin):
        """ Read a GPIO pin """
        cmd = self.cmds['gpioRead'] + f' {gpio.lower()} {pin}\n'
        self.serialThread.write(cmd)

    def help(self):
        """ Reads any help information """
        self.serialThread.write(self.cmds['help'])

    def getStatistics(self):
        """ Reads any help information """
        self.serialThread.write(self.cmds['stats'])

    def getTicks(self):
        """ Get the OS tick counter number """
        self.serialThread.write(self.cmds['ticks'])

    def getHeap(self):
        """ Get OS heap consumption """
        self.serialThread.write(self.cmds['heap'])

    def getClk(self):
        """ Get microcontroller CLK information """
        self.serialThread.write(self.cmds['clk'])

    def getStats(self):
        """ Get microcontroller general information """
        self.serialThread.write(self.cmds['stats'])

    def open(self, serialDev, baud = 9600, dataLen = 8, parity = 'N',
             stopBits = 1):
        """ Open a serial port to exchange data with the microcontroller """
        self.serialThread.open(serialDev, baud, int(dataLen), parity, int(stopBits))

    def close(self):
        """ Kill any thread or monitor activity """
        if self.isMonitoring:
            self.stopPwmMonitor()
            self.isMonitoring = False
        self.serialThread.close()

    def isOpen(self):
        """ Check if a serial communication is opened """
        return self.serialThread.isOpen()

    def getRtcTime(self):
        """ Get microcontroller RTC time """
        self.serialThread.write(self.cmds['rtcGet'])

    def setRtcTime(self, hr, min, s = 0):
        """ Set a new RTC time """
        cmd = self.cmds['rtcSet'] + f' {hr} {min} {s}\n'
        self.serialThread.write(cmd)

    def setPwmFreqDuty(self, freq, duty):
        """ Set a new PWM frequency and duty cycle """
        if (freq < 0 or freq > self.maxFreq):
            raise Exception("Invalid frequency")
        if (duty < 0 or duty > self.maxDutyCycle):
            raise Exception("Invalid duty, it should be between 1-100")

        # Frequency and duty cycle are written in two consecutive
        cmd = self.cmds['pwmSetFreq'] + f' {freq}\n'
        self.serialThread.write(cmd)
        cmd = self.cmds['pwmSetDuty'] + f' {duty}\n'
        self.serialThread.write(cmd)

    def monitorPwm(self, channel = 1):
        """ Send a command to monitor a PWM channel"""
        if str(channel) not in self.channels:
            raise Exception("Invalid channel, valid range (1-4)")
        cmd = self.cmds['pwmMonitor'] + f' {channel}\n'
        self.isMonitoring = True
        self.writeToMicro(cmd)

    def stopPwmMonitor(self):
        """ Stop PWM monitoring feature """
        cmd = f'stopMonitor\n'
        self.writeToMicro(cmd)
        self.isMonitoring = False

    def ping(self):
        """ Test if there is a connection with the microcontroller """
        cmd = self.cmds['ping']
        # Writes to the serial waiting for a read
        self.writeToMicro(cmd, False)
        data = self.serialThread.readResponseSync(timeout = 1).decode()
        if data.strip() == "OK":
            return "connected"
        else:
            return "disconnected"

    def writeToMicro(self, data, enableRead = True):
        """ Writes to the serial port where the microcontroller is connected.
            By default, each writes waits for a response in a separate thread.
            Reading after a write can be disabled by setting enable read to
            False.
        """
        self.serialThread.write(data, enableRead)

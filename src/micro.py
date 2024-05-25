from serialDev import ThreadSerialDev
class Micro():
    baudRates = ['1200','2400','4800','9600','38400', '115200']
    # channels = ['CH1', 'CH2', 'CH3', 'CH4']
    channels = ['1', '2', '3', '4']
    supportedGpios  = ['a','b','c','d','e','h']
    supportedPins = (0, 15)
    cmds = {\
            'heap':"heap\n",
            'clk':"clk\n",
            'ticks':"ticks\n",
            'version':"version\n",
            'stats':"stats\n",
            'help':"help\n",
            'rtcTime':"rtc-g\n",
            'stats':"stats\n",
            }
    maxFreq =  10000 # In Hz
    isMonitoring = False

    def __init__(self, callbackDataRead):
        self.serialDev = None
        self.callbackDataRead = callbackDataRead
        self.serialThread = ThreadSerialDev()
        self.serialThread.signalDataRead.connect(self.slotDataRead)

    def slotDataRead(self, data):
        if self.callbackDataRead is not None:
            dataDecoded = data.decode('utf-8')
            self.callbackDataRead(dataDecoded)

    def getSupportedPins(self):
        return self.supportedPins

    def getSupportedGpios(self):
        return self.supportedGpios

    def getVersion(self):
        self.serialThread.write(self.cmds['version'])

    def writePin(self, gpio, pin, state):
        if state == True:
            cmd = f'gpio-w {gpio.lower()} {pin} 1\n'
        else:
            cmd = f'gpio-w {gpio.lower()} {pin} 0\n'
        self.serialThread.write(cmd)

    def readPin(self, gpio, pin):
        cmd = f'gpio-r {gpio.lower()} {pin}\n'
        self.serialThread.write(cmd)

    def help(self):
        self.serialThread.write(self.cmds['help'])

    def getStatistics(self):
        self.serialThread.write(self.cmds['stats'])

    def getTicks(self):
        self.serialThread.write(self.cmds['ticks'])

    def getHeap(self):
        self.serialThread.write(self.cmds['heap'])

    def getClk(self):
        self.serialThread.write(self.cmds['clk'])

    def getStats(self):
        self.serialThread.write(self.cmds['stats'])

    def open(self, serialDev, baud = 9600, dataLen = 8, parity = 'N', stopBits = 1):
        self.serialThread.open(serialDev, baud, int(dataLen), parity, int(stopBits))

    def close(self):
        self.serialThread.close()

    def isOpen(self):
        return self.serialThread.isOpen()

    def getRtcTime(self):
        self.serialThread.write(self.cmds['rtcTime'])

    def setRtcTime(self, hr, min, s = 0):
        cmd = f'rtc-s {hr} {min} {s}'
        self.serialThread.write(cmd)

    def setPwmFreqDuty(self, freq, duty):
        # Validate freq and duty parameters
        if (freq < 0 or freq > self.maxFreq):
            raise Exception("Invalid frequency")
        if (duty < 0 or duty > 100):
            raise Exception("Invalid duty, it should be between 1-100")

        # Write frequency
        cmd = f'pwm-f {freq}'
        print(cmd)
        # self.serialThread.write(cmd)
        # Write duty cycle
        cmd = f'pwm-d {duty} 1'
        print(cmd)
        # self.serialThread.write(cmd)

    def monitorPwm(self, channel = 1):
        """ Send a command to monitor a PWM channel"""
        if str(channel) not in self.channels:
            raise Exception("Invalid channel, valid range (1-4) ")
        cmd = f'pwmMonitor {channel}\n'
        self.isMonitoring = True
        self.writeToSerial(cmd)

    def stopPwmMonitor(self):
        """ Stop PWM monitoring feature """
        cmd = f'stopMonitor\n'
        self.writeToSerial(cmd)
        self.isMonitoring = False

    def writeToSerial(self, data, enableReading = True):
        """ Function to send data to a serial device"""
        self.serialThread.write(data, enableReading)

    def ping(self):
        """ Test if there is a connection with the microcontroller """
        cmd = f'ping\n'
        self.writeToSerial(cmd, False)
        data = self.serialThread.readResponseSync(1).decode()
        if data.strip() == "OK":
            return "connected"
        else:
            return "disconnected"

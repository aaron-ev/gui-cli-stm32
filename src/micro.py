from serialDev import ThreadSerialDev

class Micro():
    supportedGpios  = ['a','b','c','d','e','h']
    supportedPins = (0, 15)
    cmds = {\
            'heap':"heap\n",
            'clk':"clk\n",
            'ticks':"ticks\n",
            'version':"version\n",
            'stats':"stats\n",
            'help':"help\n",
            }

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

    def open(self, serialDev, baud):
        self.serialThread.open(serialDev, baud)

    def close(self):
        self.serialThread.close()


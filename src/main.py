"""
    Author: Aaron Escoboza
    Github: https://github.com/aaron-ev
    File name: main.py
    Description:  GUI application to perform I/O operations in a
    microcontroller.
"""

# Built-in modules
import os
import queue
import time

# PyQT modules
from PyQt5.QtWidgets import (QApplication, QMenuBar, QToolBar, QWidget, QGridLayout,
                             QFrame, QFileDialog, QMessageBox,QStatusBar
                             )
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QColor, QTextCursor

# User defined modules
from appClasses import AppMainWindow, AWidgets, ASettings, APlot
from micro import Micro

# Serial communication modules
import serial
import serial.tools.list_ports

# Matplot modules
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Utilities
import numpy as np

# Window size
APP_WIDTH = 1000
APP_HIGHT = 860

class GuiCli(AppMainWindow):
    """ Main window class """

    appVersion = {'major': '1', 'minor':'0'}
    # Settings that apply to the majority of the widgets
    guiSettings = {
                   'buttonSize':(110, 45),
                   'defaultLogFrameSize':450,
                   'labelPointSize': 12,
                   'maxControlFrameWidth': 290,
                   'maxControlFrameHight': 80,
                   'currentTheme': 'dark',
                   'toolbarIconSize': 23,
                   'textBoxLogHeight': 280,
                   'frameGpioHeight': 180,
                   'frameGeneralInfoHeight': 180,
                   'frameRtcHeight': 150,
                   'framePwmHeight': 230,
                  }
    # All widgets are tracked so that a new theme can be applied to them
    listWidgets = {
                   'frame':[],
                   'button': [],
                   'line': [],
                   'label':[],
                   'combobox':[],
                   'textBox':[],
                   'text':[],
                   'toolbar':[],
                   }
    pwmYValues = []
    yValues = []
    t = 0
    threadStarted = False
    plotTimer = None
    plotYValues = []
    isMonitoring = False
    oldDigit = 0

    def slotPlotTimerTimeOut(self):
        """ Slot for catching the timer timeout """
        if not self.plotQueue.qsize() == 0:
            newDigit = self.plotQueue.get()
            if len(self.plotYValues) > 500:
                self.plotYValues = self.plotYValues[25:]
            [self.plotYValues.append(newDigit) for i in range(0, 25)]
            # # Create X list with linspace values
            plotXValues = np.linspace(0, 10, len(self.plotYValues))
            self.writeToPlot(plotXValues, self.plotYValues)

    def startPlotTimer(self):
        """ Start a timer for plotting data """
        if self.plotTimer is not None:
            self.plotTimer.start(1)

    def stopPlotTimer(self):
        """ Stop the plot timer """
        if self.plotTimer is not None:
            self.plotTimer.stop()
            self.plotYValues = []

    def __init__(self, title, w, h):
        super().__init__()
        self.appRootPath = os.getcwd()

        # Object to perform microcontroller operations
        self.micro = Micro(callbackDataRead = self.callbackMicroReadData)

        # Initialize main window with icon, title, and user width/height
        self.initMainWindow(self.appRootPath, title, w, h)

        # Object to create custom widgets
        self.aWidgets = AWidgets()

        # Set a default fo nt for buttons
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(self.buttonFontSize)

        # Object to save user settings
        self.settings = ASettings(self.appRootPath, self.iconPaths)

        # Initialize all layouts attached to the main window
        self.initLayouts()

        # Initialize status bar
        self.statusBarWidget = QStatusBar()
        self.initStatusBar(self.statusBarWidget)

        self.initPlot()
        # Initialize menu bar
        # self.initMenuBar()

        # Initialize toolbar
        self.initToolBar()

        # Initialize two main section:
        # 1. Section for buttons to send micro requests/cmds
        # 2. Section for logging and data visualization
        self.initLogSection()
        self.initControlSection()
        self.aplot.setLegend(f'Channel {self.comboBoxPwmChannels.currentText()}')

        # Create queue for saving log messages
        self.logQueue = queue.Queue()

        self.applyTheme(self.guiSettings['currentTheme'])
        if self.guiSettings['currentTheme'] == 'dark':
            self.writeToLog("Welcome to Micro CLI\n\n", 'white')
        else:
            self.writeToLog("Welcome to Micro CLI\n\n", 'dark')

        # Initialize event loop by calling show method
        self.show()

    def initPlot(self):
        """ Initialize the a plot object to plot a PWM signal """
        self.aplot = APlot()
        self.aplot.setLineStyle('b-')
        self.aplot.setXlim((0, 100))
        self.aplot.setYLim((-0.1, 1.1))
        self.aplot.setTitle("PWM signal")
        self.aplot.setXLabel("Time")
        self.aplot.setYLabel("Logic level")
        self.plotTimer = QTimer()
        self.plotTimer.timeout.connect(self.slotPlotTimerTimeOut)
        # Queue to save plot data coming from the micro
        self.plotQueue = queue.Queue()

        self.plotNavigationBar = NavigationToolbar(self.aplot.canvas)
        self.plotNavigationBar.setStyleSheet("background-color:white;")
        self.aplot.canvas.setMinimumHeight(260)

    def initStatusBar(self, statusBar):
        """ Initialize the status bar """
        self.setStatusBar(statusBar)
        font = QFont()
        font.setPointSize(10)
        self.statusBarWidget.setFont(font)
        self.updateStatusBar("Serial device: disconnected")

    def initMenuBar(self):
        """ Initialize the menu bar """
        menuBar = QMenuBar()

        # Create bar options
        menuBarSave= menuBar.addMenu("&Save")
        menuBarSettings = menuBar.addMenu("&Settings")
        menuBarSettings.aboutToShow.connect(self.showSettingsMenu)
        menuBarHelp = menuBar.addMenu("&Help")

        # Create actions for help
        infoAction = self.aWidgets.newAction(self, "&Info", self.appRootPath + self.iconPaths['info'], self.actionHelp)
        # actionSerialSettings = self.aWidgets.newAction(self, "&Serial device", slot = self.actionSerialSettings)
        actionSaveLog = self.aWidgets.newAction(self, "&Log", self.appRootPath + self.iconPaths['save'],  self.actionSaveLog)

        # Add all actions to the menubar
        menuBarHelp.addAction(infoAction)
        # menuBarSettings.addAction(actionSerialSettings)
        menuBarSave.addAction(actionSaveLog)

        # Set menu bar to the main window
        self.setMenuBar(menuBar)

    def initToolBar(self):
        """ Initialize the tool bar """
        self.toolbar = QToolBar()
        self.listWidgets['toolbar'].append(self.toolbar)

        # Create actions for saving the log
        actionSaveLog = self.aWidgets.newAction(self, "&Save log", self.appRootPath + self.iconPaths['save'], self.actionSaveLog)
        actionSaveLog.setToolTip("<font color='back'>Save logs to a file</font>")

        # Create actions for general settings
        actionSettings = self.aWidgets.newAction(self, "&Settings", self.appRootPath + self.iconPaths['settings'], self.actionSettings)
        actionSettings.setToolTip("<font color='back'>General settings</font>")

        # Create help action
        actionHelp = self.aWidgets.newAction(self, "&Help", self.appRootPath + self.iconPaths['help'], self.actionHelp)
        actionHelp.setToolTip("<font color='black'>General help</font>")

        # Add all actions to the self.toolbar
        self.toolbar.addAction(actionSaveLog)
        self.toolbar.addAction(actionSettings)
        self.toolbar.addAction(actionHelp)

        # self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolbar.setMovable(False)

        self.addToolBar(self.toolbar)

    def applyTheme(self, theme):
        """ Apply a new theme to all widgets """
        # Select the theme
        newTheme = theme.lower()
        widgetStyles = self.themes[newTheme]

        # Set the new style to each widget
        self.setStyleSheet(widgetStyles['mainWindow'])
        for key in self.listWidgets:
            for widget in self.listWidgets[key]:
                widget.setStyleSheet(widgetStyles[key])
        self.toolbar.setIconSize(QSize(self.guiSettings['toolbarIconSize'], self.guiSettings['toolbarIconSize']))
        self.guiSettings['currentTheme'] = newTheme

        # Update text already displayed in log widget
        if newTheme == 'light':
            self.updateTextColor('dark', self.textBoxLog)
            self.statusBarWidget.setStyleSheet(f'color:dark;')
        else:
            self.statusBarWidget.setStyleSheet(f'color:white;')
            self.updateTextColor('white', self.textBoxLog)

    def actionInfo(self):
        self.writeToLog("Info not implemented yet\n")

    def actionSaveLog(self):
        """ Save the log to a text file """
        # If queue is empty, it doesn't make sense to save a log file
        if self.logQueue.empty():
            self.showErrorMessage("No log to save")
            return

        fileName, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text Files (*.txt)")
        if fileName:
            # Copy current log from a queue
            tmpLogQueue = queue.Queue()
            for item in self.logQueue.queue:
                tmpLogQueue.put(item)
            # Write tmp queue to selected file
            with open(fileName, 'w') as f:
                while not tmpLogQueue.empty():
                    f.write(tmpLogQueue.get())
            self.writeToLog(f'\nSaved log to {fileName}\n', 'green')

    def actionSettings(self):
        """ Open a new window with general settings """
        # Enter in an event loop until user close the pop up window
        if self.settings.exec_():
            # Apply the new theme in case it is different from the current one
            theme = self.settings.getTheme()
            if theme != self.guiSettings['currentTheme']:
                self.applyTheme(theme)

    def actionHelp(self):
        """ Shows general help information """
        self.writeToLog(f'\nApp version v{self.appVersion["major"]}.{self.appVersion["minor"]}\n'
                        f'Author: Aaron Escoboza\n'
                        f'Github: https://github.com/aaron-ev\n',
                        'white'
                        )

    def showSettingsMenu(self):
        """ Show general settings window """
        if self.settings.exec_():
            self.writeToLog("Apply event\n")

    def clearLogQueue(self):
        """ Clear the queue by removing all items """
        while not self.logQueue:
            self.logQueue.get()

    state = "idle"
    firstRisingEdgeTimeDetection = 0
    secondRisingEdgeTimeDetection = 0

    def detectFrequency(self, digit):
        """ State machine to detect rising, falling and rising edge again"""
        # print(digit)
        # Idle state
        if self.state == "idle":
            if digit:
                self.state = "firstEdge"
                # print("debug: rising edge")
                self.firstRisingEdgeTimeDetection = time.time()

        # First edge state
        if self.state == "firstEdge":
            if not digit :
                # print("debug: falling edge")
                self.state = "fallingEdge"

        # Falling edge state
        if self.state == "fallingEdge":
            if digit:
                # print("debug: second rising edge")
                self.state = "secondRisingEdge"
                self.secondRisingEdgeTimeDetection = time.time()
                # Calculate frequency
                t1 = self.firstRisingEdgeTimeDetection
                t2 = self.secondRisingEdgeTimeDetection
                if (t2 - t1) > 0:
                    freq = str(1 / float(t2 - t1))
                    dotIndex = freq.find('.')
                    truncatedFrequency = freq[:dotIndex + 1] + freq[dotIndex  + 1: dotIndex  + 4]
                    self.writeToLog(f'Frequency: {truncatedFrequency}Hz\n')

        if self.state == "secondRisingEdge":
            if not digit:
                # print("debug: second falling edge, going to idle\n")
                self.state = "idle"

    def callbackMicroReadData(self, data):
        """ Callback to receive data read from the microcontroller """
        # If data comes from PWW monitor feature, it should be displayed in
        # a plot instead of a text widget.
        if "pwm:" in data:
            digit = int(data.split(':')[-1].strip())
            self.detectFrequency(digit)
            if not self.plotTimer.isActive():
                self.startPlotTimer()

            if self.plotQueue.not_full:
                if digit != self.oldDigit:
                    self.plotQueue.put(digit)
                    self.oldDigit = digit
            else:
                self.writeToLog("Error: Plot queue full\n")

        else: # Any command that is not monitoring
            if not data.strip() == "OK":
                self.writeToLog(data)

            # Prevent log queue to overflow by incoming new data
            if self.logQueue.full():
                self.writeToLog("Can't log more data, queue is full\n", 'red')
            else:
                pass
                # self.logQueue.put(data)

    def slotComboBoxComPorts(self):
        pass

    ##3###########################################################
    #                    START OF INIT FUNCTIONS
    ##3###########################################################
    def initLogSection(self):
        """ Initialize a section with all widgets to view log information """
        # Create all labels
        labelPort = self.aWidgets.newLabel("Port", self.guiSettings['labelPointSize'], None)
        labelBaudRate = self.aWidgets.newLabel("Baud rate", self.guiSettings['labelPointSize'], None)
        self.listWidgets['label'].append(labelPort)
        self.listWidgets['label'].append(labelBaudRate)

        # Create combobox for sandboxes
        self.comboBoxComPorts = self.aWidgets.newComboBox(self.slotComboBoxComPorts)
        self.comboBoxComPorts.setFixedWidth(250)
        self.comboBoxBaudrates = self.aWidgets.newComboBox()
        self.listWidgets['combobox'].append(self.comboBoxComPorts)
        self.listWidgets['combobox'].append(self.comboBoxBaudrates)

        # Update combobox with available ports
        self.refreshSerialPorts()

        # Update combobox with supported baudrates
        for baud in self.micro.baudRates:
            self.comboBoxBaudrates.addItem(baud)
        self.comboBoxBaudrates.setCurrentText('115200')

        # Dock: Dock for any message from serial port
        self.dockLog, self.textBoxLog = self.aWidgets.newDock("Log", "dock")
        self.textBoxLog.setFixedHeight(self.guiSettings['textBoxLogHeight'])
        self.listWidgets['text'].append(self.textBoxLog)

        # Button: Connect to serial port
        self.buttonConnectDisconnect = self.aWidgets.newButton("Start connection",
                                                                self.slotConnectDisconnect,
                                                                self.buttonsFont,
                                                                self.appRootPath + self.iconPaths['serialPort'],
                                                                (220, 30)
                                                              )
        # Button: Refresh the serial port list
        buttonRefresh = self.aWidgets.newButton("",
                                                  self.slotButtonRefreshSerialPorts,
                                                  self.buttonsFont,
                                                  self.appRootPath + self.iconPaths['refresh'],
                                                  (60, 35),
                                                  None
                                                )
        # Button: Clean log
        buttonCleanLog = self.aWidgets.newButton("Clear",
                                                  self.slotButtonCleanLog,
                                                  self.buttonsFont,
                                                  self.appRootPath + self.iconPaths['clear'],
                                                  None,
                                                )
        # Track all buttons
        self.listWidgets['button'].append(self.buttonConnectDisconnect)
        self.listWidgets['button'].append(buttonRefresh)
        self.listWidgets['button'].append(buttonCleanLog)

        # Add widgets to the log layout
        ## Serial and text widgets
        self.layoutLog.addWidget(labelPort, 1, 0)
        self.layoutLog.addWidget(self.comboBoxComPorts, 1, 1)
        self.layoutLog.addWidget(buttonRefresh, 1, 2)
        self.layoutLog.addWidget(labelBaudRate, 1, 3)
        self.layoutLog.addWidget(self.comboBoxBaudrates, 1, 4)
        self.layoutLog.addWidget(buttonCleanLog, 2, 0)
        self.layoutLog.addWidget(self.buttonConnectDisconnect, 2, 1, 1, -1, alignment = Qt.AlignmentFlag.AlignCenter)
        self.layoutLog.addWidget(self.dockLog, 3, 0, 1, -1)

        ## Plot widgets
        self.layoutPlots.addWidget(self.plotNavigationBar, 0, 0)
        self.layoutPlots.addWidget(self.aplot.canvas, 1, 0)

    def writeToPlot(self, x, y):
        """ Write to the plot the list of x and y values """
        self.aplot.plot(x,y)

    def initControlSection(self):
        """ Initialize a section with all widgets to perform IO operations with
            the microcontroller.
        """
        # Create all labels
        labelTitleGpioRW = self.aWidgets.newLabel("GPIO Write/Read", self.guiSettings['labelPointSize'], None)
        labelGpio= self.aWidgets.newLabel("GPIO", 10, None)
        labelPin = self.aWidgets.newLabel("Pin", 10, None)
        labelTitleGeneralInfo = self.aWidgets.newLabel("General information ", self.guiSettings['labelPointSize'], None)
        labelTitleRtc = self.aWidgets.newLabel("RTC", self.guiSettings['labelPointSize'], None)
        labelRtcHr = self.aWidgets.newLabel("Hr", 10, None)
        labelRctMin = self.aWidgets.newLabel("Min", 10, None)
        labelTitlePwm = self.aWidgets.newLabel("PWM", self.guiSettings['labelPointSize'], None)
        labelPwmFreq  = self.aWidgets.newLabel("Freq", 10, None)
        labelPwmDuty  = self.aWidgets.newLabel("Duty", 10, None)
        labelPwmChannel = self.aWidgets.newLabel("Channel", 10, None)

        # Track the widgets
        self.listWidgets['label'].append(labelTitleGpioRW)
        self.listWidgets['label'].append(labelGpio)
        self.listWidgets['label'].append(labelPin)
        self.listWidgets['label'].append(labelTitleGeneralInfo)
        self.listWidgets['label'].append(labelTitleRtc)
        self.listWidgets['label'].append(labelRtcHr)
        self.listWidgets['label'].append(labelRctMin)
        self.listWidgets['label'].append(labelTitlePwm)
        self.listWidgets['label'].append(labelPwmFreq)
        self.listWidgets['label'].append(labelPwmDuty)
        self.listWidgets['label'].append(labelPwmChannel)

        # Combobox: GPIOs
        self.comboBoxGpios = self.aWidgets.newComboBox()
        for gpio in self.micro.gpios:
            self.comboBoxGpios.addItem(gpio.upper())

        # Line: Pin numbers
        self.comboBoxPins = self.aWidgets.newComboBox()
        minPinNumber, maxPinNumber = self.micro.pins
        for pinNumber in range(minPinNumber, maxPinNumber + 1):
            self.comboBoxPins.addItem(str(pinNumber).upper())

        # Button: Set to ON
        buttonPinON = self.aWidgets.newButton("On",
                                            self.slotButtonOn,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['powerOn'],
                                            )
        # Button: Set to OFF
        buttonPinOff= self.aWidgets.newButton("Off",
                                            self.slotButtonOff,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['powerOff'],
                                            )
        # Button: Read from GPIO pin
        buttonReadPin = self.aWidgets.newButton("Read",
                                            self.slotButtonReadPin,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['refresh'],
                                            )
        # Button: Get the project version
        buttonVersion = self.aWidgets.newButton("Version",
                                            self.slotVersion,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['version'],
                                            )
        # Button: Help
        buttonHelp = self.aWidgets.newButton("Help",
                                            self.slotHelp,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['info'],
                                            )
        # Button: Heap information
        buttonHeap = self.aWidgets.newButton("Heap",
                                            self.slotHeap,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['ram'],
                                            None,
                                            )
        # Button: Tick information
        buttonTicks = self.aWidgets.newButton("Ticks",
                                            self.slotTicks,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['freq'],
                                            )
        # Button: Clock information
        buttonClk = self.aWidgets.newButton("Clock",
                                            self.slotClk,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['clk'],
                                            )
        # Button: General statistics
        buttonStats = self.aWidgets.newButton("Stats",
                                            self.slotStats,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['stats'],
                                            )

        # Widgets for RTC peripheral
        self.textRtcHr = self.aWidgets.newLine(10)
        self.textRtcMin = self.aWidgets.newLine(10)
        # Button: Set a time RTC time
        buttonSetTime = self.aWidgets.newButton("Set time",
                                            self.slotRtcSetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['setTime'],
                                            )
        # Button: Get the current RTC time
        buttonGetTime = self.aWidgets.newButton("Get time",
                                            self.slotRtcGetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['getTime'],
                                            )
        # Combobox: PWM channels
        self.comboBoxPwmChannels = self.aWidgets.newComboBox()
        for channel in self.micro.channels:
            self.comboBoxPwmChannels.addItem(channel)

        # Widgets to set PWM frequency and duty cycle
        self.textPwmFreq = self.aWidgets.newLine(10)
        self.textPwmDuty = self.aWidgets.newLine(10)

        # Button: Set frequency and duty cycle
        buttonPwmSetFreqDuty = self.aWidgets.newButton("Set freq/duty",
                                            self.slotPwmSetFreqDuty,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['freq2'],
                                            )
        # Button: Start measure
        self.buttonPwmMonitor = self.aWidgets.newButton("Monitor channel",
                                            self.slotPwmMonitor,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['stats'],
                                            )


        # Add widgets to the record of widgets
        self.listWidgets['button'].append(buttonPinON)
        self.listWidgets['button'].append(buttonPinOff)
        self.listWidgets['button'].append(buttonReadPin)
        self.listWidgets['button'].append(buttonVersion)
        self.listWidgets['button'].append(buttonHelp)
        self.listWidgets['button'].append(buttonHeap)
        self.listWidgets['button'].append(buttonTicks)
        self.listWidgets['button'].append(buttonClk)
        self.listWidgets['button'].append(buttonStats)
        self.listWidgets['button'].append(buttonSetTime)
        self.listWidgets['button'].append(buttonGetTime)
        self.listWidgets['button'].append(buttonPwmSetFreqDuty)
        self.listWidgets['button'].append(self.buttonPwmMonitor)
        self.listWidgets['combobox'].append(self.comboBoxGpios)
        self.listWidgets['combobox'].append(self.comboBoxPins)
        self.listWidgets['combobox'].append(self.comboBoxPwmChannels)
        self.listWidgets['line'].append(self.textRtcHr)
        self.listWidgets['line'].append(self.textRtcMin)
        self.listWidgets['line'].append(self.textPwmFreq)
        self.listWidgets['line'].append(self.textPwmDuty)

        # GPIO handling
        self.layoutGpio.addWidget(labelTitleGpioRW, 0, 0, 1, -1)
        self.layoutGpio.addWidget(labelGpio, 1, 0)
        self.layoutGpio.addWidget(self.comboBoxGpios, 1, 1)
        self.layoutGpio.addWidget(labelPin, 1, 2)
        self.layoutGpio.addWidget(self.comboBoxPins, 1, 3)
        self.layoutGpio.addWidget(buttonPinON, 2, 0, 1, 2)
        self.layoutGpio.addWidget(buttonPinOff, 2, 2, 1, 2)
        self.layoutGpio.addWidget(buttonReadPin, 3, 0, 1, -1)

        # General info
        self.layoutGeneral.addWidget(labelTitleGeneralInfo, 0, 0, 1, -1)
        self.layoutGeneral.addWidget(buttonHeap, 1, 0, 1, 2)
        self.layoutGeneral.addWidget(buttonTicks, 1, 2, 1, 2)
        self.layoutGeneral.addWidget(buttonClk, 2, 0, 1, 2)
        self.layoutGeneral.addWidget(buttonVersion, 2, 2, 1, 2)
        self.layoutGeneral.addWidget(buttonHelp, 3, 0, 1, 2)
        self.layoutGeneral.addWidget(buttonStats, 3, 2, 1, 2)

        # RTC
        self.layoutRtc.addWidget(labelTitleRtc, 0, 0, 1, -1)
        self.layoutRtc.addWidget(labelRtcHr, 1, 0)
        self.layoutRtc.addWidget(self.textRtcHr, 1, 1)
        self.layoutRtc.addWidget(labelRctMin, 1, 2)
        self.layoutRtc.addWidget(self.textRtcMin, 1, 3)
        self.layoutRtc.addWidget(buttonSetTime, 2, 0, 1, 2)
        self.layoutRtc.addWidget(buttonGetTime, 2, 2, 1, 2)

        # PWM
        self.layoutPwm.addWidget(labelTitlePwm, 0, 0, 1, -1)
        self.layoutPwm.addWidget(labelPwmFreq, 1, 0)
        self.layoutPwm.addWidget(self.textPwmFreq, 1, 1)
        self.layoutPwm.addWidget(labelPwmDuty, 1, 2)
        self.layoutPwm.addWidget(self.textPwmDuty, 1, 3)
        self.layoutPwm.addWidget(buttonPwmSetFreqDuty, 2, 0, 1, -1)
        self.layoutPwm.addWidget(labelPwmChannel, 3, 0, 1, 2)
        self.layoutPwm.addWidget(self.comboBoxPwmChannels, 3, 2, 1, -1)
        self.layoutPwm.addWidget(self.buttonPwmMonitor, 4, 0, 1, -1)

    def slotPwmMonitor(self):
        """ Slot to monitor a PWM channel"""
        if self.micro.isMonitoring:
            self.stopPlotTimer()
            self.buttonPwmMonitor.setText("Monitor channel")
        else: # No monitoring active, it should be started
            channel = int(self.comboBoxPwmChannels.currentText())
            # Start time will be used as start time for signal plotting
            try:
                self.aplot.setLegend(f'Channel {channel}')
                self.micro.monitorPwm(channel)
                self.writeToLog("\nResponse: \n\n", '#77DD77')
                self.buttonPwmMonitor.setText("Stop monitoring")
            except Exception as e:
                self.showErrorMessage(f'{e}')

    def updateBorderColor(self, widget, hexBorderColor):
        """ Updates the border of a widget """
        style = widget.styleSheet()
        border_index = style.find("border:")
        if border_index != -1:
            hash_index = style.find("#", border_index)
            if hash_index != -1:
                color_substring = style[hash_index:hash_index + 7]
                new_style = style.replace(color_substring, hexBorderColor)
                widget.setStyleSheet(new_style)

    def slotRtcSetTime(self):
        """ Slot to set a new RTC time """
        # Validate time
        hr = self.textRtcHr.text()
        min = self.textRtcMin.text()
        if len(hr) < 1:
            self.showErrorMessage("Invalid hour")
            return
        if len(min) < 1:
            self.showErrorMessage("Invalid minutes")
            return

        try:
            self.micro.setRtcTime(hr, min)
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotRtcGetTime(self):
        """ Slot to get the RTC time from the microcontroller """
        try:
            self.micro.getRtcTime()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotPwmSetFreqDuty(self):
        """ Slot to set the frequency and the duty cycle """
        try:
            freq =  self.textPwmFreq.text()
            duty = self.textPwmDuty.text()
            if len(freq) < 1:
                raise Exception("Invalid frequency")
            if len(duty) < 1:
                raise Exception("Invalid duty cycle")

            self.micro.setPwmFreqDuty(int(freq), int(duty))
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonReadPin(self):
        """ Slot to read a GPIO pin """
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
             self.micro.readPin(gpio, pin)
             self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotVersion(self):
        """ Slot to get the microcontroller software version """
        try:
            self.micro.getVersion()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotHelp(self):
        """ Slot to display microcontroller help """
        try:
            self.micro.help()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotTicks(self):
        """ Slot to get ticks information """
        try:
            self.micro.getTicks()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotClk(self):
        """ Slot to get clock information """
        try:
            self.micro.getClk()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotStats(self):
        """ Slot to get microcontroller statistics """
        try:
            self.micro.getStats()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotHeap(self):
        """ Slot to get heap information """
        try:
            self.micro.getHeap()
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonOn(self):
        """ Slot to turn on a pin """
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
            self.micro.writePin(gpio, pin, True)
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonCleanLog(self):
        self.textBoxLog.clear()
        self.clearLogQueue()

    def slotButtonOff(self):
        """ Slot to off on a pin """
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
            self.micro.writePin(gpio, pin, False)
            self.writeToLog("\nResponse: \n\n", '#77DD77')
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonRefreshSerialPorts(self):
        """ Slot to refresh the list of serial ports """
        self.refreshSerialPorts()
        if len(self.ports) < 1:
            self.showErrorMessage("Valid ports not found")

    def refreshSerialPorts(self):
        self.comboBoxComPorts.clear()
        tmpPorts = serial.tools.list_ports.comports()
        self.ports = []
        for port in tmpPorts:
            if "USB" in port.hwid:
                self.comboBoxComPorts.addItem(port.description)
                self.ports.append(port)

    def centerWindow(self):
        """ Centers the window on the screen """
        # Get the geometry of the screen
        screenGeometry = QApplication.desktop().screenGeometry()

        # Calculate the center position for the main window
        x = (screenGeometry.width() - self.width()) // 2 - 220
        y = (screenGeometry.height() - self.height()) // 2 - 180

        # Set the geometry of the main window to the center position
        self.setGeometry(x, y, self.width(), self.height())

    def initMainWindow(self, appRootPath, title, w, h):
        """ Set default main windows properties """
        self.centerWindow()
        self.setMinimumHeight(h)
        # self.setFixedSize(w, h)
        self.setWindowTitle(title + f" v{self.appVersion['major']}.{self.appVersion['minor']}")
        self.setWindowIcon(QIcon(appRootPath + self.iconPaths["mainIcon"]))

    def initLayouts(self):
        """ Initialize all layouts """
        # Central widget
        self.centralWidget = QWidget()

        # Layout: Main
        self.gridLayout = QGridLayout(self.centralWidget)
        self.centralWidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralWidget)

        # Frame: Frame for holding widgets for controlling the micro
        frame = QFrame(self)
        # frame.setFixedWidth(self.guiSettings['maxControlFrameWidth'])
        # frame.setMaximumHeight(self.guiSettings['maxControlFrameHight'])
        self.layoutFrameControl = QGridLayout()
        frame.setLayout(self.layoutFrameControl)
        self.gridLayout.addWidget(frame, 0, 0, -1, 1)

        # Frame: Frame for holding widgets to GPIO handling
        frame = QFrame()
        self.layoutGpio = QGridLayout()
        frame.setLayout(self.layoutGpio)
        frame.setMaximumHeight(180)
        self.layoutFrameControl.addWidget(frame, 0, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to general info
        frame = QFrame()
        self.layoutGeneral = QGridLayout()
        frame.setLayout(self.layoutGeneral)
        frame.setMaximumHeight(180)
        self.layoutFrameControl.addWidget(frame, 1, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to RTC
        frame = QFrame()
        self.layoutRtc = QGridLayout()
        frame.setLayout(self.layoutRtc)
        frame.setMaximumHeight(150)
        self.layoutFrameControl.addWidget(frame, 2, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to PWM
        frame = QFrame()
        self.layoutPwm = QGridLayout()
        frame.setLayout(self.layoutPwm)
        frame.setMaximumHeight(230)
        self.layoutFrameControl.addWidget(frame, 3, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for logs and data visualization
        frame = QFrame()
        frame.setMaximumHeight(self.guiSettings['defaultLogFrameSize'])

        self.layoutLog = QGridLayout()
        frame.setLayout(self.layoutLog)
        self.gridLayout.addWidget(frame, 0, 1)
        self.listWidgets['frame'].append(frame)

        # Frame: Plots
        frame = QFrame()
        self.layoutPlots = QGridLayout()
        frame.setLayout(self.layoutPlots)

        self.gridLayout.addWidget(frame, 1, 1)

    def updateStatusBar(self, text, color = 'white'):
        """ Update the status bar state """
        self.statusBarWidget.setStyleSheet(f'color:{color};')
        self.statusBarWidget.showMessage(text)
        self.currentStatus = text

    def updateTextColor(self, color, textEdit):
        """ Update the color font of a text edit widget """
        # Define the color you want to change the text to
        color = QColor(color)

        # Get the text cursor
        cursor = textEdit.textCursor()

        # Select all the text
        cursor.select(QTextCursor.Document)

        # Create a QTextCharFormat and set the foreground color
        charFormat = QTextCharFormat()
        charFormat.setForeground(color)

        # Apply the format to the selected text
        cursor.mergeCharFormat(charFormat)

    #############################################################
    #                    START OF SLOT FUNCTIONS
    #############################################################
    def slotConnectDisconnect(self):
        """ Slot to process the connection and disconnection from the
            the serial port.
        """
        # Validate the selected port
        portDescription = self.comboBoxComPorts.currentText()
        if len(portDescription) < 1:
            self.showErrorMessage("No port detected")
            return

        # Get port name based on the selected port description
        for port in self.ports:
            if port.description == portDescription:
                portName = port.name

        # Get serial port parameters from widgets
        baud = self.comboBoxBaudrates.currentText()
        dataLen = self.settings.getSerialDataLen()
        stopBits = self.settings.getSerialStopBits()
        parity  = self.settings.getSerialParity()

        # Handle connection and disconnection states
        try:
            if self.micro.isOpen(): # Serial device is opened
                if self.micro.isMonitoring:
                    self.buttonPwmMonitor.setText("Monitor channel")
                # Close any current connection and update any widget
                self.micro.close()
                self.buttonConnectDisconnect.setText("Start connection")
                self.updateStatusBar("Serial device: disconnected")
                self.updateBorderColor(self.buttonConnectDisconnect, "#555555")
            else: # Serial device not opened
                # Open the serial port with the user
                self.micro.open(portName, baud, dataLen, parity, stopBits)
                self.buttonConnectDisconnect.setText("Stop connection")

                # Check if the microcontroller can response to a ping command
                # after a successful connection
                response = self.micro.ping()
                if response == "connected":
                    self.updateStatusBar("Serial device: connected", "#77DD77")
                    self.writeToLog("Microcontroller connected\n", "#77DD77")
                    self.updateBorderColor(self.buttonConnectDisconnect, "#77DD77")
                else:
                    self.updateStatusBar("Serial device: not responding", "red")
                    self.writeToLog("Microcontroller not responding\n", "red")
                    self.updateBorderColor(self.buttonConnectDisconnect, "#FF0000")
        except Exception as e:
            self.showErrorMessage(f'Error{e}')

    def closeEvent(self, event):
        """ Function called when the main window is closed
            by pressing the X button.
           """
        # Make sure any microcontroller instance or serial port is closed
        # properly
        if self.micro.isOpen():
            self.micro.close()
        event.accept()

    def writeToLog(self, text, color = 'white'):
        """ Write a text to the log dock/text widget """
        cursor = self.textBoxLog.textCursor()
        cursor.movePosition(cursor.End)
        format_ = QTextCharFormat()

        if self.guiSettings['currentTheme'] == 'light' and color == 'white':
            format_.setForeground(QColor('black'))
        else:
            format_.setForeground(QColor(color))
        cursor.insertText(text, format_)
        self.textBoxLog.setTextCursor(cursor)
        self.textBoxLog.ensureCursorVisible()

    def showErrorMessage(self, text):
        """ Pops up an error window  """
        # Create a message box and initialize it
        icon = QMessageBox.Icon(QMessageBox.Icon.Critical)
        messageBox = QMessageBox()
        messageBox.setIcon(icon)
        messageBox.setWindowIcon(QIcon(self.appRootPath + self.iconPaths["mainIcon"]))
        messageBox.setWindowTitle("Error")
        messageBox.setText(text)
        messageBox.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0; /* Light gray background */
                color: black; /* Text color */
                border: 2px solid #00BFFF; /* Border color */
            }
        """)

        # Add buttons to the message box
        messageBox.addButton(QMessageBox.Ok)

        # Show the message box
        messageBox.exec_()


if __name__ == '__main__':
    app = QApplication([])
    codeLink = GuiCli("MicroCLI", APP_WIDTH, APP_HIGHT)
    app.exec_()

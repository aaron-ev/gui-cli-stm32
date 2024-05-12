"""
    Author: Aaron Escoboza
    Description:  GUI application to drive STM32 peripheral
    Github: https://github.com/aaron-ev
"""

import os
import queue
from PyQt5.QtWidgets import (QApplication, QMenuBar, QToolBar, QWidget, QGridLayout,
                             QFrame, QComboBox, QFileDialog, QMessageBox,
                             QWidgetAction, QSpinBox, QStatusBar
                             )
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QColor

from appClasses import AppMainWindow, AWidgets, ASettings
from micro import Micro

import serial
import serial.tools.list_ports

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

APP_WIDTH = 920
APP_HIGHT = 880
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.axes.set_facecolor('#2E2E2E')
        self.setStyleSheet("background-color: white;")  # Black

class GuiCli(AppMainWindow):
    appVersion = {'major': '1', 'minor':'0'}
    buttonSize = (110, 30)
    defaultControlFrameSize = 320
    defaultLogFrameSize = 380
    labelPointSize = 12
    textLogHightSize = 110
    maxPlotFrameHight = 320
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
    currentTheme = 'dark'

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
        self.setStatusBar(self.statusBarWidget)
        # self.statusBarWidget.setStyleSheet("color: white;")
        font = QFont()
        font.setPointSize(10)
        self.statusBarWidget.setFont(font)
        self.statusBarWidget.setMaximumHeight(13)
        self.updateStatusBar("Serial device: disconnected", "yellow")
        # self.listWidgets['statusbar'] = self.statusBarWidget

        # Initialize menu bar
        # self.initMenuBar()
        # Toolbar
        self.initToolBar()

        # Initialize two main section:
        # 1. Section for buttons to send micro requests/cmds
        # 2. Section for logging and data visualization
        self.initLogSection()
        self.initControlSection()

        # Create queue for saving log messages
        self.logQueue = queue.Queue()

        # Display welcome message
        self.writeToLog("Welcome to Micro CLI\n\n", 'green')
        # self.writeToLog("\t\tWelcome to Micro CLI\n\n", 'green')
        # self.writeToLog("\t\t<Ready to start, select a serial port>\n", 'yellow')

        # Initialize event loop by calling show method
        self.applyTheme(self.currentTheme)
        self.show()

    def applyTheme(self, themeStr):
        theme = self.themes[themeStr.lower()]

        self.setStyleSheet(theme['mainWindow'])
        for key in self.listWidgets:
            print(key)
            for widget in self.listWidgets[key]:
                widget.setStyleSheet(theme[key])

    def initMenuBar(self):
        menuBar = QMenuBar()
        # Set default style
        # menuBar.setStyleSheet(self.styles['menuBar'])

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

    def actionInfo(self):
        self.writeToLog("Info not implemented yet\n")

    def initToolBar(self):
        toolbar = QToolBar()
        iconSize = 20
        toolbar.setIconSize(QSize(iconSize, iconSize))
        # toolbar.setStyleSheet("QToolBar QToolButton:disabled { color: inherit; }")
        self.listWidgets['toolbar'].append(toolbar)

        # Create actions for saving the log
        actionSaveLog = self.aWidgets.newAction(self, "&Save log", self.appRootPath + self.iconPaths['save'], self.actionSaveLog)
        actionSaveLog.setToolTip("<font color='back'>Save logs to a file</font>")

        # Create actions for general settings
        actionSettings = self.aWidgets.newAction(self, "&Settings", self.appRootPath + self.iconPaths['settings'], self.actionSettings)
        actionSettings.setToolTip("<font color='back'>Serial device</font>")

        # Create help action
        actionHelp = self.aWidgets.newAction(self, "&Help", self.appRootPath + self.iconPaths['help'], self.actionHelp)
        actionHelp.setToolTip("<font color='black'>General help</font>")

        # spinBoxLogFontSize = QSpinBox(self)
        # spinBoxLogFontSize.setMinimumWidth(65)
        # spinBoxLogFontSize.setMinimumHeight(25)
        # spinBoxLogFontSize.setMinimum(8)
        # spinBoxLogFontSize.setMaximum(24)
        # spinBoxLogFontSize.setValue(10)
        # spinBoxLogFontSize.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # spinBoxLogFontSize.valueChanged.connect(self.slotSpinBoxLogValueChanged)

        iconSpinBoxForLogFontSize = QIcon(self.iconPaths["fontSize"])
        # actionChangeLogFontSize = QWidgetAction(self)
        # actionChangeLogFontSize.setDefaultWidget(spinBoxLogFontSize)
        actionFontSize = self.aWidgets.newAction(self, "Font size", self.appRootPath + self.iconPaths['fontSize'], None)

        # Add all actions to the toolbar
        toolbar.addAction(actionSaveLog)
        toolbar.addAction(actionSettings)
        toolbar.addAction(actionHelp)

        # toolbar.setMaximumHeight(30)
        # toolbar.addAction(actionChangeLogFontSize)
        # toolbar.addAction(actionFontSize)

        # toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)

        self.addToolBar(toolbar)

    def actionSaveLog(self):
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
        if self.settings.exec_():
            self.writeToLog("Apply event\n")
            theme = self.settings.getTheme()
            self.applyTheme(theme)
            self.currentTheme = theme

    def slotSpinBoxLogValueChanged(self, newValue):
        font = self.textBoxLog.font()
        font.setPointSize(newValue)
        self.textBoxLog.setFont(font)

    def actionHelp(self):
        self.writeToLog(f'\nApp version v{self.appVersion["major"]}.{self.appVersion["minor"]}\n'
                        f'Author: Aaron Escoboza\n'
                        f'Github: https://github.com/aaron-ev\n',
                        'yellow'
                        )

    def showSettingsMenu(self):
        if self.settings.exec_():
            self.writeToLog("Apply event\n")

    def clearLogQueue(self):
        while not self.logQueue:
            self.logQueue.get()

    def callbackMicroReadData(self, data):
        if self.currentTheme.lower() == "dark":
            color = 'white'
        else:
            color = 'black'

        self.writeToLog(data, color)
        if self.logQueue.full():
            self.writeToLog("Can't log more data, queue is full\n", 'red')
        else:
            self.logQueue.put(data)

    def slotComboBoxComPorts(self):
        pass
        # ports = serial.tools.list_ports.comports()
        # self.comboBoxComPorts.clear()
        # for i, port in enumerate(ports):
        #     self.comboBoxComPorts.addItem("")
        #     if i == len(ports): return

    def slotComboBoxBaudrates(self):
        pass

    ##3###########################################################
    #                    START OF INIT FUNCTIONS
    ##3###########################################################
    def initLogSection(self):
        labelPort = self.aWidgets.newLabel("Port", self.labelPointSize, None)
        labelBaudRate = self.aWidgets.newLabel("Baud rate", self.labelPointSize, None)
        # labelTitlePlot = self.aWidgets.newLabel("Mat plot", self.labelPointSize, None)
        self.listWidgets['label'].append(labelPort)
        self.listWidgets['label'].append(labelBaudRate)

        # Create combobox for sandboxes
        self.comboBoxComPorts = self.aWidgets.newComboBox(self.slotComboBoxComPorts)
        self.comboBoxBaudrates = self.aWidgets.newComboBox()
        self.listWidgets['combobox'].append(self.comboBoxComPorts)
        self.listWidgets['combobox'].append(self.comboBoxBaudrates)

        # Update combobox with available ports
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.comboBoxComPorts.addItem(port.description)

        # Update combobox with supported baudrates
        for baud in self.micro.baudRates:
            self.comboBoxBaudrates.addItem(baud)
        # Set 9600 as default since it is the most common baud rate
        self.comboBoxBaudrates.setCurrentText('9600')

        # Dock: Dock for any message from serial port
        self.dockLog, self.textBoxLog = self.aWidgets.newDock("Log", "dock")
        # self.dockLog.setFixedHeight(30)
        # self.textBoxLog.setFixedHeight(50)

        self.listWidgets['text'].append(self.textBoxLog)

        # Button: Connect to serial port
        self.buttonConnectDisconnect = self.aWidgets.newButton("Start monitoring",
                                                            self.slotConnectDisconnect,
                                                            self.buttonsFont,
                                                            self.appRootPath + self.iconPaths['serialPort'], \
                                                            (220, 30),
                                                            None
                                                              )
        # Button: Refresh the serial port list
        buttonRefresh = self.aWidgets.newButton("",
                                                  self.slotButtonRefreshSerialPorts,
                                                  self.buttonsFont,
                                                  self.appRootPath + self.iconPaths['refresh'],
                                                  (30, 25),
                                                  None
                                                )
        self.listWidgets['button'].append(self.buttonConnectDisconnect)
        self.listWidgets['button'].append(buttonRefresh)

        # Matplot
        sc = MplCanvas(self, width=3, height=3, dpi=100)
        sc.axes.set_xlabel("Time(s)")
        sc.axes.set_ylabel("Voltage(V)")
        sc.axes.set_title("Signal")

        x =  list(range(0, 7))
        y  = [0, 0, 1, 1, 1,0, 0]
        sc.axes.plot(x, y)
        toolbar = NavigationToolbar(sc)

        self.layoutLog.addWidget(labelPort, 1, 0)
        self.layoutLog.addWidget(self.comboBoxComPorts, 1, 1)
        self.layoutLog.addWidget(buttonRefresh, 1, 2)
        self.layoutLog.addWidget(labelBaudRate, 1, 3)
        self.layoutLog.addWidget(self.comboBoxBaudrates, 1, 4)
        self.layoutLog.addWidget(self.buttonConnectDisconnect, 2, 0, 1, -1, alignment = Qt.AlignmentFlag.AlignCenter)
        self.layoutLog.addWidget(self.dockLog, 3, 0, 1, -1)
        # self.layoutLog.addWidget(labelTitlePlot, 4, 0, 1, -1)

        self.layoutPlots.addWidget(toolbar, 0, 0)
        self.layoutPlots.addWidget(sc, 1, 0)

    def initControlSection(self):
        labelTitleGpioRW = self.aWidgets.newLabel("GPIO Write/Read", self.labelPointSize, None)
        labelGpio= self.aWidgets.newLabel("GPIO", 10, None)
        labelPin = self.aWidgets.newLabel("Pin", 10, None)
        labelTitleGeneralInfo = self.aWidgets.newLabel("General information ", self.labelPointSize, None)
        labelTitleRtc = self.aWidgets.newLabel("RTC", self.labelPointSize, None)
        labelRtcHr = self.aWidgets.newLabel("Hr", 10, None)
        labelRctMin = self.aWidgets.newLabel("Min", 10, None)
        labelTitlePwm = self.aWidgets.newLabel("PWM", self.labelPointSize, None)
        labelPwmFreq  = self.aWidgets.newLabel("Freq", 10, None)
        labelPwmDuty  = self.aWidgets.newLabel("Duty", 10, None)
        # labelTitlePwm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labelPwmChannel = self.aWidgets.newLabel("Channel", self.labelPointSize, None)

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

        # Combobox: GPIOS
        self.comboBoxGpios = self.aWidgets.newComboBox()
        for gpio in self.micro.getSupportedGpios():
            self.comboBoxGpios.addItem(gpio.upper())

        # Line: Pin numbers
        self.comboBoxPins = self.aWidgets.newComboBox()
        minPinNumber, maxPinNumber = self.micro.getSupportedPins()
        for pinNumber in range(minPinNumber, maxPinNumber + 1):
            self.comboBoxPins.addItem(str(pinNumber).upper())

        # Button: Set to ON
        buttonPinON = self.aWidgets.newButton("On",
                                            self.slotButtonOn,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['powerOn'],
                                            self.buttonSize,
                                            None
                                            )
        # Button: Set to OFF
        buttonPinOff= self.aWidgets.newButton("Off",
                                            self.slotButtonOff,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['powerOff'],
                                            self.buttonSize,
                                            None
                                            )
        # Button: Read from GPIO pin
        buttonReadPin = self.aWidgets.newButton("Read pin",
                                            self.slotButtonReadPin,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['refresh'],
                                            self.buttonSize,
                                            None
                                            )
        # Button: Get the project version
        buttonVersion = self.aWidgets.newButton("Version",
                                            self.slotVersion,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['version'],
                                            self.buttonSize,
                                            None
                                            )
        buttonHelp = self.aWidgets.newButton("Help",
                                            self.slotHelp,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['info'],
                                            self.buttonSize,
                                            None
                                            )
        buttonHeap = self.aWidgets.newButton("Heap",
                                            self.slotHeap,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['ram'],
                                            self.buttonSize,
                                            )
        buttonTicks = self.aWidgets.newButton("Ticks",
                                            self.slotTicks,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['freq'],
                                            self.buttonSize,
                                            )
        buttonClk = self.aWidgets.newButton("Clock",
                                            self.slotClk,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['clk'],
                                            self.buttonSize,
                                            )
        buttonStats = self.aWidgets.newButton("Stats",
                                            self.slotStats,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['stats'],
                                            self.buttonSize,
                                            )
        self.textRtcHr = self.aWidgets.newLine(10)
        self.textRtcMin = self.aWidgets.newLine(10)

        buttonSetTime = self.aWidgets.newButton("Set time",
                                            self.slotRtcSetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['setTime'],
                                            self.buttonSize,
                                            )
        buttonGetTime = self.aWidgets.newButton("Get time",
                                            self.slotRtcGetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['getTime'],
                                            self.buttonSize,
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
                                            )

        # Button: Start measure
        buttonPwmMeasure = self.aWidgets.newButton("Start measure",
                                            self.slotPwmStartMeasure,
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
        self.listWidgets['button'].append(buttonPwmMeasure)
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
        self.layoutPwm.addWidget(labelPwmChannel, 3, 0)
        self.layoutPwm.addWidget(self.comboBoxPwmChannels, 3, 2, 1, -1)
        self.layoutPwm.addWidget(buttonPwmMeasure, 4, 0, 1, -1)

    def slotPwmStartMeasure(self):
        self.writeToLog("Not implemented yet :)\n", 'yellow')

    def updateBorderColor(self, style, hexBorderColor):
        border_index = style.find("border:")
        if border_index != -1:
            hash_index = style.find("#", border_index)
            if hash_index != -1:
                color_substring = style[hash_index:hash_index + 7]
                new_style = style.replace(color_substring, hexBorderColor)
                return new_style
        return style

    def slotRtcSetTime(self):
        hr = self.textRtcHr.text()
        min = self.textRtcMin.text()
        try:
             self.micro.setRtcTime(hr, min)
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotRtcGetTime(self):
        try:
             self.micro.getRtcTime()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotPwmSetFreqDuty(self):
        try:
            freq =  self.textPwmFreq.text()
            duty = self.textPwmDuty.text()
            if len(freq) < 1:
                raise Exception("Invalid frequency")
            if len(duty) < 1:
                raise Exception("Invalid duty cycle")

            self.micro.setPwmFreqDuty(int(freq), int(duty))
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonReadPin(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
             self.micro.readPin(gpio, pin)
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotVersion(self):
        try:
            self.micro.getVersion()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotHelp(self):
        try:
            self.micro.help()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotTicks(self):
        try:
            self.micro.getTicks()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotClk(self):
        try:
            self.micro.getClk()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotStats(self):
        try:
            self.micro.getStats()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotHeap(self):
        try:
            self.micro.getHeap()
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonOn(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
             self.micro.writePin(gpio, pin, True)
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonOff(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
            self.micro.writePin(gpio, pin, False)
        except Exception as e:
            self.showErrorMessage(f'{e}')

    def slotButtonRefreshSerialPorts(self):
        self.comboBoxComPorts.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBoxComPorts.addItem(port.description)

    def centerWindow(self):
        # Get the geometry of the screen
        screenGeometry = QApplication.desktop().screenGeometry()

        # Calculate the center position for the main window
        x = (screenGeometry.width() - self.width()) // 2 - 220
        y = (screenGeometry.height() - self.height()) // 2 - 180
        # Set the geometry of the main window to the center position
        self.setGeometry(x, y, self.width(), self.height())

    def initMainWindow(self, appRootPath, title, w, h):
        """ Set default main windows properties  """
        self.centerWindow()
        # self.setMinimumSize(w, h)
        self.setFixedSize(w, h)
        self.setWindowTitle(title + f" v{self.appVersion['major']}.{self.appVersion['minor']}")
        self.setWindowIcon(QIcon(appRootPath + self.iconPaths["mainIcon"]))

    def initComboBoxes(self):
        # Create combobox for sandboxes
        self.comboBoxComPorts = QComboBox()
        self.comboBoxBaudrates = QComboBox()
        # self.comboBoxSandbox.setFixedSize(self.buttonSize[0],self.buttonSize[1])
        # self.comboBoxSandbox.activated.connect(self.slotComboboxPressed)
        # self.comboBoxSandbox.setStyleSheet(self.styles['comboBox'])

        font = QFont()
        font.setPointSize(12)
        self.comboBoxComPorts.setFont(font)
        self.comboBoxBaudrates.setFont(font)

        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBoxComPorts.addItem(port.name)

        for baud in self.micro.baudRates:
            self.comboBoxBaudrates.addItem(baud)

        self.gridLayout.addWidget(self.comboBoxComPorts, 0, 0)
        self.gridLayout.addWidget(self.comboBoxBaudrates, 0, 1)
        self.gridLayout.addWidget(self.comboBoxBaudrates, 1, 0)
        self.gridLayout.addWidget(self.comboBoxBaudrates, 1, 1)

    def initLayouts(self):
        # Central widget
        self.centralWidget = QWidget()

        # Layout: Main
        self.gridLayout = QGridLayout(self.centralWidget)
        self.centralWidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralWidget)

        # Frame: Frame for holding widgets for controlling the micro
        frame = QFrame(self)
        # frame.setStyleSheet(self.defaultFrameStyle)
        # frame.setMaximumWidth(self.defaultControlFrameSize)
        self.layoutFrameControl = QGridLayout()
        frame.setLayout(self.layoutFrameControl)
        self.gridLayout.addWidget(frame, 0, 0, -1, 1)
        # self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to GPIO handling
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        # frame.setMaximumHeight(140)
        self.layoutGpio = QGridLayout()
        frame.setLayout(self.layoutGpio)
        self.layoutFrameControl.addWidget(frame, 0, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to general info
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        # frame.setMaximumWidth(self.defaultControlFrameSize)
        # frame.setMaximumHeight(180)
        self.layoutGeneral = QGridLayout()
        frame.setLayout(self.layoutGeneral)
        self.layoutFrameControl.addWidget(frame, 1, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to RTC
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        frame.setMaximumWidth(self.defaultControlFrameSize)
        # frame.setMaximumHeight(180)
        self.layoutRtc = QGridLayout()
        frame.setLayout(self.layoutRtc)
        self.layoutFrameControl.addWidget(frame, 2, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for holding widgets to PWM
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        frame.setMaximumWidth(self.defaultControlFrameSize)
        # frame.setMaximumHeight(320)
        self.layoutPwm = QGridLayout()
        frame.setLayout(self.layoutPwm)
        self.layoutFrameControl.addWidget(frame, 3, 0)
        self.listWidgets['frame'].append(frame)

        # Frame: Frame for logs and data visualization
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        frame.setMaximumHeight(self.defaultLogFrameSize)
        self.layoutLog = QGridLayout()
        frame.setLayout(self.layoutLog)
        self.gridLayout.addWidget(frame, 0, 1)
        self.listWidgets['frame'].append(frame)

        # Frame: Plots
        frame = QFrame()
        # frame.setStyleSheet(self.defaultFrameStyle)
        # frame.setMaximumHeight(self.maxPlotFrameHight)
        self.layoutPlots = QGridLayout()
        frame.setLayout(self.layoutPlots)
        self.gridLayout.addWidget(frame, 1, 1)
        frame.setStyleSheet( """ QFrame {
                                background-color: white;
                                border-radius: 10px;
                                padding: 10px;
                                }
                            """
                            )
        # frame.setContentsMargins(0, 0 ,0, 0)
        # self.listWidgets['frame'].append(frame)

    def updateStatusBar(self, text, color = 'white'):
        # Check if color is hex code
        self.statusBarWidget.setStyleSheet(f'color:{color};')
        self.statusBarWidget.showMessage(text)

    #############################################################
    #                    START OF SLOT FUNCTIONS
    #############################################################
    def slotConnectDisconnect(self):
        portDescription = self.comboBoxComPorts.currentText()
        for port in self.ports:
            if port.description == portDescription:
                portName = port.name

        if len(portName) < 1:
            self.showErrorMessage("Invalid port name")

        baud = self.comboBoxBaudrates.currentText()
        dataLen = self.settings.getSerialDataLen()
        stopBits = self.settings.getSerialStopBits()
        parity  = self.settings.getSerialParity()

        try:
            if self.micro.isOpen():
                self.micro.close()
                self.buttonConnectDisconnect.setText("Start monitoring")
                # self.writeToLog(f'Serial device: disconnected from {portName}\n', 'yellow')

                # Update button border  color
                self.prevStyle = self.buttonConnectDisconnect.styleSheet()
                newStyle = self.updateBorderColor(self.prevStyle, "#555555")
                self.buttonConnectDisconnect.setStyleSheet(newStyle)

                self.updateStatusBar("Serial device: disconnected", "yellow")

            else:
                self.micro.open(portName, baud, dataLen, parity, stopBits)
                # self.writeToLog(f'Connected to {portName}\n', 'green')
                self.buttonConnectDisconnect.setText("Stop monitoring")

                # Update button border  color
                self.prevStyle = self.buttonConnectDisconnect.styleSheet()
                newStyle = self.updateBorderColor(self.prevStyle, "#77DD77")
                self.buttonConnectDisconnect.setStyleSheet(newStyle)

                # Update status bar
                self.updateStatusBar("Serial device: connected", "#77DD77")
        except Exception as e:
            self.showErrorMessage(f'Error{e}')

    def closeEvent(self, event):
        if self.micro.isOpen():
            self.micro.close()
        print("Closing..")
        event.accept()
    def slotButtonDisconnectPort(self):
        try:
            self.micro.close()
        except Exception as e:
            print(f'Error{e}')

        self.writeToLog("Serial device: disconnected\n", 'yellow')

    def writeToLog(self, text, color = 'white'):
        cursor = self.textBoxLog.textCursor()
        cursor.movePosition(cursor.End)

        format_ = QTextCharFormat()
        format_.setForeground(QColor(color))

        cursor.insertText(text, format_)
        self.textBoxLog.setTextCursor(cursor)
        self.textBoxLog.ensureCursorVisible()

    def showErrorMessage(self, text):
        # Create a message box with information icon
        icon = QMessageBox.Icon(QMessageBox.Icon.Critical)
        msgBox = QMessageBox()
        msgBox.setIcon(icon)
        msgBox.setWindowIcon(QIcon(self.appRootPath + self.iconPaths["mainIcon"]))
        msgBox.setWindowTitle("Error")
        msgBox.setText(text)
        # Set style sheet for the message box
        msgBox.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0; /* Light gray background */
                color: black; /* Text color */
                border: 2px solid #00BFFF; /* Border color */
            }
        """)
        # Add buttons to the message box
        msgBox.addButton(QMessageBox.Ok)
        # Show the message box
        msgBox.exec_()

    def showWarningMessage(self, text, title = None):
        # Create a message box with information icon
        icon = QMessageBox.Icon(QMessageBox.Icon.Warning)
        msgBox = QMessageBox()
        msgBox.setIcon(icon)
        msgBox.setWindowIcon(QIcon(self.appRootPath + self.iconPaths["mainIcon"]))
        if title is not None:
            msgBox.setWindowTitle(title)
        else:
            msgBox.setWindowTitle("Warning")
        msgBox.setText(text)
        # Set style sheet for the message box
        msgBox.setStyleSheet("""
            QMessageBox {
                background-color: #F0F0F0; /* Light gray background */
                color: black; /* Text color */
                border: 2px solid #00BFFF; /* Border color */
            }
        """)
        # Add buttons to the message box
        msgBox.addButton(QMessageBox.Ok)
        # Show the message box
        msgBox.exec_()
if __name__ == '__main__':
    app = QApplication([])
    codeLink = GuiCli("MicroCLI", APP_WIDTH, APP_HIGHT)
    app.exec_()

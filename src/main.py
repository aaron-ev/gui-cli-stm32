"""
    Author: Aaron Escoboza
    Description:  GUI application to drive an STM32 microcontroller
"""

import os
import queue
import webbrowser
# import psutil
from PyQt5.QtWidgets import (QApplication, QMenuBar, QToolBar, QWidget, QGridLayout,
                             QFrame, QAction, QLabel, QComboBox, QPushButton, QCheckBox,
                             QTextEdit, QDockWidget, QTextBrowser, QLineEdit, QFileDialog,
                             QMessageBox, QWidgetAction, QSpinBox
                            )
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QMutex, QWaitCondition, QThread, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QColor, QPixmap
import subprocess

from appClasses import AppMainWindow, AWidgets, ASettings
from micro import Micro

APP_WIDTH = 1220
APP_HIGHT = 550

import serial
import serial.tools.list_ports

class GuiCli(AppMainWindow):
    appVersion = {'major': '1', 'minor':'0'}
    supportedBaudarates = ['9600', '115200']
    buttonSize = (220, 35)
    defaultFrameStyle = "QFrame { background-color: #1f1f1f; border-radius: 10px; border: 2px solid #333; }"
    defaultLabelStyle = "background-color: #1f1f1f; border-radius: 1px; border: 1px solid #1f1f1f;color: white"
    defaultControlFrameSize = 480
    defaultLogFrameSize = 400
    labelPointSize = 12
    defaultToolbarBg = "#1f1f1f"
    defaultToolbarColor = "white"

    def __init__(self, title, w, h):
        super().__init__()
        self.micro = Micro(callbackDataRead = self.callbackMicroReadData)
        self.appRootPath = os.getcwd()
        self.initMainWindow(self.appRootPath, title, w, h)
        self.aWidgets = AWidgets()
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(self.buttonFontSize)

        # Layouts
        self.initLayouts()

        # Menu bar
        self.initMenuBar()

        # Toolbar
        self.initToolBar()

        # General widgets
        self.initLogSection()
        self.initControlSection()

        # Create queue for saving log messages
        self.logQueue = queue.Queue()

        self.writeToLog("\t\tWelcome to Micro CLI\n\n", 'green')
        self.writeToLog("\t\t<Ready to start, select a serial port>\n", 'yellow')

        # Initialize event loop by calling show method
        self.show()

    def initMenuBar(self):
        menuBar = QMenuBar()
        # Set default style
        menuBar.setStyleSheet(self.styles['menuBar'])

        # Create bar options
        menuBarHelp = menuBar.addMenu("&Help")

        # Create actions for help
        infoAction = self.aWidgets.newAction(self, "&Info", self.appRootPath + self.iconPaths['info'], self.actionHelp)

        # Add all actions to the menubar
        menuBarHelp.addAction(infoAction)

        # Set menu bar to the main window
        self.setMenuBar(menuBar)

    def actionInfo(self):
        self.writeToLog("Info not implemented yet\n")

    def initToolBar(self):
        toolbar = QToolBar()
        iconSize = 30
        toolbar.setIconSize(QSize(iconSize, iconSize))
        toolbar.setStyleSheet("QToolBar QToolButton:disabled { color: inherit; }")

        # Create actions for saving the log
        actionSaveLog = self.aWidgets.newAction(self, "&Save log", self.appRootPath + self.iconPaths['save'], self.actionSaveLog)
        actionSaveLog.setToolTip("<font color='back'>Save logs to a file</font>")

        # Create actions for general settings
        actionSettings = self.aWidgets.newAction(self, "&Settings", self.appRootPath + self.iconPaths['settings'], self.actionSettings)
        actionSettings.setToolTip("<font color='back'>Settings</font>")

        spinBoxLogFontSize = QSpinBox(self)
        spinBoxLogFontSize.setMinimumWidth(65)
        spinBoxLogFontSize.setMinimumHeight(25)
        spinBoxLogFontSize.setMinimum(8)
        spinBoxLogFontSize.setMaximum(24)
        spinBoxLogFontSize.setValue(10)
        spinBoxLogFontSize.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinBoxLogFontSize.valueChanged.connect(self.slotSpinBoxLogValueChanged)

        iconSpinBoxForLogFontSize = QIcon(self.iconPaths["fontSize"])
        actionChangeLogFontSize = QWidgetAction(self)
        actionChangeLogFontSize.setDefaultWidget(spinBoxLogFontSize)
        actionFontSize = self.aWidgets.newAction(self, "Font size", self.appRootPath + self.iconPaths['fontSize'], None)

        # Add all actions to the toolbar
        toolbar.addAction(actionSaveLog)
        toolbar.addAction(actionSettings)
        toolbar.addAction(actionChangeLogFontSize)
        toolbar.addAction(actionFontSize)

        toolbar.setStyleSheet(f'background-color: {self.defaultToolbarBg} ; color: {self.defaultToolbarColor}')
        # toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)

        self.addToolBar(toolbar)

    def actionSaveLog(self):
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
        settingsWindow = ASettings(self.appRootPath, self.iconPaths, self.styles)
        if settingsWindow.exec_():
            self.writeToLog("user select yes\n")

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

    def clearLogQueue(self):
        while not self.logQueue:
            self.logQueue.get()

    def callbackMicroReadData(self, data):
        self.writeToLog(data)
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
        labelPort = self.aWidgets.newLabel("Port", self.labelPointSize, self.defaultLabelStyle)
        labelBaudRate = self.aWidgets.newLabel("Baud rate", self.labelPointSize, self.defaultLabelStyle)

        # Create combobox for sandboxes
        self.comboBoxComPorts = self.aWidgets.newComboBox(self.slotComboBoxComPorts)
        self.comboBoxBaudrates = self.aWidgets.newComboBox()

        # Update combobox with available ports
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.comboBoxComPorts.addItem(port.description)

        # Update combobox with supported baudrates
        for baud in self.supportedBaudarates:
            self.comboBoxBaudrates.addItem(baud)

        # Dock: Dock for any message from serial port
        self.dockLog, self.textBoxLog = self.aWidgets.newDock("Log", "dock")

        # Button: Connect to serial port
        self.buttonConnectDisconnect = self.aWidgets.newButton("Start monitoring",
                                                            self.slotConnectDisconnect,
                                                            self.buttonsFont,
                                                            self.appRootPath + self.iconPaths['serialPort'], \
                                                            None,
                                                            self.styles['button']
                                                          )
        self.layoutLog.addWidget(labelPort, 1, 0)
        self.layoutLog.addWidget(self.comboBoxComPorts, 1, 1)
        self.layoutLog.addWidget(labelBaudRate, 1, 2)
        self.layoutLog.addWidget(self.comboBoxBaudrates, 1, 3)
        self.layoutLog.addWidget(self.buttonConnectDisconnect, 2, 0, 1, -1)
        self.layoutLog.addWidget(self.dockLog, 3, 0, 1, -1)

    def initControlSection(self):
        labelTitleGpioRW = self.aWidgets.newLabel("GPIO Write/Read", self.labelPointSize, self.defaultLabelStyle)
        labelGpio= self.aWidgets.newLabel("GPIO", self.labelPointSize, self.defaultLabelStyle)
        labelPin = self.aWidgets.newLabel("Pin", self.labelPointSize, self.defaultLabelStyle)
        labelTitleGeneralInfo = self.aWidgets.newLabel("General information ", self.labelPointSize, self.defaultLabelStyle)
        labelTitleRtc = self.aWidgets.newLabel("RTC", self.labelPointSize, self.defaultLabelStyle)
        labelRtcHr = self.aWidgets.newLabel("Hr", self.labelPointSize, self.defaultLabelStyle)
        labelRctMin = self.aWidgets.newLabel("Min", self.labelPointSize, self.defaultLabelStyle)


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
                                            self.styles['button']
                                            )
        # Button: Set to OFF
        buttonPinOff= self.aWidgets.newButton("Off",
                                            self.slotButtonOff,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['powerOff'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        # Button: Read from GPIO pin
        buttonReadPin = self.aWidgets.newButton("Read pin",
                                            self.slotButtonReadPin,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['refresh'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        # Button: Get the project version
        buttonVersion = self.aWidgets.newButton("Version",
                                            self.slotVersion,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['version'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        buttonHelp = self.aWidgets.newButton("Help",
                                            self.slotHelp,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['info'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        buttonHeap = self.aWidgets.newButton("Heap",
                                            self.slotHeap,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['ram'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        buttonTicks = self.aWidgets.newButton("Ticks",
                                            self.slotTicks,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['freq'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        buttonClk = self.aWidgets.newButton("Clock",
                                            self.slotClk,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['clk'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        self.textRtcHr = self.aWidgets.newLine(12)
        # self.textRtcHr.setFixedWidth(70)
        self.textRtcMin = self.aWidgets.newLine(12)
        # self.textRtcMin.setFixedWidth(70)

        buttonSetTime = self.aWidgets.newButton("Set time",
                                            self.slotRtcSetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['setTime'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )
        buttonGetTime = self.aWidgets.newButton("Get time",
                                            self.slotRtcGetTime,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['getTime'],
                                            self.buttonSize,
                                            self.styles['button']
                                            )

        self.layoutFrameControl.addWidget(labelTitleGpioRW, 0, 0, 1, -1)
        self.layoutFrameControl.addWidget(labelGpio, 1, 0)
        self.layoutFrameControl.addWidget(self.comboBoxGpios, 1, 1)
        self.layoutFrameControl.addWidget(labelPin, 1, 2)
        self.layoutFrameControl.addWidget(self.comboBoxPins, 1, 3)
        self.layoutFrameControl.addWidget(buttonPinON, 2, 0, 1, 2)
        self.layoutFrameControl.addWidget(buttonPinOff, 2, 2, 1, 2)
        self.layoutFrameControl.addWidget(buttonReadPin, 3, 0, 1, -1)
        self.layoutFrameControl.addWidget(labelTitleGeneralInfo, 4, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonHeap, 5, 0, 1, 2)
        self.layoutFrameControl.addWidget(buttonTicks, 5, 2, 1, 2)

        self.layoutFrameControl.addWidget(buttonClk, 6, 0, 1, 2)
        self.layoutFrameControl.addWidget(buttonVersion, 6, 2, 1, 2)

        self.layoutFrameControl.addWidget(buttonHelp, 7, 0, 1, 2)
        self.layoutFrameControl.addWidget(labelTitleRtc, 8, 0, 1, -1)
        self.layoutFrameControl.addWidget(labelRtcHr, 9, 0)
        self.layoutFrameControl.addWidget(self.textRtcHr, 9, 1)
        self.layoutFrameControl.addWidget(labelRctMin, 9, 2)
        self.layoutFrameControl.addWidget(self.textRtcMin, 9, 3)
        self.layoutFrameControl.addWidget(buttonSetTime, 10, 0, 1, 2)
        self.layoutFrameControl.addWidget(buttonGetTime, 10, 2, 1, 2)

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
            self.showErrorMessage(f'Error: {e}')

    def slotRtcGetTime(self):
        try:
             self.micro.getRtcTime()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotButtonReadPin(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
             self.micro.readPin(gpio, pin)
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotVersion(self):
        try:
            self.micro.getVersion()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotHelp(self):
        try:
            self.micro.help()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotTicks(self):
        try:
            self.micro.getTicks()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotClk(self):
        try:
            self.micro.getClk()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotHeap(self):
        try:
            self.micro.getHeap()
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotButtonOn(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
             self.micro.writePin(gpio, pin, True)
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

    def slotButtonOff(self):
        gpio = self.comboBoxGpios.currentText()
        pin = self.comboBoxPins.currentText()
        try:
            self.micro.writePin(gpio, pin, False)
        except Exception as e:
            self.showErrorMessage(f'Error: {e}')

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
        self.setWindowTitle(title + f" v{self.appVersion['major']}.{self.appVersion['minor']} BETA underdevelopment")
        self.setWindowIcon(QIcon(appRootPath + self.iconPaths["mainIcon"]))
        self.setStyleSheet(self.styles['mainWindow'])

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

        for baud in self.supportedBaudarates:
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

        # Frame: Frame for all buttons (any kind of control)
        frame = QFrame()
        frame.setStyleSheet(self.defaultFrameStyle)
        frame.setMaximumWidth(self.defaultControlFrameSize)
        self.layoutFrameControl = QGridLayout()
        frame.setLayout(self.layoutFrameControl)
        self.gridLayout.addWidget(frame, 0, 0)

        # Frame: Frame for logs and data visualization
        frame = QFrame()
        frame.setStyleSheet(self.defaultFrameStyle)
        frame.setMinimumWidth(self.defaultLogFrameSize)
        self.layoutLog = QGridLayout()
        frame.setLayout(self.layoutLog)
        self.gridLayout.addWidget(frame, 0, 1)

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
        try:
            if self.micro.isOpen():
                self.micro.close()
                self.buttonConnectDisconnect.setText("Start monitoring")
                self.writeToLog(f'Disconnected from {portName}\n', 'yellow')

                # Update button border  color
                self.prevStyle = self.buttonConnectDisconnect.styleSheet()
                newStyle = self.updateBorderColor(self.prevStyle, "#555555")
                self.buttonConnectDisconnect.setStyleSheet(newStyle)
            else:
                self.micro.open(portName, baud)
                self.writeToLog(f'Connected to {portName}\n', 'green')
                self.buttonConnectDisconnect.setText("Stop monitoring")

                # Update button border  color
                self.prevStyle = self.buttonConnectDisconnect.styleSheet()
                newStyle = self.updateBorderColor(self.prevStyle, "#77DD77")
                self.buttonConnectDisconnect.setStyleSheet(newStyle)
        except Exception as e:
            self.showErrorMessage(f'Error {e}')

    def slotButtonDisconnectPort(self):
        try:
            self.micro.close()
        except Exception as e:
            print(f'Error {e}')

        self.writeToLog("Disconnected\n", 'yellow')

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

if __name__ == '__main__':
    app = QApplication([])
    codeLink = GuiCli("GUI CLI", APP_WIDTH, APP_HIGHT)
    app.exec_()

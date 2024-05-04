"""
    Author: Aaron Escoboza
    User: escoaa1
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

from appClasses import AppMainWindow, AWidgets
from micro import Micro

APP_WIDTH = 1020
APP_HIGHT = 420

import serial
import serial.tools.list_ports

class GuiCli(AppMainWindow):
    appVersion = {'major': '1', 'minor':'0'}
    supportedBaudarates = ['9600', '115200']
    buttonSize = (250,30)
    defaultFrameStyle = "QFrame { background-color: #1f1f1f; border-radius: 10px; border: 2px solid #333; }"
    defaultLabelStyle = "background-color: #1f1f1f; border-radius: 1px; border: 1px solid #1f1f1f;color: white"
    defaultControlFrameSize = 275
    defaultLogFrameSize = 400
    labelPointSize = 12

    def __init__(self, title, w, h):
        super().__init__() # Allows the use of abstract class to work
        self.micro = Micro(callbackDataRead = self.callbackMicroReadData)
        self.appRootPath = os.getcwd()
        self.initMainWindow(self.appRootPath, title, w, h)
        self.aWidgets = AWidgets()
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(self.buttonFontSize)

        # Layouts
        self.initLayouts()

        # General widgets
        self.initLogSection()
        self.initControlSection()
        # Comboboxes
        # self.initComboBoxes()

        # Initialize event loop by calling show method
        self.show()

    def callbackMicroReadData(self, data):
        self.writeToLog(data)

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
        labelSerialConfig = self.aWidgets.newLabel("Serial configuration", self.labelPointSize, self.defaultLabelStyle)

        # Create combobox for sandboxes
        self.comboBoxComPorts = self.aWidgets.newComboBox(self.slotComboBoxComPorts)
        self.comboBoxBaudrates = self.aWidgets.newComboBox()

        # Update combobox with available ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
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
        self.layoutLog.addWidget(labelSerialConfig, 0, 0, 1, -1)
        self.layoutLog.addWidget(self.comboBoxComPorts, 1, 0)
        self.layoutLog.addWidget(self.comboBoxBaudrates, 1, 1)
        self.layoutLog.addWidget(self.buttonConnectDisconnect, 2, 0, 1, -1)
        self.layoutLog.addWidget(self.dockLog, 3, 0, 1, -1)

    def initControlSection(self):
        # labelGpio = self.aWidgets.newLabel("GPIOx PORT", self.labelPointSize, self.defaultLabelStyle)
        # labelPinNumber = self.aWidgets.newLabel("Pin number", self.labelPointSize, self.defaultLabelStyle)

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
        buttonPinON = self.aWidgets.newButton("ON",
                                            self.slotButtonOn,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        # Button: Set to OFF
        buttonPinOff= self.aWidgets.newButton("OFF",
                                            self.slotButtonOff,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        # Button: Get the project version
        buttonVersion = self.aWidgets.newButton("Version",
                                            self.slotVersion,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        buttonHelp = self.aWidgets.newButton("Help",
                                            self.slotHelp,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        buttonHeap = self.aWidgets.newButton("heap",
                                            self.slotHeap,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        buttonTicks = self.aWidgets.newButton("ticks",
                                            self.slotTicks,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )
        buttonClk = self.aWidgets.newButton("CLK",
                                            self.slotClk,
                                            self.buttonsFont,
                                            self.appRootPath + self.iconPaths['serialPort'],
                                            None,
                                            self.styles['button']
                                            )

        # self.layoutFrameControl.addWidget(labelGpio, 0, 0)
        # self.layoutFrameControl.addWidget(labelPinNumber, 0, 1)
        self.layoutFrameControl.addWidget(self.comboBoxGpios, 0, 0)
        self.layoutFrameControl.addWidget(self.comboBoxPins, 0, 1)
        self.layoutFrameControl.addWidget(buttonPinON, 1, 0)
        self.layoutFrameControl.addWidget(buttonPinOff, 1, 1)
        self.layoutFrameControl.addWidget(buttonVersion, 2, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonHelp, 3, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonHeap, 4, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonTicks, 5, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonClk, 6, 0, 1, -1)
        self.layoutFrameControl.addWidget(buttonVersion, 7, 0, 1, -1)

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
        self.setMinimumSize(w, h)
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
        frame.setMinimumWidth(self.defaultControlFrameSize)
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
        portName = self.comboBoxComPorts.currentText()
        if len(portName) < 1:
            self.showErrorMessage("Invalid port name")

        baud = self.comboBoxBaudrates.currentText()
        try:
            if self.micro.isOpen():
                self.micro.close()
                self.buttonConnectDisconnect.setText("Start monitoring")
                self.writeToLog(f'Disconnected from {portName}\n', 'yellow')
            else:
                self.micro.open(portName, baud)
                self.writeToLog(f'Connected to {portName}\n', 'yellow')
                self.buttonConnectDisconnect.setText("Stop monitoring")
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

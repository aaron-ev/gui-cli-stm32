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

from serialDev import SerialDev
from appClasses import AppMainWindow, AWidgets
from micro import Micro

APP_WIDTH = 1020
APP_HIGHT = 420

class GuiCli(AppMainWindow):
    appVersion = {'major': '1', 'minor':'0'}
    supportedBaudarates = ['9600', '115200']
    buttonSize = (250,30)

    def __init__(self, title, w, h):
        super().__init__() # Allows the use of abstract class to work
        self.micro = Micro()
        self.appRootPath = os.getcwd()
        self.initMainWindow(self.appRootPath, title, w, h)
        self.serialDev = SerialDev()
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


    def slotComboBoxComPorts(self):
        pass
    def slotComboBoxBaudrates(self):
        pass

    ##3###########################################################
    #                    START OF INIT FUNCTIONS
    ##3###########################################################
    def initLogSection(self):
        # Create combobox for sandboxes
        self.comboBoxComPorts = self.aWidgets.newComboBox(self.slotComboBoxComPorts)
        self.comboBoxBaudrates = self.aWidgets.newComboBox(self.slotComboBoxBaudrates)

        # Update combobox with available ports
        ports = self.serialDev.listPorts()
        for port in ports:
            self.comboBoxComPorts.addItem(port.name)

        # Update combobox with supported baudrates
        for baud in self.supportedBaudarates:
            self.comboBoxBaudrates.addItem(baud)


        # Dock: Dock for any message from serial port
        self.dockLog, self.textBoxLog = self.aWidgets.newDock("Log", "dock")

        # Button: Connect to serial port
        buttonConnectToPort = self.aWidgets.newButton("Connect",
                                                      self.slotButtonConnectPort,
                                                      self.buttonsFont,
                                                      self.iconPaths['serialPort'], \
                                                      None,
                                                      self.styles['button']
                                                      )
        # Button: Disconnect from serial port
        buttonDisconnectFromPort = self.aWidgets.newButton("Disconnect",
                                                      self.slotButtonDisconnectPort,
                                                      self.buttonsFont,
                                                      self.iconPaths['serialPort'], \
                                                      None,
                                                      self.styles['button']
                                                      )

        self.layoutGrid.addWidget(self.comboBoxComPorts, 0, 2)
        self.layoutGrid.addWidget(self.comboBoxBaudrates, 0, 3)
        self.layoutGrid.addWidget(buttonConnectToPort, 1, 2)
        self.layoutGrid.addWidget(buttonDisconnectFromPort, 1, 3)
        self.layoutGrid.addWidget(self.dockLog, 2, 2, 1, -1)

    def initControlSection(self):

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
                                            self.slotButtonDisconnectPort,
                                            self.buttonsFont,
                                            self.iconPaths['serialPort'], \
                                            None,
                                            self.styles['button']
                                            )
        # Button: Set to OFF
        buttonPinOff= self.aWidgets.newButton("OFF",
                                            self.slotButtonDisconnectPort,
                                            self.buttonsFont,
                                            self.iconPaths['serialPort'], \
                                            None,
                                            self.styles['button']
                                            )

        self.layoutGrid.addWidget(self.comboBoxGpios, 2, 0)
        self.layoutGrid.addWidget(self.comboBoxPins, 2, 1)
        self.layoutGrid.addWidget(buttonPinON, 3, 0)
        self.layoutGrid.addWidget(buttonPinOff, 3, 1)

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
        self.setWindowTitle(title + f"v{self.appVersion['major']}.{self.appVersion['minor']} BETA underdevelopment")
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

        ports = self.serialDev.listPorts()
        for port in ports:
            self.comboBoxComPorts.addItem(port.name)

        for baud in self.supportedBaudarates:
            self.comboBoxBaudrates.addItem(baud)

        self.layoutGrid.addWidget(self.comboBoxComPorts, 0, 0)
        self.layoutGrid.addWidget(self.comboBoxBaudrates, 0, 1)
        self.layoutGrid.addWidget(self.comboBoxBaudrates, 1, 0)
        self.layoutGrid.addWidget(self.comboBoxBaudrates, 1, 1)

    def initLayouts(self):
        # Central widget
        self.centralWidget = QWidget()
        # Layout: Main
        self.layoutGrid = QGridLayout(self.centralWidget)
        self.centralWidget.setLayout(self.layoutGrid)
        self.setCentralWidget(self.centralWidget)

        self.centralWidget.setLayout(self.layoutGrid)
        self.setCentralWidget(self.centralWidget)

    #############################################################
    #                    START OF SLOT FUNCTIONS
    #############################################################
    def slotButtonConnectPort(self):
        portName = self.comboBoxComPorts.currentText()
        if len(portName) < 1:
            self.showErrorMessage("Invalid port name")

        baud = self.comboBoxBaudrates.currentText()
        try:
            self.serialDev.open(portName, baud)
            self.writeToLog(f'Connected to {portName}\n')
        except Exception as e:
            self.showErrorMessage(f'Error {e}')

    def slotButtonDisconnectPort(self):
        self.serialDev.close()

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
    codeLink = GuiCli("GuiCli", APP_WIDTH, APP_HIGHT)
    app.exec_()

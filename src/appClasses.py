from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton,  QLineEdit, QFileDialog,
                             QMainWindow, QDialog, QHBoxLayout, QWidget, QTextEdit,QComboBox,QDockWidget, QAction
                            )
from PyQt5.QtCore import Qt, QThread, QSize

from winotify import Notification

import os
from pydub import AudioSegment
from pydub.playback import play as playAudio
import threading

class AppMainWindow(QMainWindow):

    iconPaths = {
                    "stop": "/img/stop.png",
                    "folder":"/img/folder.png",
                    "build":"/img/build.png",
                    "remotePc":"/img/remotePc.png",
                    "warning":"/img/warning.png",
                    "features":"/img/features.png",
                    "info":"/img/info.png",
                    "save":"/img/save.png",
                    "openFolder":"/img/openFolder.png",
                    "zip":"/img/zip.png",
                    "readOnly":"/img/readOnly.png",
                    "report":"/img/report.png",
                    "play":"/img/play.png",
                    "settings":"/img/settings.png",
                    "resync":"/img/resync.png",
                    "mainIcon":"/img/icon.ico",
                    "onImage":"/img/on.png",
                    "offImage":"/img/off.png",
                    "compare":"/img/compare.png",
                    "vscode":"/img/vscode.png",
                    "copy":"/img/copy.png",
                    "fontSize":"/img/fontSize.png",
                    "serialPort":"/img/serialPort.png",
                    "stats":"/img/stats.png",
                    "circularClock":"/img/circularCLock.png",
                    "clk":"/img/clk.png",
                    "version":"/img/version.png",
                    "powerOn":"/img/powerOn.png",
                    "powerOff":"/img/powerOff.png",
                    "refresh":"/img/refresh.png",
                    "ram":"/img/ram.png",
                    "freq":"/img/freq.png",
                    "setTime":"/img/setTime.png",
                    "getTime":"/img/getTime.png",
                }
    styles = {
                "button":"""
                             QPushButton {
                                 background-color: #2E2E2E; /* Dark gray background */
                                 color: white; /* Text color */
                                 border: 2px solid #555555; /* Nice blue border color */
                                 border-radius: 5px; /* Rounded corners */
                                 padding: 5px 10px; /* Padding */
                             }
                             QPushButton:hover {
                                 background-color: #3A3A3A; /* Darker gray background on hover */
                             }
                             QPushButton:pressed {
                                 background-color: #4A4A4A; /* Pressed color */
                             }
                           """,
                "stopButton":"""
                                QPushButton {
                                    background-color: #FF6961; /* Red background */
                                    color: white; /* Text color */
                                    border: 2px solid #555555; /* Red border color */
                                    border-radius: 5px; /* Rounded corners */
                                    padding: 5px 10px; /* Padding */
                                }
                                QPushButton:hover {
                                    background-color: #FF8C85; /* Lighter red background on hover */
                                    border-color: #3A3A3A; /* Lighter red border color on hover */
                                }
                                QPushButton:pressed {
                                    background-color: #D6453D; /* Darker red background when pressed */
                                    border-color: #D6453D; /* Darker red border color when pressed */
                                }
                            """,
                "menuBar": """
                                QMenuBar {
                                    background-color: #2C2C2C; /* Black background */
                                    color: white; /* White text color */
                                }

                                QMenuBar::item {
                                    background-color: #2C2C2C; /* Black background for menu items */
                                    color: #FFFFFF; /* White text color for menu items */
                                    padding: 4px 8px; /* Padding around menu items */
                                }

                                QMenuBar::item:selected {
                                    background-color: #2C2C2C ; /* Dark gray background for selected menu items */
                                }

                                QMenu {
                                    background-color: #2C2C2C; /* Black background for submenus */
                                    color: #FFFFFF; /* White text color for submenus */
                                    border: 1px solid #3A3A3A; /* White border for submenus */
                                }

                                QMenu::item {
                                    background-color: #2C2C2C; /* Black background for submenu items */
                                    color: #FFFFFF; /* White text color for submenu items */
                                }

                                QMenu::item:selected {
                                    background-color: #333333; /* Dark gray background for selected submenu items */
                                }
                                """,
                "lineEdit": """
                                QLineEdit {
                                    background-color: #1f1f1f; /* Dark gray background */
                                    color: white; /* Text color */
                                    border: 2px solid #555555; /* Nice blue border color */
                                    border-radius: 5px; /* Rounded corners */
                                    padding: 5px 10px; /* Padding */
                                }
                                QLineEdit:hover {
                                    background-color: #3A3A3A; /* Darker gray background on hover */
                                }
                            """,
                "mainWindow":"""
                            QMainWindow {
                                background-color: #1f1f1f; /* Dark gray background */
                                color: blue; /* Text color */
                            }
                            QMainWindow::separator {
                                background-color: red; /* Change the color here */
                                height: 1px; /* Set the height of the separator */
                                margin: 2px; /* Set margin to zero */
                            }
                           """,
                "comboBox": """ background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Default text color */
                                text-align: center;
                           """,
                "dialog":"""
                            QDialog {
                                background-color: #1f1f1f; /* Dark gray background */
                                color: white; /* Text color */
                            }
                        """,
                "running": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid #0023c9; /* Nice blue border color */
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "stopped": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid #F9ED69;
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "error": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid #F38181;
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "idle": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid #555555;
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "success": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid green;
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "unknown": """
                                QLineEdit {
                                background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Text color */
                                border: 2px solid pink;
                                border-radius: 5px; /* Rounded corners */
                                padding: 5px 10px; /* Padding */
                                }
                            """,
                "line": """
                            QLineEdit {
                            background-color: #2E2E2E; /* Dark gray background */
                            color: white; /* Text color */
                            border: 2px solid #4a2469;
                            border-radius: 5px; /* Rounded corners */
                            padding: 5px 10px; /* Padding */
                            }
                         """,
                }
    buttonFontSize = 12
    notiSoundPath = "audio/notification.wav"

    def __init__(self):
        super().__init__() # Allows the use of abstract class to work
        # Main font for all buttons
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(self.buttonFontSize)

class AWidgets():
    bgTextBoxes = '#2C2C2C'
    colorTextBoxes = 'white'
    styles = {"line": """
                        QLineEdit {
                        background-color: #2E2E2E; /* Dark gray background */
                        color: white; /* Text color */
                        border: 2px solid #555555;
                        border-radius: 5px; /* Rounded corners */
                        padding: 5px 10px; /* Padding */
                        }
                     """,
                "comboBox": """ background-color: #2E2E2E; /* Dark gray background */
                                color: white; /* Default text color */
                                text-align: center;
                           """
            }
    defaultLabelColor = 'white'
    defaultDockBg = "#333333"
    defaultDockColor = "white"

    def __init__(self):
        pass

    def newLine(self, pointSize, bg = 'black', color = 'black'):
        font = QFont()
        font.setFamily('Helvetica')
        font.setPointSize(pointSize)
        textEdit = QLineEdit()
        textEdit.setFixedSize(125, 30)
        textEdit.setStyleSheet(f'background-color: {bg}; color: {color};')
        textEdit.setFont(font)
        textEdit.geometry()
        return textEdit

    def newLabel(self, text, pointSize, style = None):
        label = QLabel(text, self)
        label.setStyleSheet(f'color: {self.defaultLabelColor}')
        font = QFont()
        font.setPointSize(pointSize)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if style is not None:
            label.setStyleSheet(style)
        label.maximumHeight(20)
        return label

    def newButton(self, text, slot = None, font = None, iconPath = None, size = None, style = None):
        button = QPushButton(text)
        button.setStyleSheet("color: black; background-color: white;" )
        if slot is not None:
            button.clicked.connect(slot)
        if font is not None:
            button.setFont(font)
        if iconPath is not None:
            button.setIcon(QIcon(iconPath))
        if size is not None:
            button.setFixedSize(size[0], size[1])
        if style is not None:
            button.setStyleSheet(style)
        return button

    def newTextBox(self, pointSize = None):
        font = QFont()
        if pointSize is not None:
            font.setPointSize(pointSize)
        textBox = QTextEdit()
        textBox.setStyleSheet(f'background-color: {self.bgTextBoxes}; color: {self.colorTextBoxes};')
        textBox.setFont(font)
        return textBox

    def newLine(self, pointSize = None):
        font = QFont()
        if pointSize is not None:
            font.setPointSize(pointSize)
        line = QLineEdit()
        line.setStyleSheet(self.styles['line'])
        line.setFont(font)
        return line

    def newComboBox(self, slot = None):
        comboBox = QComboBox()
        # comboBox.setFixedSize(250, 30)
        if slot is not None:
            comboBox.currentIndexChanged.connect(slot)
        comboBox.setStyleSheet(self.styles['comboBox'])
        font = QFont()
        font.setPointSize(12)
        comboBox.setFont(font)
        return comboBox

    def newDock(self, title, name):
        dock = QDockWidget(title)
        dock.setObjectName(name)
        dock.setTitleBarWidget(QWidget(None)) # Remove title bar

        font = QFont()
        font.setPointSize(10)
        textBoxLog = QTextEdit()
        textBoxLog.setStyleSheet(f'background-color: {self.bgTextBoxes}; color: {self.colorTextBoxes};')
        textBoxLog.setFont(font)
        dock.setWidget(textBoxLog)
        dock.setStyleSheet(f'background-color: {self.defaultDockBg}; color: {self.defaultDockColor};')
        return (dock, textBoxLog)

    def newLabel(self, text, pointSize, style = None):
        label = QLabel(text)
        label.setStyleSheet(f'color: {self.defaultLabelColor}')
        font = QFont()
        font.setPointSize(pointSize)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if style is not None:
            label.setStyleSheet(style)
        return label

    def newAction(self, parent, text = None, iconPath = None, slot = None):
        if text is not None:
            action = QAction(text, parent)
        else:
            action = QAction(parent)
        if iconPath is not None:
            action.setIcon(QIcon(iconPath))
        if slot is not None:
            action.triggered.connect(slot)
        return action

class ASettings(QDialog):
    maxSize = (360, 160)
    newFolderBsClient = None
    newCompilationResultsDir = None
    defaultLabelStyle = "background-color: #1f1f1f; border-radius: 1px; border: 1px solid #1f1f1f;color: white"
    labelPointSize = 12

    def initWindow(self, appRootPath, iconPaths, styles):
        self.setWindowTitle("Settings")
        self.setStyleSheet(styles['dialog'])
        self.setWindowIcon(QIcon(appRootPath + iconPaths['settings']))
        self.setFixedSize(self.maxSize[0], self.maxSize[1])

    def initFonts(self):
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(10)

    def __init__(self, appRootPath, iconPaths, styles):
        super().__init__()
        self.iconPaths = iconPaths
        self.appRootPath = appRootPath
        self.initFonts()
        self.initWindow(appRootPath, iconPaths, styles)
        # self.config = config
        aWidgets = AWidgets()
        buttonApply = QPushButton("&Apply")
        buttonCancel = QPushButton("&Cancel")
        buttonApply.setFixedWidth(140)
        buttonCancel.setFixedWidth(140)
        buttonApply.clicked.connect(self.apply)
        buttonCancel.clicked.connect(self.cancel)

        # Create labels
        labelSerialConfig = aWidgets.newLabel("Serial configuration", self.labelPointSize, self.defaultLabelStyle)
        labelDataLen = aWidgets.newLabel("Data length", self.labelPointSize, self.defaultLabelStyle)
        labelStopBits = aWidgets.newLabel("Stop bits", self.labelPointSize, self.defaultLabelStyle)

        self.comboboxDataLen = aWidgets.newComboBox()
        self.comboboxStopBits = aWidgets.newComboBox()

        # Set supported data lengths
        self.comboboxDataLen.addItem("8")
        self.comboboxDataLen.addItem("7")

        # Set supported stop bits
        self.comboboxStopBits.addItem("1")
        self.comboboxStopBits.addItem("2")

        # Initialize notifications for sending on success or failure
        self.initNotifications()
        gridLayout = QGridLayout()
        self.setLayout(gridLayout)
        # gridLayout.setContentsMargins(10, 10, 1, 1)

        # Create layout and add widgets to it
        gridLayout.addWidget(labelSerialConfig, 0, 0, 1, -1)
        gridLayout.addWidget(labelDataLen, 1, 0)
        gridLayout.addWidget(self.comboboxDataLen, 1, 1)
        gridLayout.addWidget(labelStopBits, 2, 0)
        gridLayout.addWidget(self.comboboxStopBits, 2, 1)
        gridLayout.addWidget(buttonApply, 3, 0)
        gridLayout.addWidget(buttonCancel, 3, 1)

    def initNotifications(self):
        pass
        # # Create label for enable notifications and its on/off image
        # self.labelNoti = self.createLabel("Enable notifications", 12)
        # self.notiStateImage = self.createLabel("", 12)

        # # Current size is needed to do a proper scalation
        # self.notiLabelSize = self.notiStateImage.size()

        # # Map slot to get new mouse event
        # self.notiStateImage.mousePressEvent = self.updateNotiState

        # # Check if notification value is already saved
        # regEnableNoti = self.config.read("notification", "isenable").lower()
        # if regEnableNoti is ["none"]:
        #     regEnableNoti = "false"

        # # Set new image according to reg state
        # onImage = self.appRootPath + self.iconPaths['onImage']
        # offImage = self.appRootPath + self.iconPaths['offImage']
        # newImage = onImage if regEnableNoti == "true" else offImage
        # pixmap = QPixmap(newImage)
        # self.notiStateImage.setPixmap(pixmap.scaled(self.notiLabelSize * 0.1, Qt.KeepAspectRatio, \
        #                               Qt.SmoothTransformation))

        # # Update local notification reg state
        # self.notiRegState = regEnableNoti

    def apply(self):
        # self.saveSettings()
        self.accept()

    def saveSettings(self):
        pass
        # # Save BS client path
        # if self.newFolderBsClient is not None:
        #     self.config.write("paths", "bsclient", self.newFolderBsClient)

        # # Save compilation results path
        # if self.newCompilationResultsDir is not None:
        #     self.config.write("paths", "compilationresults", self.newCompilationResultsDir)

        # # Save notification enable/disable flag
        # if self.notiRegState is not None:
        #     self.config.write("notification", "isenable", self.notiRegState)

    def cancel(self):
        self.reject()

    def updateNotiState(self, event):
        if event is not None and event.button() != Qt.LeftButton:
            return

        if self.notiRegState == "true":
            self.notiRegState = "false"
            newImage = self.appRootPath + self.iconPaths["offImage"]
        else:
            self.notiRegState = "true"
            newImage = self.appRootPath + self.iconPaths["onImage"]
        pixmap = QPixmap(newImage)
        # scaled_pixmap = pixmap.scaled(self.notificationEnableStateImage.size() * 0.1, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.notiStateImage.setPixmap(pixmap.scaled(self.notiLabelSize * 0.1, Qt.KeepAspectRatio, Qt.SmoothTransformation))

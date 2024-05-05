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


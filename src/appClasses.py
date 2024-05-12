from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton,  QLineEdit, QFileDialog,
                             QMainWindow, QDialog, QHBoxLayout, QWidget, QTextEdit,QComboBox,QDockWidget, QAction, QTabWidget
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
                    "help":"/img/help.png",
                }
    buttonFontSize = 10
    notiSoundPath = "audio/notification.wav"

    darkTheme = {
                "mainWindow":
                            """
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
                "button":
                            """
                                QPushButton {
                                    background-color: #2E2E2E;
                                    color: white;
                                    border: 2px solid #555555;
                                    border-radius: 5px; /* Rounded corners */
                                    padding: 4px 8px; /* Padding */
                                }
                                QPushButton:hover {
                                    background-color: #3A3A3A; /* Darker gray background on hover */
                                }
                                QPushButton:pressed {
                                    background-color: #4A4A4A; /* Pressed color */
                                }
                            """,
                "menuBar":
                            """ QMenuBar {
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
                            """,
                "menu":
                            """ QMenu {
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
                "line":
                            """ QLineEdit {
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
                "combobox":
                            """
                                QComboBox {
                                    background-color: #1f1f1f; /* Dark gray */
                                    color: white; /* Default text */
                                    text-align: center;
                                }
                                QComboBox::down-arrow {
                                    background-color: #1f1f1f; /* Dark gray */
                                }
                            """,
                "dialog":
                            """QDialog {
                                background-color: #1f1f1f; /* Dark gray background */
                                color: white; /* Text color */
                                }
                            """,
                "label":
                            """ QLabel {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid  #1f1f1f;
                                }
                            """,
                "text":
                            """ QTextEdit {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid #1f1f1f;
                                }
                            """,
                "dock":
                            """  QDockWidget {
                                background-color: #1f1f1f;
                                color: white;
                                }
                            """,
                "frame":
                            """ QFrame {
                                background-color: #1f1f1f;
                                border: 1px solid #555555;
                                border-radius: 10px;
                                padding: 10px;
                                }
                            """,
                "toolbar":
                            """
                                /* ToolBar */
                                QToolBar {
                                    background-color: #2C2C2C;
                                }
                                /* ToolButton */
                                QToolBar QToolButton {
                                    background-color: #f0f0f0;
                                    color: #000000;
                                    border: 1px solid #000000;
                                    padding: 5px 10px;
                                }
                                QToolBar QToolButton:hover {
                                    background-color: #d0d0d0;
                                }
                            """
                }

    darkTheme = {
                "mainWindow":
                            """
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
                "button":
                            """
                                QPushButton {
                                    background-color: #2E2E2E;
                                    color: white;
                                    border: 2px solid #555555;
                                    border-radius: 5px; /* Rounded corners */
                                    padding: 4px 8px; /* Padding */
                                }
                                QPushButton:hover {
                                    background-color: #3A3A3A; /* Darker gray background on hover */
                                }
                                QPushButton:pressed {
                                    background-color: #4A4A4A; /* Pressed color */
                                }
                            """,
                "menuBar":
                            """ QMenuBar {
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
                            """,
                "menu":
                            """ QMenu {
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
                "line":
                            """ QLineEdit {
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
                "combobox":
                            """
                                QComboBox {
                                    background-color: #1f1f1f; /* Dark gray */
                                    color: white; /* Default text */
                                    text-align: center;
                                }
                                QComboBox::down-arrow {
                                    background-color: #1f1f1f; /* Dark gray */
                                }
                            """,
                "dialog":
                            """QDialog {
                                background-color: #1f1f1f; /* Dark gray background */
                                color: white; /* Text color */
                                }
                            """,
                "label":
                            """ QLabel {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid  #1f1f1f;
                                }
                            """,
                "text":
                            """ QTextEdit {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid #1f1f1f;
                                }
                            """,
                "dock":
                            """  QDockWidget {
                                background-color: #1f1f1f;
                                color: white;
                                }
                            """,
                "frame":
                            """ QFrame {
                                background-color: #1f1f1f;
                                border: 1px solid #555555;
                                border-radius: 10px;
                                padding: 10px;
                                }
                            """,
                "toolbar":
                            """
                                /* ToolBar */
                                QToolBar {
                                    background-color: #2C2C2C;
                                }
                                /* ToolButton */
                                QToolBar QToolButton {
                                    background-color: #f0f0f0;
                                    color: #000000;
                                    border: 1px solid #000000;
                                    padding: 5px 10px;
                                }
                                QToolBar QToolButton:hover {
                                    background-color: #d0d0d0;
                                }
                            """
                }

    lightTheme = {
                "mainWindow":
                            """
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
                "button":
                            """
                                QPushButton {
                                    background-color: #2E2E2E;
                                    color: white;
                                    border: 2px solid #555555;
                                    border-radius: 5px; /* Rounded corners */
                                    padding: 4px 8px; /* Padding */
                                }
                                QPushButton:hover {
                                    background-color: #3A3A3A; /* Darker gray background on hover */
                                }
                                QPushButton:pressed {
                                    background-color: #4A4A4A; /* Pressed color */
                                }
                            """,
                "menuBar":
                            """ QMenuBar {
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
                            """,
                "menu":
                            """ QMenu {
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
                "line":
                            """ QLineEdit {
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
                "combobox":
                            """
                                QComboBox {
                                    background-color: #1f1f1f; /* Dark gray */
                                    color: white; /* Default text */
                                    text-align: center;
                                }
                                QComboBox::down-arrow {
                                    background-color: #1f1f1f; /* Dark gray */
                                }
                            """,
                "dialog":
                            """QDialog {
                                background-color: #1f1f1f; /* Dark gray background */
                                color: white; /* Text color */
                                }
                            """,
                "label":
                            """ QLabel {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid  #1f1f1f;
                                }
                            """,
                "text":
                            """ QTextEdit {
                                background-color: #1f1f1f;
                                color: white;
                                border: 1px solid #1f1f1f;
                                }
                            """,
                "dock":
                            """  QDockWidget {
                                background-color: #1f1f1f;
                                color: white;
                                }
                            """,
                "frame":
                            """ QFrame {
                                background-color: #1f1f1f;
                                border: 1px solid #555555;
                                border-radius: 10px;
                                padding: 10px;
                                }
                            """,
                "toolbar":
                            """
                                /* ToolBar */
                                QToolBar {
                                    background-color: #2C2C2C;
                                }
                                /* ToolButton */
                                QToolBar QToolButton {
                                    background-color: #f0f0f0;
                                    color: #000000;
                                    border: 1px solid #000000;
                                    padding: 5px 10px;
                                }
                                QToolBar QToolButton:hover {
                                    background-color: #d0d0d0;
                                }
                            """
                }

    themes = {"dark": darkTheme, "light": lightTheme}
    lightTheme = """
                        QPushButton {
                            background-color: #f0f0f0;
                            color: #000000;
                            border: 1px solid #000000;
                            padding: 5px 10px;
                        }
                        QPushButton:hover {background-color: #d0d0d0;}
                        QPushButton:pressed {background-color: #a0a0a0;}
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
                        QLineEdit {
                            background-color: white; /* Dark gray background */
                            color: black; /* Text color */
                            border: 2px solid #555555; /*
                            border-radius: 5px; /* Rounded corners */
                            padding: 5px 10px; /* Padding */
                        }
                        QLineEdit:hover {
                            background-color: #3A3A3A; /* Darker gray background on hover */
                        }
                        QMainWindow {
                            background-color: #ffffff; /* Dark gray background */
                            color: blue; /* Text color */
                        }
                        QMainWindow::separator {
                            background-color: red; /* Change the color here */
                            height: 1px; /* Set the height of the separator */
                            margin: 2px; /* Set margin to zero */
                        }
                        QComboBox {
                                    background-color: #f0f0f0;
                                    color: black;
                                    text-align: center;
                                   }
                        QDialog {
                            background-color: #1f1f1f; /* Dark gray background */
                            color: white; /* Text color */
                        }
                        QLabel {
                                background-color: #1f1f1f;
                                border-radius: 1px;
                                border: 1px solid #1f1f1f;
                                color: black
                                }
                        QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                        }
                        /* QLabel inside QFrame */
                        QFrame QLabel {
                            color: blue;
                        }
                        /* QFrame:hover */
                        QFrame:hover {
                            background-color: blue;
                        }
                        /* ToolBar */
                        QToolBar {
                            background-color: #f0f0f0;
                        }
                        /* ToolButton */
                        QToolBar QToolButton {
                            background-color: #f0f0f0;
                            color: #000000;
                            border: 1px solid #000000;
                            padding: 5px 10px;
                        }
                        QToolBar QToolButton:hover {
                            background-color: #d0d0d0;
                        }
                        QToolBar QToolButton:pressed {background-color: #a0a0a0};
                        QTextEdit {background-color: white; color: black;}
                    """

    def __init__(self):
        super().__init__() # Allows the use of abstract class to work
        # Main font for all buttons
        self.buttonsFont = QFont()
        self.buttonsFont.setFamily('Helvetica')
        self.buttonsFont.setPointSize(self.buttonFontSize)

class AWidgets():
    bgTextBoxes = '#2C2C2C'
    colorTextBoxes = 'white'
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
        # textEdit.setStyleSheet(f'background-color: {bg}; color: {color};')
        textEdit.setFont(font)
        textEdit.geometry()
        return textEdit

    def newLabel(self, text, pointSize, style = None):
        label = QLabel(text, self)
        # label.setStyleSheet(f'color: {self.defaultLabelColor}')
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
        # button.setStyleSheet("color: black; background-color: white;" )
        if slot is not None:
            button.clicked.connect(slot)
        if font is not None:
            button.setFont(font)
        if iconPath is not None:
            button.setIcon(QIcon(iconPath))
        if size is not None:
            button.setFixedSize(size[0], size[1])
        if style is not None:
            pass
            # button.setStyleSheet(style)
        return button

    def newTextBox(self, pointSize = None):
        font = QFont()
        if pointSize is not None:
            font.setPointSize(pointSize)
        textBox = QTextEdit()
        textBox.setFont(font)
        return textBox

    def newLine(self, pointSize = None):
        font = QFont()
        if pointSize is not None:
            font.setPointSize(pointSize)
        line = QLineEdit()
        line.setFont(font)
        return line

    def newComboBox(self, slot = None):
        comboBox = QComboBox()
        # comboBox.setFixedSize(250, 30)
        if slot is not None:
            comboBox.currentIndexChanged.connect(slot)
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
        textBoxLog.setFont(font)
        dock.setWidget(textBoxLog)
        return (dock, textBoxLog)

    def newLabel(self, text, pointSize, style = None):
        label = QLabel(text)
        font = QFont()
        font.setPointSize(pointSize)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if style is not None:
            pass
            # label.setStyleSheet(style)
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
    maxSize = (320, 180)
    labelPointSize = 12
    labelStyle = "background-color: #1f1f1f; border-radius: 1px; border: 1px solid #1f1f1f;color: white"
    tabStyle = ("QTabWidget { background-color: #1f1f1f; }"
                "QTabWidget::pane { background-color: black; }"
                "QTabBar::tab { color: white; background-color: black; }"
                "QTabBar::tab:selected { background-color: gray; }"
               )

    def __init__(self, appRootPath, iconPaths):
        super().__init__()
        self.iconPaths = iconPaths
        self.appRootPath = appRootPath
        self.aWidgets = AWidgets()

        #Initialize main window and all tabs needed
        self.initTabs()
        self.initWindow(appRootPath, iconPaths)

    def initWindow(self, appRootPath, iconPaths):
        # Set window properties
        self.setWindowTitle("Settings")
        # self.setStyleSheet(styles['dialog'])
        self.setWindowIcon(QIcon(appRootPath + iconPaths['settings']))
        self.setFixedSize(self.maxSize[0], self.maxSize[1])

        # Initialize apply/cancel buttons
        applyButton = QPushButton("&Apply")
        cancelButton = QPushButton("&Cancel")
        applyButton.setFixedWidth(140)
        cancelButton.setFixedWidth(140)
        applyButton.clicked.connect(self.apply)
        cancelButton.clicked.connect(self.cancel)

        # Set main layout
        gridLayout = QGridLayout()
        self.setLayout(gridLayout)
        gridLayout.addWidget(self.mainTab, 0, 0)
        gridLayout.addWidget(applyButton, 1, 0)
        gridLayout.addWidget(cancelButton, 1, 1)

    def initTabs(self):
        # Initialize main tab widget
        self.mainTab = QTabWidget()
        self.mainTab.setFixedWidth(self.maxSize[0])
        # self.mainTab.setStyleSheet(self.tabStyle)

        # Initialize tab for serial settings
        self.initSerialTab(self.mainTab)

        # Initialize tab for customization
        self.initCustomizationTab(self.mainTab)

    def initSerialTab(self, tabWidget):
        serialLayout = QGridLayout()

        tabSerial = QWidget()
        tabSerial.setLayout(serialLayout)
        # tabSerial.setStyleSheet("background-color: #1f1f1f;")
        # tabSerial.setContentsMargins(10,10,10,10)
        tabWidget.addTab(tabSerial, "Serial device")

        # Create labels
        # labelSerialConfig = self.aWidgets.newLabel("Settings", self.labelPointSize, self.labelStyle)
        labelDataLen = self.aWidgets.newLabel("Data:", self.labelPointSize, self.labelStyle)
        labelParity = self.aWidgets.newLabel("Parity:", self.labelPointSize, self.labelStyle)
        labelStopBits = self.aWidgets.newLabel("Stop bits:", self.labelPointSize, self.labelStyle)

        # Create comboboxes
        self.comboboxDataLen = self.aWidgets.newComboBox()
        self.comboboxStopBits = self.aWidgets.newComboBox()
        self.comboboxParity = self.aWidgets.newComboBox()

        # Set supported data lengths
        self.comboboxDataLen.addItem("8")
        self.comboboxDataLen.addItem("7")
        self.datLenPrevState = self.comboboxDataLen.currentText()

        # Set supported stop bits
        self.comboboxStopBits.addItem("1")
        self.comboboxStopBits.addItem("2")
        self.stopBitsPrevState = self.comboboxStopBits.currentText()

        # Set supported parity
        self.comboboxParity.addItem("None")
        self.comboboxParity.addItem("Odd")
        self.comboboxParity.addItem("Even")
        self.parityPrevState = self.comboboxParity.currentText()

        # Add widgets to serial tab
        # serialLayout.addWidget(labelSerialConfig, 0, 0, 1, -1)
        serialLayout.addWidget(labelDataLen, 1, 0)
        serialLayout.addWidget(self.comboboxDataLen, 1, 1)
        serialLayout.addWidget(labelParity, 2, 0)
        serialLayout.addWidget(self.comboboxParity, 2, 1)
        serialLayout.addWidget(labelStopBits, 3, 0)
        serialLayout.addWidget(self.comboboxStopBits, 3, 1)

    def initCustomizationTab(self, tabWidget):
        customLayout = QGridLayout()
        tabCustom = QWidget()

        tabCustom.setLayout(customLayout)
        # tabCustom.setStyleSheet("background-color: #1f1f1f;")
        tabWidget.addTab(tabCustom, "Custom")

        labelThemes = self.aWidgets.newLabel("Themes", self.labelPointSize, self.labelStyle)
        self.comboboxThemes= self.aWidgets.newComboBox()
        self.comboboxThemes.addItem("Dark")
        self.comboboxThemes.addItem("Light")

        customLayout.addWidget(labelThemes, 0, 0)
        customLayout.addWidget(self.comboboxThemes, 0, 1)

    def apply(self):
        self.accept()

    def cancel(self):
        # Restore previous state
        self.comboboxDataLen.setCurrentText(self.datLenPrevState)
        self.comboboxStopBits.setCurrentText(self.stopBitsPrevState)
        self.comboboxParity.setCurrentText(self.parityPrevState)
        self.reject()

    def getSerialDataLen(self):
        return self.comboboxDataLen.currentText()

    def getSerialStopBits(self):
        return self.comboboxStopBits.currentText()

    def getSerialParity(self):
        return self.comboboxParity.currentText()

    def getTheme(self):
        return self.comboboxThemes.currentText()

import sys
import threading
import time
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import recorder

class Window(QMainWindow):
    #initialize window
    def __init__(self):
        super().__init__()
        self.showWindow()
        self.m_flag = False
    
    #rewrite window events
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and not self.isMaximized():
            self.m_flag=True
            self.m_Position=event.globalPos()-self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.SizeAllCursor)) 
    def mouseMoveEvent(self,QMouseEvent):
        if Qt.LeftButton and self.m_flag:  
            self.move(QMouseEvent.globalPos()-self.m_Position)
            QMouseEvent.accept()
    def mouseReleaseEvent(self,QMouseEvent):
        self.m_flag=False
        self.setCursor(QCursor(Qt.ArrowCursor))

    #show window
    def showWindow(self):
        #set window
        self.setFixedSize(2000,1400)
        self.setWindowTitle("Screen recorder")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        #read style sheet
        style = open("windowStyle.css","r",encoding="UTF-8")
        self.setStyleSheet(style.read())
        style.close()

        #title bar
        titleBar = QWidget(self)
        titleBar.setObjectName("titleBar")
        titleBar.setFixedSize(2000,80)

        #main widget
        content = QWidget(self)
        content.setObjectName("content")
        content.setFixedSize(2000,1320)
        content.move(0,80)

        # title
        title = QLabel(text="Screen Recorder")
        title.setObjectName("windowTitle")
        title.setFixedSize(350,50)
        # buttons
        minbtn = QToolButton()
        minbtn.setObjectName("showmin")
        minbtn.setFixedSize(40,40)
        minbtn.clicked.connect(self.showMinimized)
        def toggleMax():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            titleBar.setFixedSize(self.width(),80)
            content.setFixedSize(self.width(),self.height()-80)
        maxbtn = QToolButton()
        maxbtn.setObjectName("showmax")
        maxbtn.setFixedSize(40,40)
        maxbtn.clicked.connect(toggleMax)
        closebtn = QToolButton()
        closebtn.setObjectName("closeWindow")
        closebtn.setFixedSize(40,40)
        closebtn.clicked.connect(self.close)
        
        # title bar layout
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(title,alignment=Qt.AlignLeft)
        titleLayout.addStretch(0.5)
        titleLayout.addWidget(minbtn,alignment=Qt.AlignRight)
        titleLayout.addWidget(maxbtn,alignment=Qt.AlignRight)
        titleLayout.addWidget(closebtn,alignment=Qt.AlignRight)
        titleBar.setLayout(titleLayout)

        # window contents
        windowLayout = QGridLayout()
        windowLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        content.setLayout(windowLayout)

        # record button
        def loadRecorder():
            self.hide()
            record = recorder.Recorder()
            record.showWindow()
            def recordListener():
                while True:
                    if record.recordMode == 0:
                        self.show()
                        break
            recThread = threading.Thread(target=record.recordScreen,name="Recorder")
            recThread.start()
            listenThread = threading.Thread(target=recordListener,name="Record-Listener")
            listenThread.start()
        recordbtn = QPushButton(content)
        recordbtn.setObjectName("recordButton")
        recordbtn.setFixedSize(500,500)
        recordbtn.clicked.connect(loadRecorder)
        windowLayout.addWidget(recordbtn,0,0)

        # record area set
        recArea = QWidget()
        recArea.setObjectName("recordAreaSet")
        recArea.setFixedSize(350,500)
        windowLayout.addWidget(recArea,0,1)
        # widget layout
        areaLayout = QVBoxLayout(recArea)
        areaLayout.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        areaLayout.setSpacing(30)
        # label
        areaLabel = QLabel(text="Record area")
        areaLabel.setObjectName("recordAreaLabel")
        areaLabel.setFixedSize(300,50)
        areaLayout.addWidget(areaLabel)
        # area select
        # full screen #
        fullScreen = QRadioButton(text="Full screen")
        fullScreen.setObjectName("recordFullScreen")
        fullScreen.setChecked(True)
        fullScreen.setFixedSize(300,50)
        areaLayout.addWidget(fullScreen)
        # custom area #
        cusLayout = QGridLayout()
        cusLayout.setSpacing(10)
        cusLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        tickScreen = QRadioButton(text="Custom area")
        tickScreen.setObjectName("recordCustomArea")
        tickScreen.setFixedSize(350,50)
        cusLayout.addWidget(tickScreen,0,0)

        # position #
        areaPos = QLabel(text="Position:")
        areaPos.setObjectName("areaPosition")
        areaPos.setFixedSize(300,50)
        cusLayout.addWidget(areaPos,1,0)
        areaX = QLineEdit()
        areaX.setObjectName("areaXPosition")
        areaX.setFixedSize(130,55)
        areaX.setAlignment(Qt.AlignCenter)
        areaX.setPlaceholderText("X")
        areaX.setValidator()
        areaY = QLineEdit()
        areaY.setObjectName("areaYPosition")
        areaY.setFixedSize(130,55)
        areaY.setAlignment(Qt.AlignCenter)
        areaY.setPlaceholderText("Y")
        areaWidth = QLineEdit()
        areaWidth.setObjectName("areaWidth")
        areaWidth.setFixedSize(130,55)
        areaWidth.setAlignment(Qt.AlignCenter)
        areaWidth.setPlaceholderText("Width")
        areaHeight = QLineEdit()
        areaHeight.setObjectName("areaHeight")
        areaHeight.setFixedSize(130,55)
        areaHeight.setAlignment(Qt.AlignCenter)
        areaHeight.setPlaceholderText("Height")
        cusLayout.addWidget(areaX,2,0)
        cusLayout.addWidget(areaY,2,1)
        cusLayout.addWidget(areaWidth,3,0)
        cusLayout.addWidget(areaHeight,3,1)
        areaLayout.addLayout(cusLayout)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

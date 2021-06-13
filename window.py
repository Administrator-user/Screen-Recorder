import sys
import os
import threading
import time
from PIL import ImageGrab
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
        self.m_flag = False
        self.desktop = QApplication.desktop()
        self.w = self.desktop.width()
        self.h = self.desktop.height()
        #set window
        self.setFixedSize(int(self.w*0.6),int(self.h*0.7))
        self.setWindowTitle("Screen recorder")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        self.showWindow()
        self.recArea = (0,0,self.w,self.h)
    
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
    def closeEvent(self,event):
        os.remove("buttons/desktop.png")
        event.accept()

    #show window
    def showWindow(self):
        #read style sheet
        style = open("windowStyle.css","r",encoding="UTF-8")
        self.setStyleSheet(style.read())
        style.close()

        #title bar
        titleBar = QWidget(self)
        titleBar.setObjectName("titleBar")
        titleBar.setFixedSize(self.width(),int(self.height()*0.06))

        #main widget
        content = QWidget(self)
        content.setObjectName("content")
        content.setFixedSize(self.width(),int(self.height()*0.94))
        content.move(0,titleBar.height())

        # title
        title = QLabel(text="Screen Recorder")
        title.setObjectName("windowTitle")
        title.setFixedSize(int(self.width()*0.18),int(self.height()*0.036))
        # buttons
        minbtn = QToolButton()
        minbtn.setObjectName("showmin")
        minbtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        minbtn.clicked.connect(self.showMinimized)
        minbtn.setToolTip("Show minimized (Alt+N)")
        minbtn.setShortcut("Alt+N")
        def toggleMax():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            titleBar.setFixedSize(self.width(),80)
            content.setFixedSize(self.width(),self.height()-80)
        maxbtn = QToolButton()
        maxbtn.setObjectName("showmax")
        maxbtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        maxbtn.clicked.connect(toggleMax)
        maxbtn.setToolTip("Show maximized (Alt+X)")
        maxbtn.setShortcut("Alt+X")
        closebtn = QToolButton()
        closebtn.setObjectName("closeWindow")
        closebtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        closebtn.clicked.connect(self.close)
        closebtn.setToolTip("Close (Alt+F4)")
        closebtn.setShortcut("Alt+F4")
        
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
            record = recorder.Recorder(area=self.recArea)
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
        recordbtn.setFixedSize(int(self.width()*0.25),int(self.width()*0.25))
        recordbtn.clicked.connect(loadRecorder)
        windowLayout.addWidget(recordbtn,0,0)

        # record area set
        recArea = QWidget()
        recArea.setObjectName("recordAreaSet")
        recArea.setFixedSize(int(self.width()*0.18),int(self.height()*0.357))
        windowLayout.addWidget(recArea,0,1)
        # widget layout
        areaLayout = QVBoxLayout(recArea)
        areaLayout.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        areaLayout.setSpacing(int(self.width()*0.015))
        # label
        areaLabel = QLabel(text="Record area")
        areaLabel.setObjectName("recordAreaLabel")
        areaLabel.setFixedSize(int(self.width()*0.26),int(self.height()*0.036))
        areaLayout.addWidget(areaLabel)
        # area select
        # full screen #
        fullScreen = QRadioButton(text="Full screen")
        fullScreen.setObjectName("recordFullScreen")
        fullScreen.setChecked(True)
        fullScreen.setFixedSize(int(self.width()*0.16),int(self.height()*0.036))
        areaLayout.addWidget(fullScreen)
        # custom area #
        cusLayout = QGridLayout()
        cusLayout.setSpacing(int(self.width()*0.005))
        cusLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        tickScreen = QRadioButton(text="Custom area")
        tickScreen.setObjectName("recordCustomArea")
        tickScreen.setFixedSize(int(self.width()*0.16),int(self.height()*0.036))
        cusLayout.addWidget(tickScreen,0,0)

        # position #
        areaPos = QLabel(text="Position:")
        areaPos.setObjectName("areaPosition")
        areaPos.setFixedSize(int(self.width()*0.15),int(self.height()*0.036))
        cusLayout.addWidget(areaPos,1,0)
        areaX = QLineEdit()
        areaX.setObjectName("areaXPosition")
        areaX.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaX.setAlignment(Qt.AlignCenter)
        areaX.setPlaceholderText("X")
        areaX.setValidator(QIntValidator())
        areaY = QLineEdit()
        areaY.setObjectName("areaYPosition")
        areaY.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaY.setAlignment(Qt.AlignCenter)
        areaY.setPlaceholderText("Y")
        areaY.setValidator(QIntValidator())
        areaWidth = QLineEdit()
        areaWidth.setObjectName("areaWidth")
        areaWidth.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaWidth.setAlignment(Qt.AlignCenter)
        areaWidth.setPlaceholderText("Width")
        areaWidth.setValidator(QIntValidator())
        areaHeight = QLineEdit()
        areaHeight.setObjectName("areaHeight")
        areaHeight.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaHeight.setAlignment(Qt.AlignCenter)
        areaHeight.setPlaceholderText("Height")
        areaHeight.setValidator(QIntValidator())
        cusLayout.addWidget(areaX,2,0)
        cusLayout.addWidget(areaY,2,1)
        cusLayout.addWidget(areaWidth,3,0)
        cusLayout.addWidget(areaHeight,3,1)
        areaLayout.addLayout(cusLayout)

        # area preview
        previewImage = ImageGrab.grab()
        previewImage.save("./buttons/desktop.png")
        previewWidget = QWidget()
        previewWidget.setObjectName("recordPreviewImage")
        previewWidget.setFixedSize(int(self.w*0.25),int(self.h*0.25))
        windowLayout.addWidget(previewWidget,0,2)
        previewArea = QWidget(previewWidget)
        previewArea.setObjectName("recordAreaPreview")
        previewArea.setFixedSize(int(self.w*0.25),int(self.h*0.25))
        previewArea.move(0,0)

        def checkArea():
            try:
                x = int(areaX.text())
                y = int(areaY.text())
                w = int(areaWidth.text())
                h = int(areaHeight.text())
            except:
                areaX.setText("0")
                areaY.setText("0")
                areaWidth.setText(str(self.w))
                areaHeight.setText(str(self.h))
                x = 0
                y = 0
                w = self.w
                h = self.h
            if tickScreen.isChecked():
                maxWidth = self.w-x
                maxHeight = self.h-y
                if w > maxWidth:
                    w = maxWidth
                    areaWidth.setText(str(w))
                if h > maxHeight:
                    h = maxHeight
                    areaHeight.setText(str(h))
                previewArea.setFixedSize(int(w*0.25),int(h*0.25))
                previewArea.move(int(x*0.25),int(y*0.25))
                self.recArea = (x,y,w,h)
            else:
                previewArea.setFixedSize(int(self.w*0.25),int(self.h*0.25))
                previewArea.move(0,0)
                self.recArea = (0,0,self.w,self.h)
        areaX.textChanged.connect(checkArea)
        areaY.textChanged.connect(checkArea)
        areaWidth.textChanged.connect(checkArea)
        areaHeight.textChanged.connect(checkArea)
        fullScreen.toggled.connect(checkArea)
        tickScreen.toggled.connect(checkArea)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

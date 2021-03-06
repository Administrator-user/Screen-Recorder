import sys
import threading
import time
import wave
import cv2
import numpy as np
import pyaudio
import sounddevice as sd
from moviepy.editor import *
from PIL import ImageGrab
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Recorder(QWidget):
    '''
    # Recorder
    ## Module 'Recorder' in Screen-Recorder
    
     area: the record area (x, y, width, height)
     encode: video encoder (fourcc, ffmpeg encode(when devID != 0), filename extension)
     devID: sound device index (none when devID=0)
    '''
    def __init__(self,area:tuple, encode:tuple, devID=0):
        super().__init__()
        self.recordMode = 1
        self.isExit = False
        self.desktop = QApplication.desktop()
        self.w = self.desktop.width()
        self.h = self.desktop.height()
        self.timeString = "00:00:00"
        self.wait = 3
        self.isFold = False
        self.videoName = ""
        self.audioName = ""
        self.outputName = ""
        self.area = area
        self.devID = devID
        self.fourcc = encode[0]
        self.fcodec = encode[1]
        self.fileExt = encode[2]

    #rewrite window events
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self.m_flag=True
            self.m_Position=event.globalPos()-self.pos()
            self.m_Ypos = event.globalY()-self.y()
            event.accept()
            self.setCursor(QCursor(Qt.SizeAllCursor)) 
    def mouseMoveEvent(self,QMouseEvent):
        if Qt.LeftButton:
            if self.isFold:
                self.move(self.x(), QMouseEvent.globalY()-self.m_Ypos)
            else:
                self.move(QMouseEvent.globalPos()-self.m_Position)
            QMouseEvent.accept()
    def mouseReleaseEvent(self,QMouseEvent):
        self.m_flag=False
        self.setCursor(QCursor(Qt.ArrowCursor))

    #screen record
    def recordScreen(self):
        #initalize
        desktop = ImageGrab.grab()
        w,h = desktop.size
        audioThread = threading.Thread(target=self.recordAudio,name="recorder-sound")
        timeThread = threading.Thread(target=self.updateTime,name="recorder-screen")
        if self.devID != 0:
            audioThread.start()
        timeThread.start()
        fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        self.currentTime = time.localtime()
        self.outputName = "videos/{}{}".format(time.strftime("%Y%m%d-%H%M%S",self.currentTime),
        self.fileExt)
        if self.devID == 0:
            self.videoName = "videos/{}{}".format(time.strftime("%Y%m%d-%H%M%S",self.currentTime),
            self.fileExt)
        else:
            self.videoName = "videos/v-{}{}".format(time.strftime("%Y%m%d-%H%M%S",self.currentTime),
            self.fileExt)
        FPS = cv2.CAP_PROP_FPS
        
        video = cv2.VideoWriter(self.videoName,fourcc,FPS,
        (self.area[2]-self.area[0],self.area[3]-self.area[1]))
        time.sleep(self.wait)
        # record
        while True:
            if self.recordMode == 0:
                break
            elif self.recordMode == 2:
                continue
            currentImg = ImageGrab.grab(bbox=self.area)
            writeImg = cv2.cvtColor(np.array(currentImg),cv2.COLOR_RGB2BGR)
            video.write(writeImg)
        video.release()
        self.close()
        if self.devID == 0:
            self.isExit = True
            return 0
        
    # sound record
    def recordAudio(self):
        chunk = 1024
        fmt = pyaudio.paInt16
        channels = 2
        rate = 44100

        p = pyaudio.PyAudio()
        sd.default.device[0] = self.devID
        stream = p.open(channels=channels,format=fmt,rate=rate,input=True,
        frames_per_buffer=chunk)
        self.audioName = "videos/snd{}.wav".format(time.strftime("%Y%m%d-%H%M%S"))
        wf = wave.open(self.audioName,"wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(fmt))
        wf.setframerate(rate)

        time.sleep(self.wait)

        while True:
            if self.recordMode == 0:
                break
            elif self.recordMode == 2:
                continue
            data = stream.read(chunk)
            wf.writeframes(data)
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

        # merge video and audio
        mergeThread = threading.Thread(target=self.merge,name="recorder-merger")
        mergeThread.start()
        return 0

    # time update
    def updateTime(self):
        result = "00:00:00"
        for i in range(self.wait):
            time.sleep(1)
            self.time.display(str(self.wait-i))
        while True:
            if self.recordMode == 0:
                break
            elif self.recordMode == 2:
                continue
            time.sleep(1)
            tList = self.timeString.split(":")
            #  calculate time
            h = int(tList[0])
            m = int(tList[1])
            s = int(tList[2])
            s += 1
            if s >= 60:
                m += 1
                s = 0
            if m >= 60:
                h += 1
                m = 0

            h = str(h)
            m = str(m)
            s = str(s)
            timeList = tuple(["0"+i if len(i)==1 else i for i in [h,m,s]])
            result = "{}:{}:{}".format(timeList[0],timeList[1],timeList[2])
            self.timeString = result
            self.time.display(result)
        
    
    def merge(self):
        video = VideoFileClip("./{}".format(self.videoName))
        audio = AudioFileClip("./{}".format(self.audioName)).volumex(1)
        audioAdd = CompositeAudioClip([audio])
        video.set_audio(audioAdd)
        video.write_videofile(self.outputName,codec=self.fcodec)
        
        os.remove(self.videoName)
        os.remove(self.audioName)
        time.sleep(0.1)
        self.isExit = True
        self.close()
        

    def showWindow(self):
        self.setFixedSize(int(self.w*0.17),int(self.h*0.05))
        self.setWindowTitle("Screen Recorder")
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(self.w-self.width()-50,self.h-self.height()-100)
        self.setWindowOpacity(0.8)

        #set style sheet
        styleSheet = open("recorderStyle.css","r")
        style = styleSheet.read()
        self.setStyleSheet(style)
        styleSheet.close()

        #main widget
        content = QWidget(self)
        content.setObjectName("recorder")
        content.setFixedSize(self.width(),self.height())
        content.move(0,0)
        # main layout
        recorderLayout = QHBoxLayout(content)
        recorderLayout.setGeometry(QRect(0,0,self.width(),self.height()-50))
        recorderLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        # fold / unfold
        self.fold = QToolButton()
        self.fold.setFixedSize(int(self.w*0.01),int(self.h*0.03))
        self.fold.setToolTip("Fold")
        recorderLayout.addWidget(self.fold,0,(Qt.AlignLeft|Qt.AlignTop))
        self.foldStyle = '''
        QToolButton{
            background: transparent;
            border-image: url(./required/buttons/unfold.png);
        }
        QToolButton:hover{
            background: rgba(128, 128, 128, 0.2);
        }'''
        self.unfoldStyle = '''
        QToolButton{
            background: transparent;
            border-image: url(./required/buttons/fold.svg);
        }
        QToolButton:hover{
            background: rgba(128, 128, 128, 0.2);
        }'''
        self.fold.setStyleSheet(self.unfoldStyle)
        def toggleFold():
            if self.isFold:
                self.isFold = False
                self.fold.setStyleSheet(self.unfoldStyle)
                self.fold.setToolTip("Fold")
                self.move(self.w-self.width()-50,self.y())
            else:
                self.isFold = True
                self.fold.setStyleSheet(self.foldStyle)
                self.fold.setToolTip("Unfold")
                self.move(int(self.w*0.98),self.y()) 
        self.fold.clicked.connect(toggleFold)

        # time show
        self.time = QLCDNumber()
        self.time.setObjectName("recordTime")
        self.time.setFixedSize(int(self.w*0.1),int(self.h*0.03))
        self.time.setSegmentStyle(QLCDNumber.Flat)
        self.time.setDigitCount(8)
        self.time.display(self.timeString)
        recorderLayout.addWidget(self.time,0,(Qt.AlignLeft|Qt.AlignTop))

        # pause button
        # pause button -- style sheets #
        normalStyle = """ 
        QPushButton#pauseButton{
            background: rgba(128,128,128,0);
            border: none;
            border-radius: 5px;
            border-image: url("./required/buttons/pause.svg");
        }
        QPushButton#pauseButton:hover{
            background: rgba(128,128,128,0.2);
        }
        QPushButton#pauseButton:pressed{
            background: rgba(128,128,128,0.5);
        } """
        pauseStyle = """ 
        QPushButton#pauseButton{
            background: rgba(128,128,128,0);
            border: none;
            border-radius: 5px;
            border-image: url(./required/buttons/continue.svg);
        }
        QPushButton#pauseButton:hover{
            background: rgba(128,128,128,0.2);
        }
        QPushButton#pauseButton:pressed{
            background: rgba(128,128,128,0.5);
        } """
        pause = QPushButton()
        def toggleRecord():
            if self.recordMode == 1:
                self.recordMode = 2
                pause.setStyleSheet(pauseStyle)
            else:
                self.recordMode = 1
                pause.setStyleSheet(normalStyle)
        pause.setObjectName("pauseButton")
        pause.setStyleSheet(normalStyle)
        pause.setFixedSize(int(self.w*0.021),int(self.w*0.021))
        pause.clicked.connect(toggleRecord)
        recorderLayout.addWidget(pause)

        # stop button
        stop = QPushButton()
        def stopRecord():
            self.recordMode = 0
        stop.setObjectName("stopButton")
        stop.setFixedSize(int(self.w*0.021),int(self.w*0.021))
        stop.clicked.connect(stopRecord)
        recorderLayout.addWidget(stop)

        self.show()

## test code ##
# app = QApplication(sys.argv)
# test = Recorder((0,0,800,600))
# test.showWindow()
# sys.exit(app.exec_())

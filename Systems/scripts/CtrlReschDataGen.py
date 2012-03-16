#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Control Research Data Generation

Two toggle buttons are created to transmit via UDP to dsm_server
the following two messages:

  NOCAL,20120312T143258,1
  NOREC,20120312T143258,1

...where the last value of 1 or 0 indicates the state of button.

NIMBUS shall include these as values in the IWG1 stream.

Instruments watching the IWG1 stream shall use these flags to
restrict calibration and recording of research data.
"""

import sys
from PyQt4.QtCore import (Qt, QObject, QTimer, QDateTime, SIGNAL)
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QApplication)
from PyQt4.QtNetwork import (QHostAddress, QUdpSocket)

DATETIME_FORMAT_VIEW = "yyyy-MM-dd H:mm:ss"
DATETIME_FORMAT_DATA = "yyyyMMddTHmmss"
PORT = 41004

class CtrlReschDataGen(QWidget):

    def __init__(self):
#       print("__init__: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        super(CtrlReschDataGen, self).__init__()

        self.initUI()

        self.udpSocket = QUdpSocket()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.sendDatagrams)
        self.timer.start(1000)

    # send state to NIDAS every second via a UDP socket
    def sendDatagrams(self):
        datetime = QDateTime.currentDateTime().toString("yyyyMMddTHmmss")
        NOCAL = "NOCAL,%s," % datetime
        NOREC = "NOREC,%s," % datetime

        if self.DoNotCalibrate.isChecked(): NOCAL = NOCAL + "1"
        else:                               NOCAL = NOCAL + "0"
#       print("NOCAL: %s" % NOCAL)
        self.udpSocket.writeDatagram(NOCAL, QHostAddress("192.168.184.1"), PORT)

        if self.DoNotRecord.isChecked(): NOREC = NOREC + "1"
        else:                            NOREC = NOREC + "0"
#       print("NOREC: %s" % NOREC)
        self.udpSocket.writeDatagram(NOREC, QHostAddress("192.168.184.1"), PORT)

    # prevent operator from leaving while actively enforcing
    def closeEvent(self, event):
        if self.DoNotCalibrate.isChecked() or self.DoNotRecord.isChecked():
            event.ignore()
            print('\a') # beep
        else:
            self.sendDatagrams()

    def initUI(self):
#       print("initUI: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.setWindowTitle('Control Research Data Generation')
        startLabel    = QLabel("Start:")
        stopLabel     = QLabel("Stop:")

        # setup DoNotCalibrate
        self.DoNotCalibrate = QPushButton('Do Not Calibrate', self)
        self.DoNotCalibrate.setCheckable(True)
        self.DoNotCalibrate.setChecked(False)
        self.DoNotCalibrate.clicked[bool].connect(self.setDoNotCalibrate)

        self.DoNotCalibrateStart = QLineEdit()
        self.DoNotCalibrateStart.setReadOnly(True)

        self.DoNotCalibrateStop = QLineEdit()
        self.DoNotCalibrateStop.setReadOnly(True)

        # setup DoNotRecord
        self.DoNotRecord = QPushButton('Do Not Record', self)
        self.DoNotRecord.setCheckable(True)
        self.DoNotRecord.setChecked(False)
        self.DoNotRecord.clicked[bool].connect(self.setDoNotRecord)

        self.DoNotRecordStart = QLineEdit()
        self.DoNotRecordStart.setReadOnly(True)

        self.DoNotRecordStop = QLineEdit()
        self.DoNotRecordStop.setReadOnly(True)

        # layout in a grid
        layout = QGridLayout()
        layout.addWidget(self.DoNotCalibrate,      0, 1)
        layout.addWidget(self.DoNotRecord,         0, 2)
        layout.addWidget(startLabel,               1, 0)
        layout.addWidget(self.DoNotCalibrateStart, 1, 1)
        layout.addWidget(self.DoNotRecordStart,    1, 2)
        layout.addWidget(stopLabel,                2, 0)
        layout.addWidget(self.DoNotCalibrateStop,  2, 1)
        layout.addWidget(self.DoNotRecordStop,     2, 2)
        self.setLayout(layout)

    def setDoNotCalibrate(self, pressed):
#       print("setDoNotCalibrate: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        if pressed:
            StartTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW)
        else:
            StartTime = ''

        self.DoNotCalibrateStart.setText(StartTime)

    def setDoNotRecord(self, pressed):
#       print("setDoNotRecord: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        if pressed:
            StartTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW)
        else:
            StartTime = ''

        self.DoNotRecordStart.setText(StartTime)


def main():
#   print("main: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
    app = QApplication(sys.argv)
    crdg = CtrlReschDataGen()
    crdg.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)
    crdg.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

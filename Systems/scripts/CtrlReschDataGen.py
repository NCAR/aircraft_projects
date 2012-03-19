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
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QLineEdit, QGridLayout,
                         QApplication, QMessageBox)
from PyQt4.QtNetwork import (QHostAddress, QUdpSocket)

DATETIME_FORMAT_VIEW = "yyyy-MM-dd H:mm:ss"
DATETIME_FORMAT_DATA = "yyyyMMddTHmmss"
PORT = 41004
NOCAL_STEP = 1
NOCALMINUTES = 15
NORECMINUTES = 15

class CtrlReschDataGen(QWidget):

    def __init__(self):
#       print("__init__: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        super(CtrlReschDataGen, self).__init__()

        self.initUI()

        self.udpSocket = QUdpSocket()

        self.DoNotCalibrateStopTime = QDateTime()
        self.DoNotRecordWarnTime = QDateTime()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.timeout)
        self.timer.start(1000)

    def showRemainingTime(self, currentDateTime):
        if currentDateTime.isValid():
            secsTo = currentDateTime.secsTo(self.DoNotCalibrateStopTime)
            hwrsTo = secsTo / 3600
            secsTo = secsTo - (hwrsTo * 3600)
            minsTo = secsTo / 60
            secsTo = secsTo - (minsTo * 60)
            self.DoNotCalibrateRemain.setText( ("%02d:%02d:%02d" % (hwrsTo, minsTo, secsTo)) )
        else:
            self.DoNotCalibrateRemain.setText( "" )

    def timeout(self):
        currentDateTime = QDateTime.currentDateTime()

        if self.DoNotCalibrateStopTime.isValid():
            self.showRemainingTime(currentDateTime)
            if currentDateTime >= self.DoNotCalibrateStopTime:
                StartTime = QDateTime()
                self.DoNotCalibrateStopTime = QDateTime()
                self.DoNotCalibrate.setChecked(False)
                self.LessTime.setEnabled(False)
                self.MoreTime.setEnabled(False)
                self.DoNotCalibrateStart.setText(StartTime.toString(DATETIME_FORMAT_VIEW))
                self.showRemainingTime(StartTime)

        if self.DoNotRecordWarnTime.isValid():
            if currentDateTime >= self.DoNotRecordWarnTime:
                self.DoNotRecordWarnTime = currentDateTime.addSecs(NORECMINUTES * 60)

                message = ("Time is: %s\n\nDo Not Record's been active for the past %d minutes" %
                  (QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW), NORECMINUTES))

                # spawn a non blocking message box, these will just keep piling up until closed
                box = QMessageBox(QMessageBox.Warning,  "Time to Disable?",
                  message, QMessageBox.Ok, self, (Qt.Dialog |
                  Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint))

                box.setWindowModality(Qt.NonModal);
                box.show();

        self.sendDatagrams(currentDateTime)

    # send state to NIDAS every second via a UDP socket
    def sendDatagrams(self, currentDateTime):
        datetime = currentDateTime.toString(DATETIME_FORMAT_DATA)
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

    def addLessTime(self):
#       print("addLessTime: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.DoNotCalibrateStopTime = self.DoNotCalibrateStopTime.addSecs(-NOCAL_STEP * 60)
        currentDateTime = QDateTime.currentDateTime()
        self.showRemainingTime(currentDateTime)

        if currentDateTime >= self.DoNotCalibrateStopTime:
            StartTime = QDateTime()
            self.DoNotCalibrateStopTime = QDateTime()
            self.DoNotCalibrate.setChecked(False)
            self.LessTime.setEnabled(False)
            self.MoreTime.setEnabled(False)
            self.DoNotCalibrateStart.setText(StartTime.toString(DATETIME_FORMAT_VIEW))
            self.showRemainingTime(StartTime)

    def addMoreTime(self):
#       print("addMoreTime: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.DoNotCalibrateStopTime = self.DoNotCalibrateStopTime.addSecs(NOCAL_STEP * 60)
        currentDateTime = QDateTime.currentDateTime()
        self.showRemainingTime(currentDateTime)

    def initUI(self):
#       print("initUI: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.setWindowTitle('Control Research Data Generation')
        startLabel    = QLabel("Start:")
        RemainLabel   = QLabel("Remain:")

        # setup DoNotCalibrate
        self.DoNotCalibrate = QPushButton('Do Not Calibrate', self)
        self.DoNotCalibrate.setCheckable(True)
        self.DoNotCalibrate.setChecked(False)
        self.DoNotCalibrate.clicked[bool].connect(self.setDoNotCalibrate)

        self.DoNotCalibrateStart = QLineEdit()
        self.DoNotCalibrateStart.setReadOnly(True)

        self.DoNotCalibrateRemain = QLineEdit()
        self.DoNotCalibrateRemain.setReadOnly(True)

        self.LessTime = QPushButton('<', self)
        self.MoreTime = QPushButton('>', self)

        self.LessTime.setEnabled(False)
        self.MoreTime.setEnabled(False)

        self.LessTime.setMaximumWidth(20)
        self.MoreTime.setMaximumWidth(20)

        QObject.connect(self.LessTime, SIGNAL("clicked()"), self.addLessTime)
        QObject.connect(self.MoreTime, SIGNAL("clicked()"), self.addMoreTime)

        # setup DoNotRecord
        self.DoNotRecord = QPushButton('Do Not Record', self)
        self.DoNotRecord.setCheckable(True)
        self.DoNotRecord.setChecked(False)
        self.DoNotRecord.clicked[bool].connect(self.setDoNotRecord)

        self.DoNotRecordStart = QLineEdit()
        self.DoNotRecordStart.setReadOnly(True)

        # layout in a grid
        layout = QGridLayout()
        layout.addWidget(self.DoNotCalibrate,       0, 1, 1, 3)
        layout.addWidget(self.DoNotRecord,          0, 4)
        layout.addWidget(startLabel,                1, 0)
        layout.addWidget(self.DoNotCalibrateStart,  1, 1, 1, 3)
        layout.addWidget(self.DoNotRecordStart,     1, 4)
        layout.addWidget(RemainLabel,               2, 0)
        layout.addWidget(self.LessTime,             2, 1, 1, 1)
        layout.addWidget(self.DoNotCalibrateRemain, 2, 2, 1, 1)
        layout.addWidget(self.MoreTime,             2, 3, 1, 1)
        self.setLayout(layout)

    def setDoNotCalibrate(self, pressed):
#       print("setDoNotCalibrate: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        if pressed:
            StartTime = QDateTime.currentDateTime()
            self.LessTime.setEnabled(True)
            self.MoreTime.setEnabled(True)
        else:
            StartTime = QDateTime()
            self.LessTime.setEnabled(False)
            self.MoreTime.setEnabled(False)

        if StartTime.isValid():
            self.DoNotCalibrateStartTime = StartTime
            self.DoNotCalibrateStopTime = StartTime.addSecs(NOCALMINUTES * 60)
        else:
            self.DoNotCalibrateStopTime = QDateTime()

        # displaying invalid times clears the display
        self.DoNotCalibrateStart.setText(StartTime.toString(DATETIME_FORMAT_VIEW))
        self.showRemainingTime(StartTime)

    def setDoNotRecord(self, pressed):
#       print("setDoNotRecord: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        if pressed:
            StartTime = QDateTime.currentDateTime()
        else:
            StartTime = QDateTime()

        if StartTime.isValid():
            self.DoNotRecordWarnTime = StartTime.addSecs(NORECMINUTES * 60)
        else:
            self.DoNotRecordWarnTime = QDateTime()

        # displaying invalid times clears the display
        self.DoNotRecordStart.setText(StartTime.toString(DATETIME_FORMAT_VIEW))


def main():
#   print("main: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
    app = QApplication(sys.argv)
    crdg = CtrlReschDataGen()
    crdg.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)
    crdg.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

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
from PyQt4.QtCore import (Qt, QObject, QTimer, QTime, QDateTime, SIGNAL)
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QLineEdit, QTimeEdit, QGridLayout,
                         QApplication, QMessageBox)
from PyQt4.QtNetwork import (QHostAddress, QUdpSocket)

TIME_FORMAT_VIEW     = "hh:mm:ss"
DATETIME_FORMAT_VIEW = "yyyy-MM-dd hh:mm:ss"
DATETIME_FORMAT_DATA = "yyyyMMddTHmmss"
PORT = 41004
NOCAL_STEP = 1
NOCALMINUTES = 15
NORECMINUTES = 15

class CtrlReschDataGen(QWidget):

    def __init__(self):
#       print("__init__: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        super(CtrlReschDataGen, self).__init__()

        self.updatingRemainingTime = False

        self.initUI()

        self.udpSocket = QUdpSocket()

        self.DoNotCalibrateStopTime = QDateTime()
        self.DoNotRecordWarnTime = QDateTime()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.timeout)
        self.timer.start(1000)

    def showRemainingTime(self, currentDateTime):
        self.updatingRemainingTime = True
        if currentDateTime.isValid():
            secsTo = currentDateTime.secsTo(self.DoNotCalibrateStopTime)
            hwrsTo = secsTo / 3600
            secsTo = secsTo - (hwrsTo * 3600)
            minsTo = secsTo / 60
            secsTo = secsTo - (minsTo * 60)
            self.remainingTime.setTime( QTime(hwrsTo, minsTo, secsTo) )
            self.hwrs = hwrsTo
            self.mins = minsTo
            self.secs = secsTo
        else:
            self.remainingTime.setTime( QTime() )

        self.updatingRemainingTime = False

    def timeout(self):
        currentDateTime = QDateTime.currentDateTime()

        if self.DoNotCalibrateStopTime.isValid():
            self.showRemainingTime(currentDateTime)
            if currentDateTime >= self.DoNotCalibrateStopTime:
                StartTime = QDateTime()
                self.DoNotCalibrateStopTime = QDateTime()
                self.DoNotCalibrate.setChecked(False)
                self.remainingTime.setEnabled(False)
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
            for i in range(2):
                self.sendDatagrams(QDateTime.currentDateTime())
            event.accept()

    def timeChanged(self):
        if not self.updatingRemainingTime:
#           print("timeChanged: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
#           print("remainingTime:          %s" % self.remainingTime.time().toString(TIME_FORMAT_VIEW))
#           print("DoNotCalibrateStopTime: %s" % self.DoNotCalibrateStopTime.toString(DATETIME_FORMAT_VIEW))

            # normalize steps to a magnitude of 1 or 0
            hwrs = 1 if self.remainingTime.time().hour()   > self.hwrs else -1
            mins = 1 if self.remainingTime.time().minute() > self.mins else -1
            secs = 1 if self.remainingTime.time().second() > self.secs else -1
            hwrs = 0 if self.remainingTime.time().hour()   == self.hwrs else hwrs
            mins = 0 if self.remainingTime.time().minute() == self.mins else mins
            secs = 0 if self.remainingTime.time().second() == self.secs else secs
#           print("Change seen: %02d:%02d:%02d" % (hwrs, mins, secs))
            self.DoNotCalibrateStopTime = self.DoNotCalibrateStopTime.addSecs( hwrs * 3600 + mins * 60 + secs )

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

        self.remainingTime = QTimeEdit()
        self.remainingTime.setDisplayFormat(TIME_FORMAT_VIEW)
        self.remainingTime.setEnabled(False)

        QObject.connect(self.remainingTime, SIGNAL("timeChanged(QTime)"), self.timeChanged)

        # setup DoNotRecord
        self.DoNotRecord = QPushButton('Do Not Record', self)
        self.DoNotRecord.setCheckable(True)
        self.DoNotRecord.setChecked(False)
        self.DoNotRecord.clicked[bool].connect(self.setDoNotRecord)

        self.DoNotRecordStart = QLineEdit()
        self.DoNotRecordStart.setReadOnly(True)

        # layout in a grid
        layout = QGridLayout()
        layout.addWidget(self.DoNotCalibrate,      0, 1)
        layout.addWidget(self.DoNotRecord,         0, 2)
        layout.addWidget(startLabel,               1, 0)
        layout.addWidget(self.DoNotCalibrateStart, 1, 1)
        layout.addWidget(self.DoNotRecordStart,    1, 2)
        layout.addWidget(RemainLabel,              2, 0)
        layout.addWidget(self.remainingTime,       2, 1)
        self.setLayout(layout)

    def setDoNotCalibrate(self, pressed):
#       print("setDoNotCalibrate: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        if pressed:
            StartTime = QDateTime.currentDateTime()
            self.remainingTime.setEnabled(True)
        else:
            StartTime = QDateTime()
            self.remainingTime.setEnabled(False)

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

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Mission Control

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
import functools

from PyQt4.QtCore import (Qt, QObject, QTimer, QTime, QDateTime, SIGNAL, QString, QSocketNotifier)
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QLineEdit, QTimeEdit, QGridLayout,
                         QApplication, QMessageBox, QGroupBox, QHBoxLayout, QButtonGroup,
                         QStackedWidget, QFrame, QComboBox)
from PyQt4.QtNetwork import (QHostAddress, QUdpSocket)

from psycopg2 import *

TIME_FORMAT_VIEW     = "hh:mm:ss"
DATETIME_FORMAT_VIEW = "yyyy-MM-dd hh:mm:ss"
DATETIME_FORMAT_DATA = "yyyyMMddTHmmss"
PORT = 41005
NOCAL_STEP = 1
NOCALMINUTES = 15
NORECMINUTES = 15

class MissionControl(QWidget):

    def __init__(self):
#       print("__init__: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        super(MissionControl, self).__init__()

        self.updatingRemainingTime = False

        # connect to the aircraft's real-time database
        conn_string = "host='acserver' dbname='real-time' user='ads'"
#       print "Connecting to database\n -> %s" % (conn_string)
        try:
            # get a connection, if a connect cannot be made an exception will be raised here
            self.conn = connect(conn_string)

            # what is psycopg2._psycopg.connection ???
            self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)

            # conn.cursor will return a cursor object, you can use this cursor to perform queries
            self.cursor = self.conn.cursor()
#           print "Connected!\n"
        except:
            self.failExit()

        # create the mission_control table
        self.cursor.execute("SELECT exists(SELECT * FROM information_schema.tables where table_name='mission_control')")
        val = self.cursor.fetchone()
        if not val[0]:
            try:
                self.cursor.execute("CREATE TABLE mission_control (key text PRIMARY KEY, value text)")
            except:
                self.failExit()

        self.initUI()

        self.udpSocket = QUdpSocket()

        self.DoNotCalibrateStopTime = QDateTime()
        self.DoNotRecordWarnTime = QDateTime()

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.timeout)
        self.timer.start(1000)

        self.updateSelectionCnt = 0;

    def __del__(self):
#       super(MissionControl, self).__del__() # bug in PyQt4?  the examples never do this
        self.conn.close()

    def failExit(self):
        # Get the most recent exception
        exceptionValue = sys.exc_info()[1]
        # Exit the script and show an error telling what happened.
        QMessageBox.warning(None, "open 'real-time'",
          QString("Database connection failed!\n -> %s" % exceptionValue))
        sys.exit(1)

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
        self.updateSelectionCnt += 1
        if (self.updateSelectionCnt % 30 == 0):
            self.updateSelection()

        currentDateTime = QDateTime.currentDateTime()

        self.CurrentTime.setText(currentDateTime.toString(DATETIME_FORMAT_VIEW))

        # update countdown clock
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

                box.setWindowModality(Qt.NonModal)
                box.show()

        self.sendDatagrams(currentDateTime)

    # send state to NIDAS every second via a UDP socket
    def sendDatagrams(self, currentDateTime):
        datetime = currentDateTime.toString(DATETIME_FORMAT_DATA)
        NOCAL = "NOCAL,%s,1" % datetime
        NOREC = "NOREC,%s,1" % datetime

        if self.DoNotCalibrate.isChecked():
            self.udpSocket.writeDatagram(NOCAL, QHostAddress("192.168.184.1"), PORT)

        if self.DoNotRecord.isChecked():
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

    def RadioButtonSelected(self):
#       print("RadioButtonSelected: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        for (key, value), rb in self.rbs.iteritems():
#           print "key: %s\tvalue: %s\tisChecked: %d" % (key, value, rb.isChecked())
            if rb.isChecked():
#               print "key: %s\tvalue: %s\t %d" % (key, value, rb.isChecked())
                try:
                    self.cursor.execute("UPDATE mission_control SET value = '%s' WHERE key='%s'" % (value, key))
                except:
                    self.failExit()

        self.cursor.execute("NOTIFY missioncontrol")
        self.conn.commit()
        self.updateSelection()

    def currentIndexChanged(self, key):
#       print "currentIndexChanged:", QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW)
        value = self.entries[key].currentText()
#       print "key:", key, "value:", value

        try:
            self.cursor.execute("UPDATE mission_control SET value = '%s' WHERE key='%s'" % (value, key))
        except:
            self.failExit()

        self.cursor.execute("NOTIFY missioncontrol")
        self.conn.commit()
        self.updateSelection()

    def selectOrInsert(self, key, value):

        # use current settings in database
        try:
            self.cursor.execute("SELECT value from mission_control WHERE key='%s'" % key)
            val = self.cursor.fetchone()
            return unicode(val[0])
        except:
            try:
                self.cursor.execute("INSERT INTO mission_control VALUES ('%s', '%s')" % (key, value))
            except:
                self.failExit()

            return value

    def horizontalRadioGroup(self, title, key, default, values):

        # use current setting in database for default
        default = self.selectOrInsert(key, default)

        groupBox = QGroupBox(title)
        group = QButtonGroup(self)
        group.setExclusive(True)
        hbox = QHBoxLayout()
        for val in values:
            rb = QPushButton(val)
            rb.setCheckable(True)
            hbox.addWidget(rb)
            group.addButton(rb)
            if (val == default):
              rb.setChecked(True)
            QObject.connect(rb, SIGNAL("toggled(bool)"), self.RadioButtonSelected)
            self.rbs[key, val] = rb

        groupBox.setLayout(hbox)
        return groupBox

    def horizontalEntryGroup(self, title, key, default, aRange):

#       print "horizontalEntryGroup:", QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW)
        default = QString.number(default)
#       print "key:", key, "default:", default

        # use current setting in database for default
        default = self.selectOrInsert(key, default)
#       print "key:", key, "default:", default

        hbox = QHBoxLayout()
        hbox.addWidget( QLabel("<b>"+title+"</b>") )
        entry = QComboBox()
        for item in range(aRange[0], aRange[1]+1):
            entry.addItem( QString.number(item) )

        entry.setCurrentIndex( entry.findText( default ) )

        hbox.addWidget(entry)
        self.entries[key] = entry

        QObject.connect(entry, SIGNAL("currentIndexChanged(QString)"), functools.partial(self.currentIndexChanged, key))
        return hbox

    def getCameraList(self):
#       print("getCameraList: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        try:
            self.cursor.execute("SELECT direction from camera")
            val = self.cursor.fetchone()
            direction = val[0]
        except:
            direction = ['forward']
        return direction

    def updateCameraList(self):
#       print("updateCameraList: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        direction = self.getCameraList()
        self.cameraList.removeWidget(self.camera)
        self.camera = self.horizontalRadioGroup("Camera feed to ground:", "camera", "forward", direction)
        self.cameraList.addWidget(self.camera)

    def updateSelection(self):
#       print("updateSelection: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.updateCameraList()

        for (key, value), rb in self.rbs.iteritems():
#           print "key: %s\tvalue: %s\tisChecked: %d" % (key, value, rb.isChecked())
            try:
#               print("SELECT value from mission_control WHERE key='%s'" % key)
                self.cursor.execute("SELECT value from mission_control WHERE key='%s'" % key)
                value = self.cursor.fetchone()
#               print("value is '%s'" % value[0])
                self.rbs[key, value[0]].setChecked(True)
            except:
                # don't fail when key is set and the UI hasn't updated yet to show the selection
                if (key != 'camera'):
                    self.failExit()

        for key, entry in self.entries.iteritems():
#           print "key: %s" % key
#           print("SELECT value from mission_control WHERE key='%s'" % key)
            self.cursor.execute("SELECT value from mission_control WHERE key='%s'" % key)
            value = self.cursor.fetchone()
#           print("value is '%s'" % value[0])
            index = entry.findText(value[0])
#           print("index is '%d'" % index)
            entry.setCurrentIndex(index)

    def initUI(self):
#       print("initUI: %s" % QDateTime.currentDateTime().toString(DATETIME_FORMAT_VIEW))
        self.setWindowTitle('Mission Control')
        startLabel    = QLabel("Start:")
        RemainLabel   = QLabel("Remain:")

        Line = QFrame()
        Line.setFrameShape(QFrame.HLine)
        Line.setFrameShadow(QFrame.Sunken)
        Line.setFixedHeight(20)

        NoteLabel    = QLabel("Note that both the IR sat and NWS radar are uploaded by default.\n")

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
        self.DoNotRecord.setEnabled(False)
        self.DoNotRecord.setCheckable(True)
        self.DoNotRecord.setChecked(False)
        self.DoNotRecord.clicked[bool].connect(self.setDoNotRecord)

        self.DoNotRecordStart = QLineEdit()
        self.DoNotRecordStart.setReadOnly(True)

        self.CurrentTime = QLineEdit()
        self.CurrentTime.setReadOnly(True)
        self.CurrentTime.setDisabled(True)

        direction = self.getCameraList()

        # setup radio buttons
        self.rbs = dict()

        self.region    = self.horizontalRadioGroup("Region (controls visable sat. and LMA location):", "region", "off", ("off", "CO", "AL", "OK"))
        self.cappi     = self.horizontalRadioGroup("CAPPI (all regions):", "cappi", "off", ("off", "on"))
        self.lightning = self.horizontalRadioGroup("LMA lightning:", "lightning", "off", ("off", "on"))
        self.camera    = self.horizontalRadioGroup("Camera feed to ground:", "camera", "forward", direction)

        self.cameraList = QStackedWidget()
        self.cameraList.addWidget(self.camera)

        # setup entry fields
        self.entries = dict()

        # setup numeric entry for lighting time span
        self.lightningTspan = self.horizontalEntryGroup("LMA lightning time span:", "lightningTspan", 6, [0, 10])

        # setup Postgres Notify/Listen connection
#       print "self.conn.fileno() %d" % self.conn.fileno()
        self.notify = QSocketNotifier(self.conn.fileno(), QSocketNotifier.Read)
        QObject.connect(self.notify, SIGNAL("activated(int)"), self.updateSelection)
        self.cursor.execute("LISTEN missioncontrol")
        self.conn.commit()

        # layout in a grid
        layout = QGridLayout()
        layout.addWidget(self.DoNotCalibrate,      0, 1)
        layout.addWidget(self.DoNotRecord,         0, 2)
        layout.addWidget(startLabel,               1, 0)
        layout.addWidget(self.DoNotCalibrateStart, 1, 1)
        layout.addWidget(self.DoNotRecordStart,    1, 2)
        layout.addWidget(RemainLabel,              2, 0)
        layout.addWidget(self.remainingTime,       2, 1)
        layout.addWidget(self.CurrentTime,         2, 2)
        layout.addWidget(Line,                     3, 0, 1, 3)
        layout.addWidget(NoteLabel,                4, 0, 1, 3)
        layout.addWidget(self.region,              5, 0, 1, 3)
        layout.addWidget(self.cappi,               6, 0, 1, 3)
        layout.addWidget(self.lightning,           7, 0, 1, 3)
        layout.addLayout(self.lightningTspan,      8, 0, 1, 3)
        layout.addWidget(self.cameraList,          9, 0, 1, 3)
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
    mc = MissionControl()
    mc.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)
    mc.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

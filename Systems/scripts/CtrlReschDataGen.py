#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Control Research Data Generation

Two toggle buttons are created to append '(NO|YES)CALIB' and
'(NO|YES)RESCH' flags to the end of the IWG1 stream broadcast
on the aircraft.  This is done by setting 

Instruments shall use these flags to restrict calibration and
gathering of research data.
"""

import sys
from PyQt4 import QtGui
from PyQt4.QtSql import *

class CtrlReschDataGen(QtGui.QWidget):

    def __init__(self):
        super(CtrlReschDataGen, self).__init__()

        # connect to the aircraft's real-time database
        self.db = QSqlDatabase("QPSQL7")

        self.db.setHostName("acserver")
        self.db.setUserName("ads")
        self.db.setDatabaseName("real-time")

        if not self.db.open():
            QMessageBox.warning(None, "open 'real-time'",
                QString("Database Error: %1").arg(self.db.lasterror().text()))
            sys.exit(1)

        self.query = QSqlQuery(self.db)

        self.initUI()

    def __del__(self):
#       super(CtrlReschDataGen, self).__del__() # bug in PyQt4?  the examples never do this
        self.query.finish()
        self.db.close()

    def initUI(self):
        self.setGeometry(300, 300, 350, 50)
        self.setWindowTitle('Control Research Data Generation')

        # setup NoCalib
        noCalib = QtGui.QPushButton('No Calibration', self)
        noCalib.move(10, 10)
        noCalib.setCheckable(True)
        noCalib.clicked[bool].connect(self.setNoCalib)

        self.query.exec_("SELECT value from global_attributes WHERE key='NoCalib'")
        if self.query.next():
            if unicode(self.query.value(0).toString()) == 'TRUE':
                noCalib.setChecked(True)
        else:
            self.query.exec_("INSERT INTO global_attributes VALUES ('NoCalib', 'FALSE')")

        # setup NoResch
        noResch = QtGui.QPushButton('No Research', self)
        noResch.move(210, 10)
        noResch.setCheckable(True)
        noResch.clicked[bool].connect(self.setNoResch)

        self.query.exec_("SELECT value from global_attributes WHERE key='NoResch'")
        if self.query.next():
            if unicode(self.query.value(0).toString()) == 'TRUE':
                noResch.setChecked(True)
        else:
            self.query.exec_("INSERT INTO global_attributes VALUES ('NoResch', 'FALSE')")

        self.show()

    def setNoCalib(self, pressed):
        if pressed: val = 'TRUE'
        else:       val = 'FALSE'
        self.query.exec_("UPDATE global_attributes SET value='%s' WHERE key='NoCalib'" % val)

    def setNoResch(self, pressed):
        if pressed: val = 'TRUE'
        else:       val = 'FALSE'
        self.query.exec_("UPDATE global_attributes SET value='%s' WHERE key='NoResch'" % val)


def main():

    app = QtGui.QApplication(sys.argv)
    crdg = CtrlReschDataGen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#
# ncpp C++ class makefile
#
INC=	../include
RAFINC=	${JLOCAL}/include
O2D=	../obj

#	Solaris
#
#INCLUDES=	-I${INC} -I${RAFINC} -I/usr/dt/include
#DEFINES=	-DSVR4

#	Linux
#
#INCLUDES= -I${INC} -I${RAFINC} -I/usr/X11R6/include
#DEFINES=

#CXXFLAGS=	-O ${INCLUDES} ${DEFINES}

OBJS=	Ascii.o CanvasWindow.o DataFile.o DataSet.o DataSource.o\
	EditDiameters.o EditPlotParms.o FileMgr.o\
	Header.o MovieControl.o Panel.o PlotInfo.o PlotMgr.o\
	Probe.o Probe200.o SetMgr.o\
	Titles.o VarsWin.o Colors.o\
	fssp.o s100.o s200.o f300.o pcasp.o x260.o x200.o y200.o\
	2D_C.o 2D_P.o hvps.o

SRCS=	Ascii.cc CanvasWindow.cc DataFile.cc DataSet.cc DataSource.cc\
	EditDiameters.cc EditPlotParms.cc FileMgr.cc Header.cc\
	MovieControl.cc Panel.cc PlotInfo.cc PlotMgr.cc\
	Probe.cc Probe200.cc SetMgr.cc Titles.cc\
	VarsWin.cc Colors.cc\
	fssp.cc s100.cc s200.cc f300.cc pcasp.cc x260.cc x200.cc y200.cc\
	2D_C.cc 2D_P.cc hvps.cc

HDRS=	${INC}/define.h

all: ${OBJS}


${OBJS}: ${HDRS}

Ascii.o:		${INC}/Ascii.h ${INC}/SetMgr.h ${RAFINC}/TextWindow.h ${INC}/DataSet.h ${INC}/PlotMgr.h ${INC}/PlotInfo.h
CanvasWindow.o:		${INC}/CanvasWindow.h ${RAFINC}/Window.h

DataFile.o:		${INC}/DataFile.h ${INC}/Probe.h ${RAFINC}/Time.h ${INC}/fssp.h ${INC}/f300.h ${INC}/pcasp.h ${INC}/x260.h ${INC}/x200.h ${INC}/y200.h ${INC}/s100.h ${INC}/hvps.h
DataSet.o:		${INC}/DataSet.h ${INC}/Probe.h ${INC}/DataFile.h
DataSource.o:		${INC}/DataSource.h ${INC}/FileMgr.h ${INC}/SetMgr.h ${INC}/Probe.h

EditDiameters.o:	${INC}/EditDiameters.h ${RAFINC}/Window.h ${INC}/FileMgr.h
EditPlotParms.o:	${INC}/EditPlotParms.h ${RAFINC}/Window.h
FileMgr.o:		${INC}/FileMgr.h ${INC}/DataFile.h
Header.o:		${INC}/Header.h ${RAFINC}/TextWindow.h
MovieControl.o:		${INC}/MovieControl.h ${RAFINC}/Window.h ${RAFINC}/Time.h ${INC}/PlotMgr.h ${RAFINC}/Application.h ${INC}/FileMgr.h ${INC}/PlotMgr.h ${INC}/SetMgr.h

Panel.o:		${INC}/Panel.h ${RAFINC}/Canvas.h ${INC}/DataSet.h ${INC}/PlotInfo.h ${RAFINC}/PostScript.h ${RAFINC}/PixMap.h ${RAFINC}/XFonts.h ${RAFINC}/XPen.h

PlotInfo.o:		${INC}/PlotInfo.h ${RAFINC}/Canvas.h ${INC}/Panel.h ${RAFINC}/Printer.h ${INC}/SetMgr.h ${INC}/Colors.h ${RAFINC}/XFonts.h ${RAFINC}/XPen.h ${RAFINC}/PostScript.h

PlotMgr.o:		${INC}/PlotMgr.h ${RAFINC}/Window.h ${INC}/DataSource.h ${RAFINC}/Canvas.h ${INC}/DataFile.h ${INC}/EditPlotParms.h ${INC}/PlotInfo.h ${INC}/SetMgr.h ${INC}/Colors.h ${RAFINC}/XFonts.h ${RAFINC}/XPen.h

SetMgr.o:		${INC}/SetMgr.h ${INC}/DataSet.h
Titles.o:		${INC}/Titles.h
VarsWin.o:		${INC}/VarsWin.h ${RAFINC}/TextWindow.h ${INC}/SetMgr.h ${INC}/PlotMgr.h ${INC}/PlotInfo.h

Colors.o:		${INC}/Colors.h


Probe.o:		${INC}/Probe.h
Probe200.o:		${INC}/Probe200.h ${INC}/Probe.h
fssp.o:			${INC}/fssp.h ${INC}/Probe.h
s100.o:			${INC}/s100.h ${INC}/Probe.h
s200.o:			${INC}/s200.h ${INC}/Probe.h
f300.o:			${INC}/f300.h ${INC}/Probe.h
pcasp.o:		${INC}/pcasp.h ${INC}/Probe.h
hvps.o:			${INC}/hvps.h ${INC}/Probe.h
x260.o:			${INC}/x260.h ${INC}/Probe200.h ${INC}/Probe.h
x200.o:			${INC}/x200.h ${INC}/Probe200.h ${INC}/Probe.h
y200.o:			${INC}/y200.h ${INC}/Probe200.h ${INC}/Probe.h
2D_P.o:			${INC}/2D_P.h ${INC}/Probe200.h ${INC}/Probe.h
2D_C.o:			${INC}/2D_C.h ${INC}/Probe200.h ${INC}/Probe.h


clean:
	${RM} *.o

#
# xpms2d C++ class makefile
#
RAFINC=	${JLOCAL}/include
I2D=	../include
O2D=	../obj

OBJS=	CanvasWindow.o Colors.o ControlWindow.o\
	DataFile.o Enchilada.o FileMgr.o Hex.o\
	Magnify.o MagnifyCanvas.o MagnifyWindow.o\
	MainCanvas.o Probe.o

SRCS=	CanvasWindow.cc Colors.cc ControlWindow.cc\
	DataFile.cc Enchilada.cc FileMgr.cc Hex.cc\
	Magnify.cc MagnifyCanvas.cc MagnifyWindow.cc\
	MainCanvas.cc Probe.cc

HDRS=	${I2D}/define.h

all: ${OBJS}


${OBJS}: ${HDRS}

CanvasWindow.o:		${I2D}/CanvasWindow.h ${RAFINC}/Window.h

ControlWindow.o:	${I2D}/ControlWindow.h ${I2D}/FileMgr.h ${I2D}/DataFile.h
Colors.o:		${I2D}/Colors.h ${I2D}/MainCanvas.h

DataFile.o:		${I2D}/DataFile.h ${RAFINC}/hdrAPI.h ${I2D}/Probe.h

FileMgr.o:		${I2D}/FileMgr.h ${I2D}/DataFile.h
Hex.o:			${I2D}/Hex.h ${RAFINC}/TextWindow.h
Enchilada.o:		${I2D}/Enchilada.h ${RAFINC}/TextWindow.h
Magnify.o:		${I2D}/Magnify.h ${I2D}/MainCanvas.h ${I2D}/MagnifyCanvas.h ${I2D}/Colors.h
MagnifyCanvas.o:	${I2D}/MagnifyCanvas.h ${RAFINC}/Canvas.h ${RAFINC}/Cursor.h
MagnifyWindow.o:	${I2D}/MagnifyWindow.h ${RAFINC}/Window.h
MainCanvas.o:		${I2D}/MainCanvas.h ${I2D}/Colors.h ${RAFINC}/Canvas.h
Probe.o:		${I2D}/Probe.h ${RAFINC}/hdrAPI.h


clean:
	${RM} *.o

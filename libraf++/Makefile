#
# libraf++ makefile
#
RELEASE=${JLOCAL}/lib
I2D=	${JLOCAL}/include


LIBNAME=	raf++

INCLUDES=	-I${I2D} -I/usr/X11R6/include
#DEFINES=	-DSVR4
CXXFLAGS=	-g -O2 ${INCLUDES} ${DEFINES}

OBJS=	adsIO.o adsIOrt.o Application.o Canvas.o Cursor.o hdrAPI.o gettext.o\
	ntohf.o PixMap.o PMSspex.o PostScript.o Printer.o Queue.o tapeIO.o\
	TextWindow.o Time.o validate.o Window.o XFonts.o XPen.o XmError.o\
	XmFile.o XmQuery.o XmWarn.o

SRCS=	adsIO.cc adsIOrt.cc Application.cc Canvas.cc Cursor.cc hdrAPI.cc\
	gettext.cc ntohf.cc PixMap.cc PMSspex.cc PostScript.o Printer.cc\
	Queue.cc tapeIO.cc TextWindow.o Time.cc validate.cc Window.cc\
	XFonts.cc XPen.cc XmError.cc XmFile.cc XmQuery.cc XmWarn.cc

all: ${OBJS}
	rm -f lib${LIBNAME}.a
	ar cr lib${LIBNAME}.a ${OBJS}

install: all
	cp -fp lib${LIBNAME}.a ${RELEASE}
	cp -fp *.h ${I2D}


# IO classes.
tapeIO.o:	tapeIO.h
hdrAPI.o:	hdrAPI.h tapeIO.h ntohf.h
adsIO.o:	adsIO.h hdrAPI.h tapeIO.h
adsIOrt.o:	adsIOrt.h hdrAPI.h
PMSspex.o:	PMSspex.h
ntohf.o:	ntohf.h

Queue.o:	Queue.h
Time.o:		Time.h

# X-window classes.
Application.o:	Application.h
Canvas.o:	Canvas.h
Cursor.o:	Cursor.h
Printer.o:	Printer.h Window.h
Window.o:	Window.h

# XLib classes
PixMap.o:	PixMap.h
XFonts.o:	XFonts.h
XPen.o:		XPen.h


# Motif dialog boxes
XmError.o:	XmError.h
XmFile.o:	XmFile.h
XmQuery.o:	XmQuery.h
XmWarn.o:	XmWarn.h


clean:
	${RM} *.o lib${LIBNAME}.a

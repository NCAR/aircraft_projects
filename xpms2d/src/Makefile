#
# Makefile for xpms2d
#
BIN	= ${LOCAL}/bin
WWW	= /net/www/docs/raf/Software
RELEASE = ${LOCAL}/xpms2d

INC	= ../include
RAFINC	= ${JLOCAL}/include
C2D	= ../class
O2D	= ../class

#       Solaris
#
DEFINES	= -DSVR4 -DPNG
INCLUDES= -I${INC} -I${RAFINC} -I/usr/dt/include
LIB_DIRS= -L${JLOCAL}/lib
LIBS    = -lraf++ -Wl,-Bstatic -lpng -lz -Wl,-Bdynamic -R /usr/dt/lib -lXm -lXt -lX11
IHOST	= mead
ANONFTP	= /net/ftp/pub/src/bin.Solaris2.9
 
#       Linux
#
DEFINES	= -DPNG
INCLUDES= -I${INC} -I/usr/X11R6/include -I${RAFINC}
LIB_DIRS= -L/usr/X11R6/lib -L${JLOCAL}/lib
LIBS   = -lraf++ -lXm -lXt -LSM -lICE -lXext -lXp -lX11 -lpng -lz
IHOST	= syrah
ANONFTP	= /net/ftp/pub/archive/RAF-src/bin.RedHat9.0



# Don't use optimization with gcc (2.95.2 and earlier) and C++.
CXX	= g++
CXXFLAGS= -g -O ${INCLUDES} ${DEFINES}

PROG	= xpms2d
HDRS	= ${INC}/define.h

SRCS=	xpms2d.cc global.cc ccb.cc cb_canvas.cc cb_control.cc cb_mag.cc\
	cb_menus.cc cb_printer.cc cb_text.cc process.cc

OBJS=	xpms2d.o global.o ccb.o cb_canvas.o cb_control.o cb_mag.o\
	cb_menus.o cb_printer.o cb_text.o process.o


O2DOB=	${O2D}/CanvasWindow.o\
	${O2D}/ControlWindow.o ${O2D}/Colors.o ${O2D}/Enchilada.o\
	${O2D}/DataFile.o ${O2D}/FileMgr.o ${O2D}/Hex.o\
	${O2D}/Magnify.o ${O2D}/MagnifyCanvas.o ${O2D}/MagnifyWindow.o\
	${O2D}/MainCanvas.o ${O2D}/Probe.o


${PROG}: ${OBJS} classDir
	${CXX} ${CXXFLAGS} ${LIB_DIRS} ${OBJS} ${O2DOB} ${LIBS} -o $@

classDir:
	cd ${O2D}; gmake "CXXFLAGS=${CXXFLAGS}"

release:
	(cd ..; tar cFFf - . | (cd ${RELEASE}; tar xfBp -))
	sed s/-g/-O2/g ../class/Makefile > ${RELEASE}/class/Makefile
	sed s/-g/-O2/g Makefile > ${RELEASE}/src/Makefile
	(cd ..; tar cFFf - . | (cd /home/linux/xpms2d; tar xfBp -))
	sed s/-g/-O/g ../class/Makefile > /home/linux/xpms2d/class/Makefile
	sed s/-g/-O/g Makefile > /home/linux/xpms2d/src/Makefile
	rm -f ${RELEASE}/LOCK.make

install: ${PROG}
	cp ${PROG} ${BIN}
	rcp ${PROG} ${IHOST}:${BIN}
	cp ${PROG} ${ANONFTP}
	cp ${PROG}.html ${WWW}

clean:
	(cd ../class; make clean)
	${RM} core* ${OBJS} ${PROG}

print:
	enscript -2Gr -b${PROG} ${HDRS} ${SRCS}

${OBJS}:	${HDRS}

xpms2d.o:	${RAFINC}/Application.h ${INC}/CanvasWindow.h ${INC}/Colors.h ${INC}/ControlWindow.h ${RAFINC}/Cursor.h ${INC}/FileMgr.h ${INC}/DataFile.h ${RAFINC}/XFonts.h ${RAFINC}/XPen.h ${INC}/MagnifyWindow.h ${INC}/MainCanvas.h ${RAFINC}/Printer.h ${RAFINC}/XmError.h ${RAFINC}/XmFile.h ${RAFINC}/XmWarn.h ${INC}/fbr.h

cb_canvas.o:	${INC}/MainCanvas.h ${INC}/Magnify.h
cb_control.o:	${RAFINC}/Cursor.h ${INC}/FileMgr.h ${INC}/MainCanvas.h ${INC}/ControlWindow.h ${INC}/Colors.h
cb_mag.o:	${INC}/MagnifyCanvas.h
cb_menus.o:	${RAFINC}/Application.h ${INC}/ControlWindow.h ${RAFINC}/Cursor.h ${INC}/FileMgr.h ${INC}/MainCanvas.h ${RAFINC}/PostScript.h ${RAFINC}/Printer.h ${RAFINC}/XmFile.h
cb_printer.o:	${RAFINC}/Printer.h
cb_text.o:	${RAFINC}/TextWindow.h
process.o:	${INC}/ControlWindow.h

#
#    Makefile for hdrbld program
#
CC=		g++
BINDIR=		${JLOCAL}/bin
MANDIR=		${JLOCAL}/man/manl

# Solaris
#
DEFINES= -DSVR4
INCLUDES= ${JLOCAL}/include -I/usr/openwin/include -I/usr/dt/include
LIB_DIRS= -L${JLOCAL}/lib
LIBS= -R /usr/dt/lib -lVarDB -lpms -lAircraft -lraf -lhdr_api -lXm -lXt -lX11

# Linux
#
INCLUDES= ${JLOCAL}/include -I/usr/X11R6/include
DEFINES = 
LIB_DIRS= -L/usr/X11R6/lib -L${JLOCAL}/lib
LIBS    = -lVarDB -lpms -lAircraft -lraf -lhdr_api -lXm -lXp -lXt -lXext -lX11

CFLAGS=		-g ${DEFINES} -I${INCLUDES}

SRCS=	Xwin.cc cb_ac.cc cb_file.cc cb_edit.cc cb_proj.cc dsm.cc\
	fork.cc globals.cc hardwire.cc hdrbld.cc init.cc\
	log.cc menu.cc opMenu.cc projFile.cc pms.cc\
	setNav.cc setOther.cc setSh.cc setPMS.cc sort.cc

OBJS=	Xwin.o cb_ac.o cb_file.o cb_edit.o cb_proj.o dsm.o\
	fork.o globals.o hardwire.o hdrbld.o init.o\
	log.o menu.o opMenu.o projFile.o pms.o\
	setNav.o setOther.o setSh.o setPMS.o sort.o

HDRS=	hdrbld.h ${JLOCAL}/include/header.h ${JLOCAL}/include/vardb.h

HWOBJS=	Xwin.o cb_edit.o cb_file.o dsm.o hardwire.o projFile.o setNav.o \
	setSh.o sort.o pms.o setPMS.o

PROG=	hdrbld

.cc.o:
	${CC} ${CFLAGS} -c $*.cc

${PROG}: ${OBJS}
	${CC} ${CFLAGS} ${OBJS} ${LIB_DIRS} ${LIBS} -o $@

install: ${PROG}
	cp ${PROG} ${BINDIR}

clean:
	rm -f ${OBJS} ${PROG}

lint:
	lint ${INCLUDES} ${SRCS} ${LINTLIBS}

print:
	enscript -2Gr -b${PROG} ${HDRS} ${SRCS}

${OBJS}:	${HDRS}
${HWOBJS}:	hardwire.h
hdrbld.o:	fbr.h

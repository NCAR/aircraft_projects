#
# Outside users, you may remove util.c cio.c if they don't compile.
#
DESTDIR=
LIBDIR=		${JLOCAL}/lib
LINTDIR=	${JLOCAL}/lib/lint
MANDIR=		${JLOCAL}/man/man3
INCLUDEDIR=	${JLOCAL}/include
CC=		gcc
FF=		f77

LIBNAME=	raf

INCLUDES=	-I/usr/X11R6/include -I${JLOCAL}/include
CFLAGS=		-g -O2 ${INCLUDES} 
FFLAGS=		-O

OBJS=	strupr.o tapeIO.o getmem.o Xerror.o Xquery.o Xfile.o Xwarn.o \
	util.o queue.o chost.o date.o portable.o
# cio.o flote.o sendhc.o sendpr.o 

SRCS=	strupr.c tapeIO.c getmem.c Xerror.c Xquery.c Xfile.c Xwarn.c \
	util.c queue.c chost.c date.c portable.c
# cio.c flote.f sendhc.f sendpr.f 

HDRS=	

.SUFFIXES: .o .h .c .cc

.c.o:
	${CC} ${CFLAGS} -c $*.c -o $*.o

.cc.o:
	${CC} ${CFLAGS} -c $*.cc

.f.o:
	${FF} ${FFLAGS} -c $*.f

all: lib${LIBNAME}.a

${OBJS}: ${HDRS}

lib${LIBNAME}.a: ${OBJS}
	rm -f lib${LIBNAME}.a
	ar cr lib${LIBNAME}.a ${OBJS}

lint:
	lint -C${LIBNAME} ${INCLUDES} *.c

install: all
	cp -p lib${LIBNAME}.a ${DESTDIR}/${LIBDIR}

include:
	install -c -m 0444 ${LIBNAME}.h ${DESTDIR}/${INCLUDEDIR}

clean:
	rm -f *.o *.a *.ln profiled/*.o

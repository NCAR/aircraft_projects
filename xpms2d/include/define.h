/*
-------------------------------------------------------------------------
OBJECT NAME:	define.h

FULL NAME:	Include File to Include the Include Files

DESCRIPTION:	
-------------------------------------------------------------------------
*/

#ifndef DEFINE_H
#define DEFINE_H

#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <iostream>

#include <string.h>

#include <Xm/Xm.h>

#include "Queue.h"

typedef unsigned long	ulong;
typedef unsigned short	ushort;

#ifndef NULL
#define NULL		(0)
#endif
 
#ifndef ERR
#define OK		(0)
#define ERR		(-1)
#endif
 
#define COMMENT		'#'	/* Comment character for textfiles  */
 
#define SecondsSinceMidnite(t)	(t[0] * 3600 + t[1] * 60 + t[2])


#define BUFFSIZE	2048
#define PATH_LEN	256
#define NAMELEN		16

#define	SPACE		' '

#define MAX_DATAFILES	2
#define MAX_DATASETS	4
#define MAX_PANELS	4
#define MAX_PROBES	4

#define TITLESIZE	80

#define ALL_SETS	(-1)


struct particle
  {
  long  time;           // Seconds since mid-night
  long  msec;

  int	w, h;
  int	area;
  bool	reject;
  bool	edge;		// particle touched either edge
  bool	timeReject;	// Nimbus will reject (because of bad timing bar)

  ushort	x1, x2;		// for particles that touch both edges.
  ulong		timeWord;
  ulong		deltaTime;	// Amount of time between prev & this particle
  ulong		liveTime;	// Amount of time consumed by particle
//  ulong	*p;
  };

typedef struct particle Particle;


struct recStats
  {
  ulong	DASelapsedTime;		// milliseconds.
  ulong	tBarElapsedtime;	// milliseconds.

  int	nTimeBars;		// n Particles.
  int	accum[1024];
  int	nonRejectParticles;	// n Particles not rejected.
  ulong	minBar, maxBar, meanBar;

  double	SampleVolume, DOFsampleVolume;
  double	tas, concentration, lwc, dbz;
  float		frequency;              // TAS clock.
  int		resolution, area;

  Queue		particles;
  };


/* Values for rejection/concentration stuff*/
enum { NONE, ENTIRE_IN, CENTER_IN, RECONSTRUCTION };

/* Values for "displayLevel"		*/
enum { NORMAL, DIAGNOSTIC, ENCHILADA };

/* Values for "HandleError"		*/
enum { RETURN, EXIT, IRET };


extern char buffer[], *outFile, DataPath[], *timeSeg, pngPath[], psPath[];

extern bool	Interactive, DataChanged, UTCseconds;


void	GetDataFileName(Widget, XtPointer, XtPointer),
	NewDataFile(Widget, XtPointer, XtPointer),
	AddDataFile(Widget, XtPointer, XtPointer),
	EditPrintParms(Widget, XtPointer, XtPointer),
	PrintSave(Widget, XtPointer, XtPointer),
	SavePNG(Widget, XtPointer, XtPointer),
	Quit(Widget, XtPointer, XtPointer);

void	CanvasExpose(Widget, XtPointer, XtPointer),
	CanvasInput(Widget, XtPointer, XtPointer),
	CanvasResize(Widget, XtPointer, XtPointer);

void	MagnifyExpose(Widget, XtPointer, XtPointer),
	MagnifyInput(Widget, XtPointer, XtPointer),
	MagnifyResize(Widget, XtPointer, XtPointer);

void	ApplyTimeChange(Widget, XtPointer, XtPointer),
	ModifyActiveVars(Widget, XtPointer, XtPointer),
	PageForward(Widget, XtPointer, XtPointer),
	PageBackward(Widget, XtPointer, XtPointer),
	ToggleWrap(Widget, XtPointer, XtPointer),
	ToggleTiming(Widget, XtPointer, XtPointer),
	PageCurrent(), SetSampleArea(),
	SetCurrentFile(Widget, XtPointer, XtPointer),
	ViewHex(Widget, XtPointer, XtPointer),
	ViewEnchilada(Widget, XtPointer, XtPointer),
	SetDensity(Widget, XtPointer, XtPointer),
	SetConcentration(Widget, XtPointer, XtPointer),
	ForkNetscape(Widget, XtPointer, XtPointer),
	SetScaleTime(Widget, XtPointer, XtPointer),
	StartMovie(Widget, XtPointer, XtPointer),
	StopMovie(Widget, XtPointer, XtPointer),
	SetScaleSpeed(Widget, XtPointer, XtPointer),
	SetProbe(Widget, XtPointer, XtPointer),
	SetPanel(Widget, XtPointer, XtPointer);

void	DismissWindow(Widget, XtPointer, XtPointer),
	DestroyWindow(Widget, XtPointer, XtPointer),
	ToggleDisplay(Widget, XtPointer, XtPointer),
	ToggleSynthetic(Widget, XtPointer, XtPointer),

	ValidateTime(Widget w, XtPointer client, XtPointer call),
        ValidateFloat(Widget w, XtPointer client, XtPointer call),
        ValidateInteger(Widget w, XtPointer client, XtPointer call);

void	ErrorMsg(char msg[]), FlushEvents(),
	WarnMsg(char msg[], XtCallbackProc okCB, XtCallbackProc cancelCB);

#endif

/* END DEFINE.H */

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

#include <string>
#include <iostream>

#include <Xm/Xm.h>

#ifndef NULL
#define NULL		(0)
#endif
 
#ifndef ERR
#define OK		(0)
#define ERR		(-1)
#endif
 
#define COMMENT		'#'	/* Comment character for textfiles  */
 
#define SecondsSinceMidnite(t)	(t[0] * 3600 + t[1] * 60 + t[2])


#define BUFFSIZE	4096
#define PATH_LEN	256
#define NAMELEN		20

#define MAX_DATAFILES	3
#define MAX_PROBES	12
#define MAX_DATASETS	6
#define MAX_PANELS	4

#define TITLESIZE	80

#define ALL_SETS	(-1)

#define MAX_FONTS	6

/* Values for "HandleError"		*/
enum { RETURN, EXIT, IRET };


enum PlotType   { XY, XYZ };
enum NormType	{ NONE, LINEAR, LOG };
//enum DataType	{ COUNTS=0x01, CONCENTRATION=0x02, SURFACE=0x04, VOLUME=0x08 };

typedef int DataType;

#define	COUNTS		0x01
#define CONCENTRATION	0x02
#define SURFACE		0x04
#define VOLUME		0x08

#define N_PLOTTYPES	2


extern char buffer[], DataPath[], UserPath[];

extern bool	Interactive, DataChanged, UTCseconds;

void	GetDataFileName(Widget, XtPointer, XtPointer),
	NewDataFile(Widget, XtPointer, XtPointer),
	AddDataFile(Widget, XtPointer, XtPointer),
	GenerateFile(Widget, XtPointer, XtPointer),
	EditPrintParms(Widget, XtPointer, XtPointer),
	PrintSave(Widget, XtPointer, XtPointer),
	SavePNG(Widget, XtPointer, XtPointer),
	Quit(Widget, XtPointer, XtPointer);

void	EditParms(Widget w, XtPointer client, XtPointer call),
	EditDiams(Widget w, XtPointer client, XtPointer call),
	ApplyDiams(Widget w, XtPointer client, XtPointer call),
	SetDiams(Widget w, XtPointer client, XtPointer call),
	SetPlotPanel(Widget w, XtPointer client, XtPointer call),
	ApplyParmsWindow(Widget w, XtPointer client, XtPointer call),
	SetParmsWindow(Widget w, XtPointer client, XtPointer call),
	AutoTitle_CB(Widget w, XtPointer client, XtPointer call),
	AutoLabel_CB(Widget w, XtPointer client, XtPointer call),
	AutoScale_CB(Widget w, XtPointer client, XtPointer call),
	AutoTic_CB(Widget w, XtPointer client, XtPointer call);

void	CanvasExpose(Widget, XtPointer, XtPointer),
	CanvasInput(Widget, XtPointer, XtPointer),
	CanvasResize(Widget, XtPointer, XtPointer);

void	ApplyTimeChange(Widget, XtPointer, XtPointer),
	ApplyAveragePeriod(Widget, XtPointer, XtPointer),
	ModifyActiveProbes(Widget, XtPointer, XtPointer),
	ModifyActiveDataTypes(Widget, XtPointer, XtPointer),
	PageForward(Widget, XtPointer, XtPointer),
	PageBackward(Widget, XtPointer, XtPointer),
	SetPlotTypeCB(Widget, PlotType, XtPointer),
	SetScaleType(Widget, XtPointer, XtPointer),
	SetCurrentFile(Widget, XtPointer, XtPointer),
	Set_nPanels(Widget, XtPointer, XtPointer),
	SetNormalization(Widget, XtPointer, XtPointer),
	ToggleDITC_CB(Widget, XtPointer, XtPointer),
	ToggleGrid_CB(Widget, XtPointer, XtPointer),
	ToggleColor_CB(Widget, XtPointer, XtPointer),
	ToggleCompute(Widget, XtPointer, XtPointer),
	SetFileNames(), SetProbeNames(), SetStartEndTime();

void	StopMovie(Widget, XtPointer, XtPointer),
	StartMovie(Widget, XtPointer, XtPointer),
	SetMovieSpeed(Widget, XtPointer, XtPointer),
	SetScaleTime(Widget, XtPointer, XtPointer),
	SetScaleSpeed(Widget, XtPointer, XtPointer);

void	ViewASCII(Widget, XtPointer, XtPointer), UpdateASCII(),
	ViewVars(Widget, XtPointer, XtPointer), UpdateVars(),
	ViewTitles(Widget, XtPointer, XtPointer),
	ViewHeader(Widget, XtPointer, XtPointer);

void	DismissWindow(Widget, XtPointer, XtPointer),
	DestroyWindow(Widget, XtPointer, XtPointer),

	ApplyPrintParms(Widget, XtPointer, XtPointer),

	ForkNetscape(Widget, XtPointer, XtPointer),

	ValidateTime(Widget w, XtPointer client, XtPointer call),
        ValidateFloat(Widget w, XtPointer client, XtPointer call),
        ValidateInteger(Widget w, XtPointer client, XtPointer call);

std::string	MakeLogTicLabel(double value),
	MakeTimeTicLabel(int indx, int nTics),
	MakeTicLabel(float diff, int majorTics, double value);

int	GetTextInt(const Widget w);
float	GetTextFloat(const Widget w);
void	GetTextString(const Widget w, std::string& s);

void	ErrorMsg(char msg[]);

#endif

/* END DEFINE.H */

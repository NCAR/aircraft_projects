/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_movie.cc

FULL NAME:	Callback Wrappers for Movie

ENTRY POINTS:	SetScaleTime()
		SetScaleSpeed()
		StartMovie()
		StopMovie()

STATIC FNS:	

DESCRIPTION:	Callbacks specific to the movie option.  See also
		cb_control.cc for other callbacks.

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "define.h"

#include "Cursor.h"
#include "MovieControl.h"
#include "PlotMgr.h"

extern MovieControl	*movieControlGUI;
extern PlotManager	*plotMgr;
extern XCursor		cursor;


/* -------------------------------------------------------------------- */
void StartMovie(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->Start();
  movieControlGUI->Stop();

}	/* END STARTMOVIE */

/* -------------------------------------------------------------------- */
void StopMovie(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->Stop();

}	/* END STOPMOVIE */

/* -------------------------------------------------------------------- */
void SetScaleTime(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->PositionTime();
  plotMgr->DrawImage();

}	/* END SETSCALETIME */

/* -------------------------------------------------------------------- */
void SetScaleSpeed(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->SetDelay();

}	/* END SETSCALESPEED */

/* END CB_MOVIE.CC */

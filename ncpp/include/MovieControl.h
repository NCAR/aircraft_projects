/*
-------------------------------------------------------------------------
OBJECT NAME:	MovieControl.h

FULL NAME:	Create Movie Control Window

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#ifndef MOVIEWIN_H
#define MOVIEWIN_H

#include "define.h"

#include "Time.h"
#include "Application.h"
#include "FileMgr.h"
#include "PlotMgr.h"
#include "SetMgr.h"
#include "Window.h"

#include <Xm/Form.h>
#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/PushB.h>
#include <Xm/RowColumn.h>
#include <Xm/Scale.h>
#include <Xm/TextF.h>

/* -------------------------------------------------------------------- */
class MovieControl : public WinForm {

public:
		MovieControl(Widget parent);

  int		AveragePeriod() const	{ return(avRate); }

  void		UpdateAveragePeriod();
  void		SetAveragePeriod(int av);

  void		TurnOnAverage()		{ XtSetSensitive(averageText, True); }
  void		TurnOffAverage()	{ XtSetSensitive(averageText, False); }

  void		UpdateTime();
  void		PositionTime();
  void		SetDelay();
  void		SetRowsCols(int r, int c);
  void		SetDefaultStartEndTime();

  void		Start();	// thread to run movie.
  void		Stop();		// clean up movie.

  void		StepForward();
  void		StepBackward();


private:
  Widget	timeText, averageText, delayScale, timeScale, butt[4];

  FlightClock	startTime, endTime, currTime;
  int		numberSeconds, avRate, delay, nRows, nCols;
  bool		movieRunning;

  void		createXwindow(Widget parent);

};	/* END MOVIECONTROL.H */

#endif

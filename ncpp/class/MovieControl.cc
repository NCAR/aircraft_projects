/*
-------------------------------------------------------------------------
OBJECT NAME:	MovieControl.cc

FULL NAME:	Movie Control Window

ENTRY POINTS:	MovieControl()
		PopUp()
		UpdateAveragePeriod()
		UpdateTime()
		PositionTime()
		SetRowsCols()
		StepForward()
		StepBackward()
		Start()
		Stop()
		createXwindow()

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "MovieControl.h"
#include <unistd.h>

extern Application	*application;
extern FileManager	fileMgr;
extern PlotManager	*plotMgr;
extern SetManager	setMgr;

#ifdef SVR4
extern "C" { int usleep(unsigned int); }
#endif

/* -------------------------------------------------------------------- */
MovieControl::MovieControl(Widget parent) : WinForm(parent, "movie", RowColumn)
{
  createXwindow(parent);

  XtSetSensitive(butt[1], False);	// Disable "stop" button.

  XmTextFieldSetString(averageText, "10");
  UpdateAveragePeriod();

  if (fileMgr.CurrentFile())
    SetDefaultStartEndTime();
  else
    numberSeconds = 0;

  delay = 0;
  nRows = nCols = 1;
  movieRunning = False;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void MovieControl::UpdateAveragePeriod()
{
  char	*p = XmTextFieldGetString(averageText);

  avRate = atoi(p);
  XtFree(p);

  if (avRate <= 0)
    {
    avRate = 1;
    XmTextFieldSetString(averageText, "1");
    }

  setMgr.SetAverageRate(avRate);

}	/* END UPDATEAVERAGEPERIOD */

/* -------------------------------------------------------------------- */
void MovieControl::SetAveragePeriod(int newRate)
{
  char	tmp[10];

  avRate = newRate;

  if (avRate <= 0)
    avRate = 1;

  sprintf(tmp, "%d", avRate);
  XmTextFieldSetString(averageText, tmp);
  setMgr.SetAverageRate(avRate);

}	/* END SETAVERAGEPERIOD */

/* -------------------------------------------------------------------- */
void MovieControl::UpdateTime()
{
  char	*p;
  int	value;

  p = XmTextFieldGetString(timeText);
  currTime = p;
  XtFree(p);

  if (currTime < startTime)
    currTime == startTime;

  if (currTime > endTime)
    currTime == endTime;

  XmTextFieldSetString(timeText, currTime.c_str());

  if (numberSeconds == 0)
    value = 0;
  else
    value = (currTime-startTime) * 100 / numberSeconds;

  if (value < 0)
    value = 0;

  XmScaleSetValue(timeScale, 0);

  setMgr.SetStartTime(currTime);

}	/* END UPDATETIME */

/* -------------------------------------------------------------------- */
void MovieControl::PositionTime()
{
  int	dist;

  XmScaleGetValue(timeScale, &dist);

  currTime = startTime + numberSeconds * dist / 100;
  XmTextFieldSetString(timeText, currTime.c_str());
  setMgr.SetStartTime(currTime);

}	/* END POSITIONTIME */

/* -------------------------------------------------------------------- */
void MovieControl::SetRowsCols(int rows, int cols)
{
  nRows = rows;
  nCols = cols;

  setMgr.SetNumberRecords(rows * cols);
  plotMgr->SetRowsCols(rows, cols);

}	/* END SETDELAY */

/* -------------------------------------------------------------------- */
void MovieControl::SetDelay()
{
  XmScaleGetValue(delayScale, &delay);
  delay *= 1000;

}	/* END SETDELAY */

/* -------------------------------------------------------------------- */
void MovieControl::SetDefaultStartEndTime()
{
  startTime = currTime = fileMgr.CurrentFile()->StartTime();
  endTime = fileMgr.CurrentFile()->EndTime();

  XmTextFieldSetString(timeText, startTime.c_str());
 
  numberSeconds = endTime - startTime;

  setMgr.SetStartTime(startTime);

}	/* END SETDEFAULTSTARTENDTIME */

/* -------------------------------------------------------------------- */
void MovieControl::StepForward()
{
  currTime += (avRate * nRows * nCols) / setMgr.FirstSet()->probe->DataRate();

  if (currTime + avRate > endTime.Seconds())
    {
    currTime = endTime;
    movieRunning = False;
    }
  else
    setMgr.PageForward();

  XmTextFieldSetString(timeText, currTime.c_str());
  XmScaleSetValue(timeScale, (currTime-startTime) * 100 / numberSeconds);

}	/* END STEPFORWARD */

/* -------------------------------------------------------------------- */
void MovieControl::StepBackward()
{
  currTime -= (avRate * nRows * nCols) / setMgr.FirstSet()->probe->DataRate();

  if (currTime <= startTime)
    {
    currTime = startTime;
    movieRunning = False;
    }
  else
    setMgr.PageBackward();

  XmTextFieldSetString(timeText, currTime.c_str());
  XmScaleSetValue(timeScale, (currTime-startTime) * 100 / numberSeconds);

}	/* END STEPBACKWARD */

/* -------------------------------------------------------------------- */
void MovieControl::createXwindow(Widget parent)
{
  Arg           args[4];
  Cardinal      n;
  Widget        frame[4], RC[4], title[4], plRC[4], label;
 
  n = 0;
  frame[0] = XmCreateFrame(Window(), "timeFrame", args, n);
  frame[1] = XmCreateFrame(Window(), "controlFrame", args, n);
  XtManageChildren(frame, 2);
 
  n = 0;
  title[0] = XmCreateLabel(frame[0], "Time/Average Period", args, n);
  title[1] = XmCreateLabel(frame[1], "Control", args, n);
  XtManageChild(title[0]); XtManageChild(title[1]);
 
  n = 0;
  RC[0] = XmCreateRowColumn(frame[0], "timeRC", args, n);
  RC[1] = XmCreateRowColumn(frame[1], "controlRC", args, n);
  XtManageChild(RC[0]); XtManageChild(RC[1]);
 

  /* Start & End Time widgets.
   */
  n = 0;
  plRC[0] = XmCreateRowColumn(RC[0], "pnRC", args, n);
  plRC[1] = XmCreateRowColumn(RC[0], "pnRC", args, n);
  XtManageChildren(plRC, 2);
 
  n = 0;
  label = XmCreateLabel(plRC[0], "Start time", args, n);
  XtManageChild(label);
 
  n = 0;
  timeText = XmCreateTextField(plRC[0], "timeText", args, n);
  XtManageChild(timeText);
  XtAddCallback(timeText, XmNlosingFocusCallback, ValidateTime, NULL);
  XtAddCallback(timeText, XmNlosingFocusCallback, ApplyTimeChange, NULL);
 
 

  n = 0;
  label = XmCreateLabel(plRC[1], "Averaging period :", args, n);
  XtManageChild(label);
 
  n = 0;
  averageText = XmCreateTextField(plRC[1], "averageText", args, n);
  XtAddCallback(averageText, XmNlosingFocusCallback, ValidateInteger, NULL);
  XtAddCallback(averageText, XmNlosingFocusCallback, ApplyAveragePeriod, NULL);
  XtManageChild(averageText);
 
  n = 0;
  label = XmCreateLabel(plRC[1], "seconds", args, n);
  XtManageChild(label);
 
 
 
  /* Start, Stop, Reset, Step buttons.
   */
  n = 0;
  plRC[0] = XmCreateRowColumn(RC[1], "pgButtRC", args, n);
  XtManageChild(plRC[0]);
 
  n = 0;
  butt[0] = XmCreatePushButton(plRC[0], "Start", args, n);
  butt[1] = XmCreatePushButton(plRC[0], "Stop", args, n);
  butt[2] = XmCreatePushButton(plRC[0], "Step Bkd", args, n);
  butt[3] = XmCreatePushButton(plRC[0], "Step Fwd", args, n);
  XtManageChildren(butt, 4);
  XtAddCallback(butt[0], XmNactivateCallback, StartMovie, NULL);
  XtAddCallback(butt[1], XmNactivateCallback, StopMovie, NULL);
  XtAddCallback(butt[2], XmNactivateCallback, PageBackward, NULL);
  XtAddCallback(butt[3], XmNactivateCallback, PageForward, NULL);


  n = 0;
  timeScale = XmCreateScale(RC[0], "timeScale", args, n);
  XtManageChild(timeScale);
  XtAddCallback(timeScale, XmNvalueChangedCallback, SetScaleTime, NULL);
 
  n = 0;
  delayScale = XmCreateScale(RC[1], "delayScale", args, n);
  XtManageChild(delayScale);
  XtAddCallback(delayScale, XmNdragCallback, SetScaleSpeed, NULL);
  XtAddCallback(delayScale, XmNvalueChangedCallback, SetScaleSpeed, NULL);

}	/* END CREATEXWINDOW */

/* -------------------------------------------------------------------- */
void MovieControl::Start()
{
  if (setMgr.NumberOfSets() == 0)
    return;

  movieRunning = True;

  XtSetSensitive(butt[0], False);
  XtSetSensitive(butt[1], True);
  XtSetSensitive(butt[2], False);
  XtSetSensitive(butt[3], False);

  setMgr.ReadAllSets();

  do
    {
    plotMgr->DrawImage();
    application->FlushEvents();

    if (delay)
      usleep(delay);

    StepForward();
    }
  while (movieRunning);

  plotMgr->DrawImage();

}	/* END START */

/* -------------------------------------------------------------------- */
void MovieControl::Stop()
{
  movieRunning = False;

  XtSetSensitive(butt[0], True);
  XtSetSensitive(butt[1], False);
  XtSetSensitive(butt[2], True);
  XtSetSensitive(butt[3], True);

}	/* END STOP */

/* END MOVIECONTROL.CC */

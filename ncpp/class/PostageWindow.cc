/*
-------------------------------------------------------------------------
OBJECT NAME:	PostageWindow.cc

FULL NAME:	Postage Window

ENTRY POINTS:	PostageWindow()
		PopUp()
		AveragePeriod()
		SetCurrentTime()
		IncrementCurrentTime()

STATIC FNS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "PostageWindow.h"
#include "FileMgr.h"
#include "SetMgr.h"

extern FileManager	fileMgr;
extern SetManager	setMgr;


/* -------------------------------------------------------------------- */
PostageWindow::PostageWindow(Widget parent) : WinForm(parent, "postage", RowColumn)
{
  createXwindow(parent);

  XtSetSensitive(butt[1], False);
  XmScaleSetValue(speedScale, 100);
  XmTextFieldSetString(averageText, "10");

  if (fileMgr.CurrentFile())
    {
    start = fileMgr.CurrentFile()->Start;
    XmTextFieldSetString(timeText[0], start.Label());

    end = fileMgr.CurrentFile()->End;
    XmTextFieldSetString(timeText[1], end.Label());

    numberSeconds = end - start;
    }
  else
    numberSeconds = 0;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void PostageWindow::PopUp()
{
  SetCurrentTime();

}	/* END POPUP */

/* -------------------------------------------------------------------- */
int PostageWindow::AveragePeriod()
{
  int	ap;
  char	*p = XmTextFieldGetString(averageText);

  ap = atoi(p);
  XtFree(p);

  return(ap);

}	/* END AVERAGEPERIOD */

/* -------------------------------------------------------------------- */
void PostageWindow::SetCurrentTime()
{
  int	dist;
  int	h, m, s;
  char	*p;

  XmScaleGetValue(timeScale, &dist);

  p = XmTextFieldGetString(timeText[0]);
  start = p;
  XtFree(p);

  p = XmTextFieldGetString(timeText[0]);
  end = p;
  XtFree(p);

  if (end < start)
    end += 86400;

  numberSeconds = end - start;
  currSecond = start.Seconds() + numberSeconds * (dist / 100);

}	/* END SETCURRENTTIME */

/* -------------------------------------------------------------------- */
int PostageWindow::IncrementCurrentTime()
{
  int	dist;

  ++currSecond;

  XmScaleSetValue(timeScale,
                  (currSecond - start.Seconds()) / numberSeconds * 100);

  // Return whether we have reached end of time period.
  if (currSecond >= end.Seconds())
    return(False);
  else
    return(True);

}	/* END INCREMENTCURRENTTIME */

/* -------------------------------------------------------------------- */
void PostageWindow::createXwindow(Widget parent)
{
  int           i;
  Arg           args[4];
  Cardinal      n;
  Widget        frame[4], RC[4], title[4], plRC[4], label;
 
  n = 0;
  frame[0] = XmCreateFrame(Window(), "timeFrame", args, 0);
  frame[1] = XmCreateFrame(Window(), "controlFrame", args, 0);
  frame[2] = XmCreateFrame(Window(), "parmsFrame", args, 0);
  XtManageChildren(frame, 3);
 
  n = 0;
  title[0] = XmCreateLabel(frame[0], "timeTitle", args, 0);
  title[1] = XmCreateLabel(frame[1], "controlTitle", args, 0);
  title[2] = XmCreateLabel(frame[2], "parmsTitle", args, 0);
  XtManageChild(title[0]); XtManageChild(title[1]);
  XtManageChild(title[2]);
 
  n = 0;
  RC[0] = XmCreateRowColumn(frame[0], "timeRC", args, 0);
  RC[1] = XmCreateRowColumn(frame[1], "controlRC", args, 0);
  RC[2] = XmCreateRowColumn(frame[2], "parmsRC", args, n);
  XtManageChild(RC[0]); XtManageChild(RC[1]);
  XtManageChild(RC[2]);
 
 
 
/* Start & End Time widgets.
 */
  n = 0;
  plRC[0] = XmCreateRowColumn(RC[0], "plRC", args, n);
  plRC[1] = XmCreateRowColumn(RC[0], "plRC", args, n);
  XtManageChildren(plRC, 2);
 
  n = 0;
  label = XmCreateLabel(plRC[0], "Start time", args, n);
  XtManageChild(label);
 
  n = 0;
  timeText[0] = XmCreateTextField(plRC[0], "timeText", args, n);
  XtManageChild(timeText[0]);
  XtAddCallback(timeText[0], XmNlosingFocusCallback, ValidateTime, NULL);
  XtAddCallback(timeText[0], XmNlosingFocusCallback, ApplyPostageTime, NULL);
 
  n = 0;
  label = XmCreateLabel(plRC[0], " End time", args, n);
  XtManageChild(label);
 
  n = 0;
  timeText[1] = XmCreateTextField(plRC[0], "timeText", args, n);
  XtManageChild(timeText[1]);
  XtAddCallback(timeText[1], XmNlosingFocusCallback, ValidateTime, NULL);
  XtAddCallback(timeText[1], XmNlosingFocusCallback, ApplyPostageTime, NULL);

 
  n = 0;
  label = XmCreateLabel(plRC[1], "Averaging period :", args, n);
  XtManageChild(label);
 
  n = 0;
  averageText = XmCreateTextField(plRC[1], "averageText", args, n);
  XtAddCallback(averageText, XmNlosingFocusCallback, ValidateInteger, NULL);
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
  XtAddCallback(butt[0], XmNactivateCallback, StartPostage, NULL);
  XtAddCallback(butt[1], XmNactivateCallback, StopMovie, NULL);
  XtAddCallback(butt[2], XmNactivateCallback, StepBkd, NULL);
  XtAddCallback(butt[3], XmNactivateCallback, StepFwd, NULL);
 
  n = 0;
  timeScale = XmCreateScale(RC[0], "timeScale", args, n);
  XtManageChild(timeScale);
  XtAddCallback(timeScale, XmNvalueChangedCallback, SetScaleTime, NULL);
 
  n = 0;
  speedScale = XmCreateScale(RC[1], "speedScale", args, n);
  XtManageChild(speedScale);
  XtAddCallback(speedScale, XmNdragCallback, SetScaleSpeed, NULL);

}	/* END CREATEXWINDOW */

/* -------------------------------------------------------------------- */
void PostageWindow::Start()
{
  int		i, avRate;
  DataSet	*set;

  avRate = AveragePeriod();

/*
  for (currRec = firstRecord; currRec < lastRecord; ++currRec)
    {
    for (set = setMgr.FirstSet(); set; set = setMgr.NextSet())
      {
      set->file->ReadConcentrations(currRec, avRate, set);
      }




    mainPlot->drawPostage();
    }

  mainPlot->exposeAll();
*/

}	/* END START */

/* END POSTAGEWINDOW.CC */

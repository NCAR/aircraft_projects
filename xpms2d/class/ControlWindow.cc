/*
-------------------------------------------------------------------------
OBJECT NAME:	ControlWindow.cc

FULL NAME:	Callbacks for Control Window

ENTRY POINTS:	ControlWindow()
		PoopUp()
		SetFileNames()
		SetTimeText()
		SetDensity()
		SetDelay()
		Start()
		Stop()
		PositionTime()
		UpdateTimeScale()

STATIC FNS:	

DESCRIPTION:	

MODIFIES:	CurrentDataFile, CurrentPanelNumber, NumberOfPanels

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#include <unistd.h>

#include "ControlWindow.h"
#include "FileMgr.h"

extern Application      *application;
extern FileManager	fileMgr;

#ifdef SVR4
extern "C" { int usleep(unsigned int); }
#endif

/* -------------------------------------------------------------------- */
ControlWindow::ControlWindow(Widget parent) : WinForm(parent, "control", RowColumn)
{
  Widget	pnRC[2], plRC[8], label, trc;
  Widget	title[8], bkd, fwd, frame[6], RC[6];
  Arg		args[8];
  int		i, n;

  delay = 0;
  densIdx = 0;
  concIdx = 0;

  /* Did anyone every mention that C++'s ability to have pre-initialized
   * stuff in a class sucks the big one.
   */
  density[0].label = "Water (1.0)";
  density[1].label = "Ice (0.916)";
  density[2].label = "Graupel (0.5)";
  density[3].label = "Snow (0.12)";
  density[0].density = 1.0;
  density[1].density = 0.916;
  density[2].density = 0.5;
  density[3].density = 0.12;

  n = 0;
  frame[0] = XmCreateFrame(Window(), "timeFrame", args, 0);
  frame[1] = XmCreateFrame(Window(), "probeFrame", args, 0);
trc = XmCreateRowColumn(Window(), "trc", args, 0);
  frame[2] = XmCreateFrame(trc, "cncFrame", args, 0);
  frame[3] = XmCreateFrame(trc, "denFrame", args, 0);
  XtManageChild(trc);
  XtManageChild(frame[0]); XtManageChild(frame[1]);
  XtManageChild(frame[2]); XtManageChild(frame[3]);

  n = 0;
  title[0] = XmCreateLabel(frame[0], "timeTitle", args, 0);
  title[1] = XmCreateLabel(frame[1], "probeTitle", args, 0);
  title[2] = XmCreateLabel(frame[2], "cncTitle", args, 0);
  title[3] = XmCreateLabel(frame[3], "denTitle", args, 0);
  XtManageChild(title[0]); XtManageChild(title[1]);
  XtManageChild(title[2]); XtManageChild(title[3]);

  n = 0;
  RC[0] = XmCreateRowColumn(frame[0], "movieRC", args, n);
  RC[1] = XmCreateRowColumn(frame[1], "probeRC", args, 0);
  RC[2] = XmCreateRadioBox(frame[2], "cncRC", args, 0);
  RC[3] = XmCreateRadioBox(frame[3], "denRC", args, 0);
  XtManageChild(RC[0]); XtManageChild(RC[1]);
  XtManageChild(RC[2]); XtManageChild(RC[3]);


  n = 0;
  frame[0] = XmCreateFrame(RC[0], "timeFrame", args, n);
  frame[1] = XmCreateFrame(RC[0], "ctlFrame", args, n);
  XtManageChildren(frame, 2);

  n = 0;
  pnRC[0] = XmCreateRowColumn(frame[0], "timeRC", args, n);
  pnRC[1] = XmCreateRowColumn(frame[1], "ctlRC", args, n);
  XtManageChild(pnRC[0]); XtManageChild(pnRC[1]);


  /* Start & End Time widgets.
   */
  n = 0;
  plRC[0] = XmCreateRowColumn(pnRC[0], "pnRC", args, n);
  plRC[1] = XmCreateRowColumn(pnRC[0], "pnRC", args, n);
  XtManageChildren(plRC, 2);

  n = 0;
  label = XmCreateLabel(plRC[0], "Start time", args, n);
  XtManageChild(label);

  n = 0;
  timeText = XmCreateTextField(plRC[0], "timeText", args, n);
  XtManageChild(timeText);
  XtAddCallback(timeText, XmNlosingFocusCallback, ValidateTime, NULL);
  XtAddCallback(timeText, XmNlosingFocusCallback, ApplyTimeChange, NULL);


  /* Start, Stop, Reset, Step buttons.
   */
  n = 0;
  plRC[0] = XmCreateRowColumn(pnRC[1], "pgButtRC", args, n);
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
  timeScale = XmCreateScale(pnRC[0], "timeScale", args, n);
  XtManageChild(timeScale);
  XtAddCallback(timeScale, XmNvalueChangedCallback, SetScaleTime, NULL);

  n = 0;
  delayScale = XmCreateScale(pnRC[1], "delayScale", args, n);
  XtManageChild(delayScale);
  XtAddCallback(delayScale, XmNdragCallback, SetScaleSpeed, NULL);
  XtAddCallback(delayScale, XmNvalueChangedCallback, SetScaleSpeed, NULL);



  /* Probe Toggle Buttons.
   */
  for (i = 0; i < MAX_PROBES; ++i)
    {
    n = 0;
    probeB[i] = XmCreateToggleButton(RC[1], "none     ", NULL, 0);
    XtAddCallback(probeB[i], XmNvalueChangedCallback,
                  (XtCallbackProc)SetProbe, (XtPointer)i);
    }

  XtManageChildren(probeB, MAX_PROBES);


  /* Concentration calculation
   */
  for (i = 0; i < 4; ++i)
    {
    n = 0;
    sprintf(buffer, "conc%d", i);
    cncB[i] = XmCreateToggleButton(RC[2], buffer, NULL, 0);
    XtAddCallback(cncB[i], XmNvalueChangedCallback,
                  (XtCallbackProc)SetConcentration, (XtPointer)i);
    }

  XtManageChildren(cncB, i);
  XmToggleButtonSetState(cncB[concIdx], True, False);

  /* Water density
   */
  for (i = 0; i < 4; ++i)
    {
    n = 0;
    densB[i] = XmCreateToggleButton(RC[3], density[i].label, NULL, 0);
    XtAddCallback(densB[i], XmNvalueChangedCallback,
                  (XtCallbackProc)SetDensity, (XtPointer)i);
    }

  XtManageChildren(densB, i);
  XmToggleButtonSetState(densB[densIdx], True, False);

}	/* END CONTROLWINDOW */

/* -------------------------------------------------------------------- */
void ControlWindow::PopUp()
{
  XtManageChild(Window());
  XtPopup(XtParent(Window()), XtGrabNone);

//  SetFileNames();
  SetProbes();

}	/* END OPEN */

/* -------------------------------------------------------------------- */
void ControlWindow::SetFileNames()
{
  int		i;
  XmString	label;
  Arg		args[2];

printf("In SetFileNames()\n");
return;

/*
  for (i = 0; i < fileMgr.NumberOfFiles(); ++i)
    {
    XtSetSensitive(fileB[i], True);
 
    label = XmStringCreate(fileMgr.dataFile[i]->FileName(), XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(fileB[i], args, 1);
    XmStringFree(label);
 
    if (i == CurrentDataFile)
      XmToggleButtonSetState(fileB[i], True, True);
    }
 
  for (; i < MAX_DATAFILES; ++i)
    {
    XtSetSensitive(fileB[i], False);
 
    label = XmStringCreate("none", XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(fileB[i], args, 1);
    XmStringFree(label);
    }
*/
}	/* END SETFILENAMES */

/* -------------------------------------------------------------------- */
void ControlWindow::SetProbes()
{
  int		i = 0;
  XmString	label;
  Arg		args[2];
printf("In SetProbes()\n");
  if (fileMgr.CurrentFile())
    for (i = 0; i < fileMgr.CurrentFile()->NumberOfProbes(); ++i)
      {
      XtSetSensitive(probeB[i], True);

      label = XmStringCreate(fileMgr.CurrentFile()->probe[i]->Name,
                             XmFONTLIST_DEFAULT_TAG);
      XtSetArg(args[0], XmNlabelString, label);
      XtSetValues(probeB[i], args, 1);
      XmStringFree(label);

      XmToggleButtonSetState(probeB[i], False, False);
      }
 
  for (; i < MAX_PROBES; ++i)
    {
    XtSetSensitive(probeB[i], False);
 
    label = XmStringCreate("none", XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(probeB[i], args, 1);
    XmStringFree(label);

    XmToggleButtonSetState(probeB[i], False, False);
    }

}	/* END SETPROBES */

/* -------------------------------------------------------------------- */
void ControlWindow::UpdateStartTime(P2d_rec *buff)
{
  char	tmpSpace[16];

  sprintf(tmpSpace, "%02d:%02d:%02d", buff->hour, buff->minute, buff->second);
  XmTextFieldSetString(timeText, tmpSpace);

}	/* END UPDATESTARTTIME */

/* -------------------------------------------------------------------- */
void ControlWindow::SetUserDensity()
{
  char	*p, tmp[16];

  p = XmTextFieldGetString(densTxt);
  density[3].density = atof(p);
  sprintf(tmp, "%4.2f", density[3].density);
  XmTextFieldSetString(densTxt, tmp);

}

/* -------------------------------------------------------------------- */
void ControlWindow::Start()
{
  if (fileMgr.CurrentFile() == 0)
    return;

  movieRunning = True;

  XtSetSensitive(butt[0], False);
  XtSetSensitive(butt[1], True);
  XtSetSensitive(butt[2], False);
  XtSetSensitive(butt[3], False);

  do
    {
    PageForward(NULL, NULL, NULL);
    application->FlushEvents();

    if (delay)
      usleep(delay);
    }
  while (movieRunning);

}       /* END START */

/* -------------------------------------------------------------------- */
void ControlWindow::Stop()
{
  movieRunning = False;

  XtSetSensitive(butt[0], True);
  XtSetSensitive(butt[1], False);
  XtSetSensitive(butt[2], True);
  XtSetSensitive(butt[3], True);

}

/* -------------------------------------------------------------------- */
void ControlWindow::UpdateTimeScale()
{
  int	timePos = 0;

  timePos = fileMgr.CurrentFile()->GetPosition();
  XmScaleSetValue(timeScale, timePos);

}

/* -------------------------------------------------------------------- */
void ControlWindow::PositionTime(bool reset)
{
  int	timePos = 0;

  if (!reset)
    XmScaleGetValue(timeScale, &timePos);

  fileMgr.CurrentFile()->SetPosition(timePos);

}

/* -------------------------------------------------------------------- */
void ControlWindow::SetDelay()
{
  XmScaleGetValue(delayScale, &delay);
  delay *= 1000;

}       /* END SETDELAY */

/* END CONTROLWINDOW.CC */

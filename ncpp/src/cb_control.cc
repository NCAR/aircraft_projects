/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_control.cc

FULL NAME:	Callback Wrappers for PlotType & DataSource classes

ENTRY POINTS:	SetPlotType()
		SetFileNames()
		SetProbeNames()
		SetCurrentFile()
		ModifyActiveProbes()
		ModifyActiveDataTypes()
		ApplyTimeChange()
		ApplyAveragePeriod()
		PageForward()
		PageBackward()
		Set_nPanels()
		SetNormalization()
		ToggleDITC_CB()
		ToggleGrid_CB()
		ToggleColor_CB()
		ToggleCompute()

STATIC FNS:	none

DESCRIPTION:	Callbacks for PlotType, File, Probe, and Data buttons.
		Basically things that are in common between movieGUI and
		postageGUI.

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"
#include <unistd.h>

#include "Canvas.h"
#include "Cursor.h"
#include "FileMgr.h"
#include "MovieControl.h"
#include "PlotMgr.h"
#include "Printer.h"
#include "SetMgr.h"


extern Canvas		*mainCanvas;
extern FileManager	fileMgr;
extern MovieControl	*movieControlGUI;
extern PlotManager	*plotMgr;
extern Printer		*printerSetup;
extern SetManager	setMgr;
extern XCursor		cursor;


/* -------------------------------------------------------------------- */
void SetPlotTypeCB(Widget w, PlotType client, XtPointer call)
{
  plotMgr->SetPlotType((PlotType)client);
  plotMgr->Resize();
  plotMgr->DrawImage();

}	/* END SETPLOTTYPE */

/* -------------------------------------------------------------------- */
void SetFileNames()
{
  plotMgr->SetFileNames();
  SetDiams(NULL, NULL, 0);

}	/* END SETFILENAMES */

/* -------------------------------------------------------------------- */
void SetProbeNames()
{
  plotMgr->SetProbeNames();

}	/* END SETPROBENAMES */

/* -------------------------------------------------------------------- */
void SetStartEndTime()
{
  movieControlGUI->SetDefaultStartEndTime();

}	/* END SETSTARTENDTIME */

/* -------------------------------------------------------------------- */
void SetCurrentFile(Widget w, XtPointer client, XtPointer call)
{
  XmToggleButtonCallbackStruct *cb = (XmToggleButtonCallbackStruct *)call;

  if (!cb->set)
    return;

  fileMgr.SetCurrentFile((int)client);
  SetProbeNames();
  plotMgr->GenerateAutoTitles(*fileMgr.CurrentFile());

  SetDiams(NULL, 0, NULL);

}	/* END SETCURRENTFILE */

/* -------------------------------------------------------------------- */
void ModifyActiveProbes(Widget w, XtPointer client, XtPointer call)
{
  XmToggleButtonCallbackStruct *cb = (XmToggleButtonCallbackStruct *)call;

  cursor.WaitCursor(movieControlGUI->Window());

  // Update the SetMgrs' (Add/Delete).

  if (cb->set)
    {
    if (setMgr.Add(fileMgr.CurrentFile(),
		fileMgr.CurrentFile()->probe[(int)client]) == false)
      XmToggleButtonSetState(w, false, false);
    }
  else
    setMgr.Delete(fileMgr.CurrentFile(),
		fileMgr.CurrentFile()->probe[(int)client]);


  // If High-rate, then force averaging period to one, and shut it down.
  if (setMgr.NumberOfSets() == 0)
    movieControlGUI->TurnOnAverage();
  else
    {
    if (setMgr.FirstSet()->probe->DataRate() > 1)
      {
      movieControlGUI->SetAveragePeriod(1);
      movieControlGUI->TurnOffAverage();
      }
    }

  plotMgr->DrawImage();

  cursor.PointerCursor(movieControlGUI->Window());

}	/* END MODIFYACTIVEPROBES */

/* -------------------------------------------------------------------- */
void ModifyActiveDataTypes(Widget w, XtPointer client, XtPointer call)
{
  DataType dt = plotMgr->ActiveDataTypes();

  if (w)	// Resize to portrait or landscape, based on # types.
    {
    int	cnt, i;

    for (i = 0, cnt = 0; i < 16; ++i)
      if ((dt >> i) & 1)
        ++cnt;

    if (cnt == 1)
      {
      mainCanvas->SetSize(650, 840);
      printerSetup->SetShape(Printer::LANDSCAPE);
      }
    else
      {
      mainCanvas->SetSize(840, 650);
      printerSetup->SetShape(Printer::PORTRAIT);
      }
    }

  plotMgr->SetDataTypes(dt);
  setMgr.SetDataTypes(dt);

  plotMgr->DrawImage();

}	/* END MODIFYACTIVEDATATYPES */

/* -------------------------------------------------------------------- */
void ApplyTimeChange(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->UpdateTime();

  plotMgr->DrawImage();

}       /* END APPLYTIMECHANGE */

/* -------------------------------------------------------------------- */
void ApplyAveragePeriod(Widget w, XtPointer client, XtPointer call)
{
  // Local SetAveragePeriod() must update SetMgr.

  movieControlGUI->UpdateAveragePeriod();
 
  plotMgr->DrawImage();

}       /* END APPLYAVERAGEPERIOD */
 
/* -------------------------------------------------------------------- */
void PageForward(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->StepForward();
 
  plotMgr->DrawImage();

}       /* END STEPFWD */
 
/* -------------------------------------------------------------------- */
void PageBackward(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->StepBackward();
 
  plotMgr->DrawImage();

}       /* END STEPBKD */

/* -------------------------------------------------------------------- */
void Set_nPanels(Widget w, XtPointer client, XtPointer call)
{
  int rows, cols;

  sscanf((char *)client, "%dx%d", &rows, &cols);

  movieControlGUI->SetRowsCols(rows, cols);
  plotMgr->DrawImage();

}	/* SET_NPANELS */

/* -------------------------------------------------------------------- */
void SetNormalization(Widget w, XtPointer client, XtPointer call)
{
  char *p = (char *)client;
  NormType	n = NONE;

  if (strcmp(p, "Linear") == 0)
    n = LINEAR;

  if (strcmp(p, "Log") == 0)
    n = LOG;

  setMgr.SetNormalize(n);
  plotMgr->SetNormalize(n);
  plotMgr->DrawImage();

}	/* SETNORMALIZATION */

/* -------------------------------------------------------------------- */
void ToggleDITC_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleDITC();
  plotMgr->DrawImage();

}	/* END TOGGLEDITC_CB */

/* -------------------------------------------------------------------- */
void ToggleGrid_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleGrid();
  plotMgr->DrawImage();

}	/* END TOGGLEGRID_CB */

/* -------------------------------------------------------------------- */
void ToggleColor_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleColor();
  plotMgr->DrawImage();

}	/* END TOGGLECOLOR_CB */

/* -------------------------------------------------------------------- */
void ToggleCompute(Widget w, XtPointer client, XtPointer call)
{
  setMgr.SetCompute((bool)client);
  plotMgr->DrawImage();

}	/* END TOGGLECOMPUTE */

/* END CB_CONTROL.CC */

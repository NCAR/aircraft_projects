/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_edit.cc

FULL NAME:	Callbacks to EditWindow(s)

ENTRY POINTS:	EditParms()
		EditDiameters()
		ApplyParmsWindow()
		SetParmsWindow()
		SetDiams()
		AutoTitle_CB()
		AutoLabel_CB()
		AutoScale_CB()
		AutoTic_CB()

STATIC FNS:	none

DESCRIPTION:	

REFERENCES:	none

REFERENCED BY:	Menu buttons, and buttons on edit windows.

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#include "Application.h"
#include "EditDiameters.h"
#include "FileMgr.h"
#include "PlotMgr.h"
#include "SetMgr.h"

static EditDiameters	*editDiams = NULL;

extern Application	*application;
extern FileManager	fileMgr;
extern PlotManager	*plotMgr;
extern SetManager	setMgr;


/* -------------------------------------------------------------------- */
void EditDiams(Widget w, XtPointer client, XtPointer call)
{
  if (!editDiams)
    editDiams = new EditDiameters(application->Shell());

  editDiams->SetProbeNames(fileMgr.CurrentFile());
  editDiams->PopUp();

}	/* END EDITDIAMETERS */

/* -------------------------------------------------------------------- */
void EditParms(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->EditParms(application->Shell(), (int)client);

}	/* END EDITPARMS */

/* -------------------------------------------------------------------- */
void AutoTitle_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleAutoTitle((int)client);

}

/* -------------------------------------------------------------------- */
void AutoLabel_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleAutoLabel((int)client);

}

/* -------------------------------------------------------------------- */
void AutoScale_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleAutoScale((int)client);

}

/* -------------------------------------------------------------------- */
void AutoTic_CB(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ToggleAutoTics((int)client);

}

/* -------------------------------------------------------------------- */
void ApplyParmsWindow(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->ApplyParms((int)client, *fileMgr.CurrentFile());

}	/* END APPLYPARMSWINDOW */

/* -------------------------------------------------------------------- */
void SetParmsWindow(Widget w, XtPointer client, XtPointer call)
{
  plotMgr->SetParms((int)client);

}	/* END SETPARMSWINDOW */

/* -------------------------------------------------------------------- */
static int currentProbe = 0;

void ApplyDiams(Widget w, XtPointer client, XtPointer call)
{
  editDiams->ApplyDiameters(fileMgr.CurrentFile()->probe[currentProbe]);
  setMgr.ReadAllSets();
  plotMgr->DrawImage();

}	/* END APPLYPARMSWINDOW */

/* -------------------------------------------------------------------- */
void SetDiams(Widget w, XtPointer client, XtPointer call)
{
  if (call && ((XmToggleButtonCallbackStruct *)call)->set == 0)
    return;

  if (editDiams && fileMgr.CurrentFile())
    {
    currentProbe = (int)client;
    editDiams->SetDiameters(fileMgr.CurrentFile()->probe[currentProbe]);
    }

}	/* END SETDIAMS */

/* END CB_EDIT.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_control.cc

FULL NAME:	Callback Wrappers (C++ is so cheezy sometimes).

ENTRY POINTS:	ApplyTimeChange()
		ModifyActiveVars()
		PageForward()
		PageCurrent()
		PageBackward()
		SetCurrentFile()
		SetProbe()
		SetDensity()
		SetConcentration()
		SetScaleTime()
		SetScaleSpeed()
		StartMovie()
		StopMovie()

STATIC FNS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1994-2001
-------------------------------------------------------------------------
*/

#include "define.h"
#include <unistd.h>

#include "ControlWindow.h"
#include "Colors.h"
#include "Cursor.h"
#include "Enchilada.h"
#include "FileMgr.h"
#include "XPen.h"
#include "MainCanvas.h"

extern Enchilada	*enchiladaWin;
extern FileManager	fileMgr;
extern ControlWindow	*controlWindow;
extern MainCanvas	*mainPlot;
extern XCursor		cursor;
extern Colors		*color;
extern XPen		*pen;

struct recStats &ProcessRecord(P2d_rec *, float);

/* Contains current N 2d records (for re-use by things like ViewHex */
int	nBuffs = 0;
P2d_rec	pgFbuff[20];


/* -------------------------------------------------------------------- */
void ApplyTimeChange(Widget w, XtPointer client, XtPointer call)
{
  int		j, h, m, s;
  char		*p;
  float		version;

  if (fileMgr.CurrentFile() == NULL ||
      fileMgr.CurrentFile()->NumberOfProbes() == 0)
    return;


  cursor.WaitCursor(mainPlot->Wdgt());
  version = atof(fileMgr.CurrentFile()->HeaderVersion());
  p = XmTextFieldGetString(controlWindow->StartTime());

  if (strlen(p) == 0) {
    cursor.PointerCursor(mainPlot->Wdgt());
    XtFree(p);
    return;
    }

  sscanf(p, "%d:%d:%d", &h, &m, &s);

  if (!fileMgr.CurrentFile()->LocatePMS2dRecord(&pgFbuff[0], h, m, s))
    {
    fprintf(stderr, "No 2d records after %s.\n", p);
    cursor.PointerCursor(mainPlot->Wdgt());
    XtFree(p);
    return;
    }

  XtFree(p);

  PageForward(NULL, NULL, NULL);

}	/* END APPLYTIMECHANGE */

/* -------------------------------------------------------------------- */
void PageForward(Widget w, XtPointer client, XtPointer call)
{
  int		j;
  char		*buff_p;
  bool		probes = false;
  float		version;
  struct recStats p7;

  if (fileMgr.NumberOfFiles() == 0)
    return;

  for (j = 0; j < fileMgr.CurrentFile()->NumberOfProbes(); ++j)
    if (fileMgr.CurrentFile()->probe[j]->Display())
      probes = true;

  if (!probes)
    return;

  cursor.WaitCursor(mainPlot->Wdgt());

  mainPlot->Clear();
  mainPlot->reset(fileMgr.CurrentFile());
  version = atof(fileMgr.CurrentFile()->HeaderVersion());

  if (enchiladaWin)
    enchiladaWin->Clear();

  for (nBuffs = 0; nBuffs < mainPlot->maxRecords() &&
              fileMgr.CurrentFile()->NextPMS2dRecord(&pgFbuff[nBuffs]); )
    {
    buff_p = (char *)&pgFbuff[nBuffs];

    if (((buff_p[0] == 'H' && mainPlot->SpaceAvailable() < 294) ||
	 (buff_p[0] != 'H' && mainPlot->SpaceAvailable() < 70)) )
      break;

    if (nBuffs == 0)
      controlWindow->UpdateStartTime(&pgFbuff[nBuffs]);

    for (j = 0; j < fileMgr.CurrentFile()->NumberOfProbes(); ++j)
      {
      if (!strncmp(fileMgr.CurrentFile()->probe[j]->Code, buff_p, 2)
          && fileMgr.CurrentFile()->probe[j]->Display())
        {
        pen->SetColor(color->GetColor(j+1));
        mainPlot->draw(&pgFbuff[nBuffs],
		ProcessRecord(&pgFbuff[nBuffs], version), version, j+1, NULL);
        pen->SetColor(color->GetColor(0));
        ++nBuffs;
        break;
        }
      }
    }

  mainPlot->ExposeAll();
  cursor.PointerCursor(mainPlot->Wdgt());
  controlWindow->UpdateTimeScale();

}	/* END PAGEFORWARD */

/* -------------------------------------------------------------------- */
void PageCurrent()
{
  int		i, j;
  P2d_rec	pgBbuff;

  if (fileMgr.NumberOfFiles() == 0)
    return;

  cursor.WaitCursor(mainPlot->Wdgt());

  for (i = 0; i < mainPlot->maxRecords() &&
              fileMgr.CurrentFile()->PrevPMS2dRecord(&pgBbuff); )
    {
    for (j = 0; j < fileMgr.CurrentFile()->NumberOfProbes(); ++j)
      if (!strncmp(fileMgr.CurrentFile()->probe[j]->Code, (char *)&pgBbuff, 2)
          && fileMgr.CurrentFile()->probe[j]->Display())
        {
        ++i;
        }
    }

  ProcessRecord(&pgBbuff, -1);
  cursor.PointerCursor(mainPlot->Wdgt());
  PageForward(NULL, NULL, NULL);

}	/* END PAGECURRENT */

/* -------------------------------------------------------------------- */
void PageBackward(Widget w, XtPointer client, XtPointer call)
{
  int		i, j;
  P2d_rec	pgBbuff;

  if (fileMgr.NumberOfFiles() == 0)
    return;

  cursor.WaitCursor(mainPlot->Wdgt());

  for (i = 0; i < (mainPlot->maxRecords() << 1) &&
              fileMgr.CurrentFile()->PrevPMS2dRecord(&pgBbuff); )
    {
    for (j = 0; j < fileMgr.CurrentFile()->NumberOfProbes(); ++j)
      if (!strncmp(fileMgr.CurrentFile()->probe[j]->Code, (char *)&pgBbuff, 2)
          && fileMgr.CurrentFile()->probe[j]->Display())
        {
        ++i;
        }
    }

  ProcessRecord(&pgBbuff, -1);
  cursor.PointerCursor(mainPlot->Wdgt());
  PageForward(NULL, NULL, NULL);
  controlWindow->UpdateTimeScale();

}	/* END PAGEBACKWARD */

/* -------------------------------------------------------------------- */
void SetCurrentFile(Widget w, XtPointer client, XtPointer call)
{
  fileMgr.SetCurrentFile((int)client);

}

/* -------------------------------------------------------------------- */
void SetProbe(Widget w, XtPointer client, XtPointer call)
{
  fileMgr.CurrentFile()->probe[(int)client]->setDisplay(((XmToggleButtonCallbackStruct *)call)->set);
  PageCurrent();

}	/* END SETPROBE */

/* -------------------------------------------------------------------- */
void SetDensity(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->SetWaterDensity((int)client);
  PageCurrent();

}

/* -------------------------------------------------------------------- */
void SetConcentration(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->SetConcentrationCalc((int)client);
  SetSampleArea();
  PageCurrent();

}

/* -------------------------------------------------------------------- */
void StartMovie(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->Start();
  controlWindow->Stop();

}       /* END START */

/* -------------------------------------------------------------------- */
void StopMovie(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->Stop();

}

/* -------------------------------------------------------------------- */
void SetScaleTime(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->PositionTime(False);
  PageForward(NULL, NULL, NULL);

}       /* END SETSCALETIME */

/* -------------------------------------------------------------------- */
void SetScaleSpeed(Widget w, XtPointer client, XtPointer call)
{
  controlWindow->SetDelay();

}       /* END SETSCALESPEED */

/* END CB_CONTROL.CC */

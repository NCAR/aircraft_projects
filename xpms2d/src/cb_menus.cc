/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_menus.c

FULL NAME:	Callback Wrappers for menus off of main menu bar

ENTRY POINTS:	GetDataFileName()
		NewDataFile()
		AddDataFile()
		PrintSave()
		SavePNG()
		Quit()
		ToggleDisplay()
		ToggleSynthetic()

STATIC FNS:	PrintPS()
		Save()

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#include "define.h"
#include <errno.h>
#include <unistd.h>

#include "Application.h"
#include "ControlWindow.h"
#include "Colors.h"
#include "Cursor.h"
#include "FileMgr.h"
#include "MainCanvas.h"
#include "PostScript.h"
#include "Printer.h"
#include "XmFile.h"
#include "XmWarn.h"

static char	*PSoutFile = NULL, *pngOutFile = NULL;

extern Application	*application;
extern ControlWindow	*controlWindow;
extern Colors		*color;
extern XCursor		cursor;
extern FileManager	fileMgr;
extern MainCanvas	*mainPlot;
extern Printer		*printerSetup;
extern XmFile		*fileSel;

struct recStats &ProcessRecord(P2d_rec *, float);

/* Contains current N 2d records (for re-use by things like ViewHex */
extern int     nBuffs;
extern P2d_rec pgFbuff[];


/* -------------------------------------------------------------------- */
void GetDataFileName(Widget w, XtPointer client, XtPointer call)
{
  fileSel->QueryFile("Enter Data file to read:", DataPath, (XtCallbackProc)client);
}

/* -------------------------------------------------------------------- */
void NewDataFile(Widget w, XtPointer client, XtPointer call)
{
  char *dataFile;

  fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &dataFile);
 
  fileMgr.NewFile(dataFile);
  controlWindow->SetFileNames();
  controlWindow->SetProbes();
  controlWindow->PositionTime(True);

}	/* END NEWDATAFILE */

/* -------------------------------------------------------------------- */
void AddDataFile(Widget w, XtPointer client, XtPointer call)
{
  char *dataFile;

  if (fileMgr.NumberOfFiles() >= MAX_DATAFILES)
    {
    ErrorMsg("Currently at maximum allowed files.");
    return;
    }
 
  fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &dataFile);
 
  fileMgr.AddFile(dataFile);
  controlWindow->SetFileNames();

}	/* END ADDDATAFILE */

/* -------------------------------------------------------------------- */
static void PrintPS(Widget w, XtPointer client, XtPointer call)
{
  int           i, j;
  bool          probes = false;
  float         version;
  char		title[200];
  ADS_DataFile	*file = fileMgr.CurrentFile();

  for (j = 0; j < file->NumberOfProbes(); ++j)
    if (file->probe[j]->Display())
      probes = true;

  if (!probes)
    return;

  cursor.WaitCursor(mainPlot->Wdgt());
  mainPlot->reset(NULL);
  version = atof(file->HeaderVersion());
 
  sprintf(title, "%s, %s - %s", file->ProjectNumber(), file->FlightNumber(),
        file->FlightDate());

  PostScript pen(PSoutFile, "xpms2d", title, 0.72);
  pen.SetFont(40);
  sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
                550, title, (int)(800 * printerSetup->HeightRatio()));
  pen.Issue(buffer);
  pen.ShowStr(title);
  pen.SetFont(16);

  for (i = 0; i < nBuffs; ++i)
    for (j = 0; j < file->NumberOfProbes(); ++j)
      {
      if (!strncmp(file->probe[j]->Code, (char*)&pgFbuff[i], 2)
          && file->probe[j]->Display())
        mainPlot->draw(&pgFbuff[i], ProcessRecord(&pgFbuff[i], version), version, j+1, &pen);
      }

  cursor.PointerCursor(mainPlot->Wdgt());

}	/* END POSTSCRIPT */

/* -------------------------------------------------------------------- */
static void SavePS(Widget w, XtPointer client, XtPointer call)
{
  char	*p;

  fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &PSoutFile);

  strcpy(psPath, PSoutFile);
  if ((p = strrchr(psPath, '/')))
    strcpy(p+1, "*.ps");

  if (access(PSoutFile, F_OK) == 0)
    {
    sprintf(buffer, "Overwrite file %s", PSoutFile);
    WarnMsg(buffer, PrintPS, NULL);
    }
  else
    PrintPS(NULL, NULL, NULL);
 
}       /* END SAVEPS */

/* -------------------------------------------------------------------- */
void PrintSave(Widget w, XtPointer client, XtPointer call)
{
  if (fileMgr.NumberOfFiles() == 0)
    {
    ErrorMsg("No data.");
    return;
    }
 
  if (client)
    fileSel->QueryFile("Enter PostScript output file name:", psPath,
                       (XtCallbackProc)SavePS);
  else
    {
    PSoutFile = NULL;
    PrintPS(NULL, NULL, NULL);
    }

}	/* END POSTSCRIPT */

#ifdef PNG
/* -------------------------------------------------------------------- */
void SavePNG_OK(Widget w, XtPointer client, XtPointer call)
{
  XImage        *image;

  image = mainPlot->GetImage(0, 1, mainPlot->Width(), mainPlot->Height()-1);

  color->SavePNG(pngOutFile, image);

  XDestroyImage(image);

}       /* END SAVEPNG_OK */

/* -------------------------------------------------------------------- */
void confirmPNG(Widget w, XtPointer client, XtPointer call)
{
  char	*p;

  fileSel->ExtractFileName(((XmFileSelectionBoxCallbackStruct *)call)->value, &pngOutFile);

  strcpy(pngPath, pngOutFile);
  if ((p = strrchr(pngPath, '/')))
    strcpy(p+1, "*.png");

  if (access(pngOutFile, F_OK) == 0)
    {
    sprintf(buffer, "Overwrite file %s", pngOutFile);
    new XmWarn(application->Shell(), buffer, SavePNG_OK, NULL);
    }
  else
    SavePNG_OK((Widget)NULL, (XtPointer)NULL, (XtPointer)NULL);

}

/* -------------------------------------------------------------------- */
void SavePNG(Widget w, XtPointer client, XtPointer call)
{
  fileSel->QueryFile("Enter PNG output file name:", pngPath,
                       (XtCallbackProc)confirmPNG);

}       /* END SAVEPNG */
#endif

/* -------------------------------------------------------------------- */
void Quit(Widget w, XtPointer client, XtPointer call)
{
  delete application;

  exit(0);

}	/* END QUIT */

/* -------------------------------------------------------------------- */
void ToggleTiming(Widget w, XtPointer client, XtPointer call)
{
  mainPlot->SetTimingWords();
  PageCurrent();

}       /* END TOGGLEDISPLAY */

/* -------------------------------------------------------------------- */
void ToggleWrap(Widget w, XtPointer client, XtPointer call)
{
  mainPlot->SetWrapDisplay();
  PageCurrent();

}       /* END TOGGLEDISPLAY */

/* -------------------------------------------------------------------- */
void ToggleDisplay(Widget w, XtPointer client, XtPointer call)
{
  mainPlot->SetDisplayMode((int)client);
  PageCurrent();

}       /* END TOGGLEDISPLAY */

/* -------------------------------------------------------------------- */
void ToggleSynthetic(Widget w, XtPointer client, XtPointer call)
{
  fileMgr.CurrentFile()->ToggleSyntheticData();
  PageCurrent();

}       /* END TOGGLESYNTHETIC */

/* -------------------------------------------------------------------- */
void ForkNetscape(Widget w, XtPointer client, XtPointer call)
{
  if (fork() == 0)
    {
    switch ((int)client)
      {
      case 1:
        execlp("netscape", "netscape", "http://raf.atd.ucar.edu", NULL);
        break;
      case 2:
        execlp("netscape", "netscape", "http://raf.atd.ucar.edu/Software", NULL);
        break;
      case 3:
        execlp("netscape", "netscape", "http://raf.atd.ucar.edu/Software/xpms2d.html", NULL);
        break;
      }

    printf("exec of netscape failed, errno = %d\n", errno);
    exit(0);
    }

}       /* END FORKNETSCAPE */

/* END CB_MENUS.CC */

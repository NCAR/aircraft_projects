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

STATIC FNS:	Print()
		Save()

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"
#include <unistd.h>

#include "Application.h"
#include "Canvas.h"
#include "Cursor.h"
#include "FileMgr.h"
#include "MovieControl.h"
#include "PostScript.h"
#include "PlotMgr.h"
#include "SetMgr.h"
#include "XmFile.h"
#include "XmWarn.h"

extern Application	*application;
extern FileManager	fileMgr;
extern Canvas		*mainCanvas;
extern MovieControl	*movieControlGUI;
extern PlotManager	*plotMgr;
extern SetManager	setMgr;
extern XCursor		cursor;
extern XmFile		*fileSel;

/* -------------------------------------------------------------------- */
void GetDataFileName(Widget w, XtPointer client, XtPointer call)
{
  static bool   firstTime = True;
 
  if (firstTime)
    {
    fileSel->QueryFile("Enter Data file to read:", DataPath, (XtCallbackProc)client);
    firstTime = False;
    }
  else
    fileSel->QueryFile("Enter Data file to read:", NULL, (XtCallbackProc)client);

}

/* -------------------------------------------------------------------- */
void NewDataFile(Widget w, XtPointer client, XtPointer call)
{
  char *dataFile;

  if (w)
    fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &dataFile);
  else
    dataFile = (char *)client;
 
  fileMgr.NewFile(dataFile);

  if (w)
    setMgr.Clear();

  SetFileNames();
  SetProbeNames();
  SetStartEndTime();

  movieControlGUI->TurnOnAverage();
  movieControlGUI->UpdateTime();

  if (w)
    plotMgr->DrawImage();

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
  SetFileNames();

}	/* END ADDDATAFILE */

/* -------------------------------------------------------------------- */
void GenerateFile(Widget w, XtPointer client, XtPointer call)
{
  movieControlGUI->SetAveragePeriod(1);
  movieControlGUI->SetDefaultStartEndTime();

//  Copy file.
//  Add new variables.

//  foreach probe in currentFile()
//    Read, compute, and write.

}	/* END GENERATEFILE */

/* -------------------------------------------------------------------- */
static char	*PSoutFile = NULL;

static void PrintPS(Widget w, XtPointer client, XtPointer call)
{
//  cursor.WaitCursor(mainCanvas->w);
  plotMgr->Print(PSoutFile);

//  cursor.PointerCursor(mainCanvas->w);

}	/* END POSTSCRIPT */

/* -------------------------------------------------------------------- */
static void SavePS(Widget w, XtPointer client, XtPointer call)
{
  fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &PSoutFile);

  if (access(PSoutFile, F_OK) == 0)
    {
    sprintf(buffer, "Overwrite file %s", PSoutFile);
    new XmWarn(application->Shell(), buffer, PrintPS, NULL);
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
    fileSel->QueryFile("Enter PostScript output file name:", "*.ps",
                       (XtCallbackProc)SavePS);
  else
    {
    PSoutFile = NULL;
    PrintPS(NULL, NULL, NULL);
    }

}	/* END PRINTSAVE */

#ifdef PNG
static char *pngOutFile;

/* -------------------------------------------------------------------- */
void SavePNG_OK(Widget w, XtPointer client, XtPointer call)
{
  XImage        *image;

  image = mainCanvas->GetImage(0, 20, mainCanvas->Width(), mainCanvas->Height()-20);

  if (strstr(pngOutFile, ".png") == NULL)
    strcat(pngOutFile, ".png");

  plotMgr->SavePNG(pngOutFile, image);

  XDestroyImage(image);

}	/* END SAVEPNG_OK */

/* -------------------------------------------------------------------- */
void confirmPNG(Widget w, XtPointer client, XtPointer call)
{
  fileSel->ExtractFileName(((XmFileSelectionBoxCallbackStruct *)call)->value, &pngOutFile);

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
  fileSel->QueryFile("Enter PNG output file name:", "*.png",
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
        execlp("netscape", "netscape", "http://raf.atd.ucar.edu/Software/ncpp.html", NULL);
        break;
      }

    printf("exec of netscape failed, errno = %d\n", errno);
    exit(0);
    }

}       /* END FORKNETSCAPE */

/* END CB_MENUS.CC */

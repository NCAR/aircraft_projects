/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_text.cc

FULL NAME:	Callbacks to TextWindow(s)

ENTRY POINTS:	ViewHeader()
		ViewASCII()
		UpdateASCII()
		ViewVars()
		UpdateVars()
		DismissText()
		SaveText()
		PrintText()

DESCRIPTION:	SaveText2()

REFERENCES:	none

REFERENCED BY:	Menu button.

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Application.h"
#include "Ascii.h"
#include "Cursor.h"
#include "Header.h"
#include "FileMgr.h"
#include "PlotMgr.h"
#include "Printer.h"
#include "SetMgr.h"
#include "TextWindow.h"
#include "Titles.h"
#include "VarsWin.h"
#include "XmFile.h"

#include <Xm/Text.h>

extern Application	*application;
extern FileManager	fileMgr;
extern PlotManager	*plotMgr;
extern Printer		*printerSetup;
extern SetManager	setMgr;
extern XCursor		cursor;
extern XmFile		*fileSel;

static Ascii	*ascii = NULL;
static Header	*ncHeader = NULL;
static Titles	*varTitles = NULL;
static VarsWin	*otherVars = NULL;

/* -------------------------------------------------------------------- */
void ViewTitles(Widget w, XtPointer client, XtPointer call)
{
  if (fileMgr.NumberOfFiles() == 0)
    return;

  if (!varTitles)
    varTitles = new Titles(application->Shell());

  varTitles->Update(fileMgr.CurrentFile()->FileName());
  varTitles->PopUp();

}	/* END VIEWTITLES */

/* -------------------------------------------------------------------- */
void ViewHeader(Widget w, XtPointer client, XtPointer call)
{
  if (fileMgr.NumberOfFiles() == 0)
    return;

  if (!ncHeader)
    ncHeader = new Header(application->Shell());

  ncHeader->Update(fileMgr.CurrentFile()->FileName());
  ncHeader->PopUp();

}	/* END VIEWHEADER */

/* -------------------------------------------------------------------- */
void ViewASCII(Widget w, XtPointer client, XtPointer call)
{
  if (!ascii)
    ascii = new Ascii(application->Shell());

  UpdateASCII();

  ascii->PopUp();

}	/* END VIEWASCII */

/* -------------------------------------------------------------------- */
void UpdateASCII()
{
  if (ascii)
    ascii->Update(setMgr, plotMgr);

}	/* END UPDATEASCII */

/* -------------------------------------------------------------------- */
void ViewVars(Widget w, XtPointer client, XtPointer call)
{
  if (!otherVars)
    otherVars = new VarsWin(application->Shell());

  UpdateVars();

  otherVars->PopUp();

}	/* END VIEWASCII */

/* -------------------------------------------------------------------- */
void UpdateVars()
{
  if (otherVars)
    otherVars->Update(setMgr, plotMgr);

}	/* END UPDATEASCII */

/* -------------------------------------------------------------------- */
void DismissText(Widget w, XtPointer client, XtPointer call)
{
  TextWindow	*obj = (TextWindow *)client;

  XtPopdown(XtParent(obj->Window()));
  XtUnmanageChild(obj->Window());

  obj->Clear();

}	/* END DISMISSTEXT */

/* -------------------------------------------------------------------- */
void PrintText(Widget w, XtPointer client, XtPointer call)
{
  FILE  *fp;
  char  *p;

//  cursor.WaitCursor(application->Shell());
  cursor.WaitCursor((Widget)client);

  if ((fp = popen(printerSetup->lpCommand(), "w")) == NULL)
    {
    ErrorMsg("Print: can't open pipe to 'lp'");
    return;
    }

  p = XmTextGetString((Widget)client);

  fprintf(fp, "%s\n", p);
  XtFree(p);

  pclose(fp);

  cursor.PointerCursor((Widget)client);
//  cursor.PointerCursor(application->Shell());

}	/* END PRINTTEXT */

/* -------------------------------------------------------------------- */
static Widget	tmpText;

void SaveText2(Widget w, XtPointer client, XtPointer call)
{
  FILE  *fp;
  char  *p, *dataFile;

  fileSel->ExtractFileName(
         ((XmFileSelectionBoxCallbackStruct *)call)->value, &dataFile);

  if ((fp = fopen(dataFile, "w")) == NULL)
    {
    sprintf(buffer, "SaveText: can't open %s.", dataFile);
    ErrorMsg(buffer);
    return;
    }

  p = XmTextGetString(tmpText);
  fprintf(fp, "%s\n", p);
  XtFree(p);

  fclose(fp);

}	/* END SAVETEXT2 */

/* -------------------------------------------------------------------- */
void SaveText(Widget w, XtPointer client, XtPointer call)
{
  tmpText = (Widget)client;

  fileSel->QueryFile("Enter file name to save as:", DataPath, (XtCallbackProc)SaveText2);

}	/* END SAVETEXT */

/* -------------------------------------------------------------------- */
void SearchText(Widget w, XtPointer client, XtPointer call)
{
  ((TextWindow *)client)->Search();

}	/* END SEARCH */

/* END CB_TEXT.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_text.cc

FULL NAME:	Callbacks to TextWindow(s)

ENTRY POINTS:	ViewHex()
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
#include "Cursor.h"
#include "FileMgr.h"
#include "Printer.h"
#include "Enchilada.h"
#include "Hex.h"
#include "XmFile.h"

#include <Xm/Text.h>

extern Application	*application;
extern Printer		*printerSetup;
extern XCursor		cursor;
extern XmFile		*fileSel;

static Hex	*hexWin = NULL;
Enchilada	*enchiladaWin = NULL;

extern int     nBuffs;
extern P2d_rec pgFbuff[];

/* -------------------------------------------------------------------- */
void ViewEnchilada(Widget w, XtPointer client, XtPointer call)
{ 
  if (nBuffs == 0)
    return;
  
  if (!enchiladaWin)
    enchiladaWin = new Enchilada(application->Shell());

  enchiladaWin->PopUp();
  PageCurrent();

}       /* END VIEWTITLES */

/* -------------------------------------------------------------------- */
void ViewHex(Widget w, XtPointer client, XtPointer call)
{
  if (nBuffs == 0)
    return;

  if (!hexWin)
    hexWin = new Hex(application->Shell());

  hexWin->Update(nBuffs, pgFbuff);
  hexWin->PopUp();

}	/* END VIEWTITLES */

/* -------------------------------------------------------------------- */
void DismissText(Widget w, XtPointer client, XtPointer call)
{
  TextWindow	*obj = (TextWindow *)client;

  obj->Clear();
  obj->PopDown();

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
void SearchText(Widget w, XtPointer client, XtPointer call)
{
  ((TextWindow *)client)->Search();

}       /* END SEARCH */

/* -------------------------------------------------------------------- */
void SaveText(Widget w, XtPointer client, XtPointer call)
{
  tmpText = (Widget)client;

  fileSel->QueryFile("Enter file name to save as:", DataPath, (XtCallbackProc)SaveText2);

}	/* END SAVETEXT */

/* END CB_TEXT.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	XmFile.cc

FULL NAME:	Motif File Selection Box

DESCRIPTION:	This pops up a Fileselection box for choosing a file name
		Call CreateFile where you init X stuff.  Then just call
		QueryFile(Prompt, Default Directory, OK_callBack);  Then your
		OKcallBack procedure calls ExtractFileName()

INPUT:		String to Display.

OUTPUT:		Error message in its own tidy little window.
-------------------------------------------------------------------------
*/

#include "XmFile.h"


/* -------------------------------------------------------------------- */
static void DismissFile(Widget w, XtPointer client, XtPointer call)
{
  XtUnmanageChild((Widget)client);
  XtRemoveGrab((Widget)client);
}

/* -------------------------------------------------------------------- */
XmFile::XmFile(Widget parent)
{
  fileBox = XmCreateFileSelectionDialog(parent, "fileBox", NULL, 0);
  XtSetSensitive(XmFileSelectionBoxGetChild(fileBox, XmDIALOG_HELP_BUTTON), false);

  XtAddCallback(fileBox,XmNcancelCallback,(XtCallbackProc)DismissFile, fileBox);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void XmFile::QueryFile(char prompt[], char directory[], XtCallbackProc callBack)
{
  XmString	xmdir, xmprompt;
  Arg		args[4];
  Cardinal	n = 0;

  if (prompt)
    {
    xmprompt = XmStringCreate(prompt, XmSTRING_DEFAULT_CHARSET);

    XtSetArg(args[n], XmNselectionLabelString, xmprompt); ++n;
    XtSetValues(fileBox, args, n);
    XmStringFree(xmprompt);
    }

  if (directory)
    {
    xmdir = XmStringCreate(directory, XmSTRING_DEFAULT_CHARSET);
    XmFileSelectionDoSearch(fileBox, xmdir);
    XmStringFree(xmdir);
    }
  else
    XmFileSelectionDoSearch(fileBox, NULL);

  XtRemoveAllCallbacks(fileBox, XmNokCallback);
  XtAddCallback(fileBox, XmNokCallback, (XtCallbackProc)DismissFile, fileBox);
  XtAddCallback(fileBox, XmNokCallback, (XtCallbackProc)callBack, fileBox);

  XtAddGrab(fileBox, true, false);
  XtManageChild(fileBox);

}	/* END QUERYFILE */

/* -------------------------------------------------------------------- */
void XmFile::ExtractFileName(XmString str, char **text)
{
  XmStringGetLtoR(str, XmSTRING_DEFAULT_CHARSET, text);

}	/* END EXTRACTFILENAME */

/* END XMFILE.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	Xfile.c

FULL NAME:	FileSelectionBox

DESCRIPTION:	This pops up a Fileselection box for choosing a file name
		Call CreateFile where you init X stuff.  Then just call
		QueryFile(Prompt, Default Directory, OK_callBack);  Then your
		OKcallBack procedure calls ExtractFileName()

INPUT:		String to Display.

OUTPUT:		Error message in its own tidy little window.
-------------------------------------------------------------------------
*/

#include <Xm/Xm.h>
#include <Xm/FileSB.h>

static Widget	fileBox;


/* -------------------------------------------------------------------- */
void QueryFile(char *prompt, char *directory, XtCallbackProc callBack)
{
  XmString	xmdir, xmprompt;
  Arg		args[4];
  int		n = 0;

  if (prompt)
    {
    xmprompt = XmStringCreateLocalized(prompt);
 
    XtSetArg(args[n], XmNselectionLabelString, xmprompt); ++n;
    XtSetValues(fileBox, args, n);
    XmStringFree(xmprompt);
    }
 
  if (directory)
    {
    xmdir = XmStringCreateLocalized(directory);
    XmFileSelectionDoSearch(fileBox, xmdir);
    XmStringFree(xmdir);
    }
  else
    XmFileSelectionDoSearch(fileBox, NULL);

  XtRemoveAllCallbacks(fileBox, XmNokCallback);
  XtAddCallback(fileBox, XmNokCallback, (XtCallbackProc)callBack,
							(XtPointer)NULL);

  XtAddGrab(fileBox, TRUE, FALSE);
  XtManageChild(fileBox);

}	/* END QUERYFILE */

/* -------------------------------------------------------------------- */
/* ARGSUSED */
void FileCancel(Widget w, XtPointer clientData, XtPointer callData)
{
  XtUnmanageChild(fileBox);
  XtRemoveGrab(fileBox);

}	/* END FILECANCEL */

/* -------------------------------------------------------------------- */
void CreateFileSelectionBox(Widget parent)
{
  fileBox = XmCreateFileSelectionDialog(parent, "fileBox", NULL, 0);
  XtSetSensitive(XmFileSelectionBoxGetChild(fileBox, XmDIALOG_HELP_BUTTON),
		FALSE);

  XtAddCallback(fileBox, XmNcancelCallback, (XtCallbackProc)FileCancel,
		(XtPointer)FALSE);

}	/* END CREATEFILESELECTIONBOX */

/* -------------------------------------------------------------------- */
void ExtractFileName(XmString str, char **text)
{
  XmStringGetLtoR(str, XmSTRING_DEFAULT_CHARSET, text);

}	/* END EXTRACTFILENAME */

/* END XFILE.C */

/*
-------------------------------------------------------------------------
OBJECT NAME:	XmQuery.c

FULL NAME:	Show Selection Box with Message

DESCRIPTION:	This routines allow you to Ask the user a question and
		get the answer.  During Initialization call CreateQuery().
		To use, just call QueryUser(question, maxlen_of_input,
		callBack to call if the OK buttonis pressed), in the
		callBack procedure call ExtractAnswer().

INPUT:		String to Display, and callBack for OK

OUTPUT:		Question in its own tidy little window.

AUTHOR:		websterc@ncar
-------------------------------------------------------------------------
*/

#include "XmQuery.h"


/* -------------------------------------------------------------------- */
static void DismissQuery(Widget w, XtPointer client, XtPointer call)
{
  XtUnmanageChild((Widget)client);
  XtRemoveGrab((Widget)client);
}
 
/* -------------------------------------------------------------------- */
void XmQuery::QueryUser(char str[], int maxlen, void (*callBack)())
{
  Widget	w;
  Arg		args[5];
  int		n;
  XmString	xStr;

  n = 0;
  w = XmSelectionBoxGetChild(queryBox, XmDIALOG_SELECTION_LABEL);
  xStr = XmStringCreateLtoR(str, XmSTRING_DEFAULT_CHARSET);
  XtSetArg(args[n], XmNlabelString, xStr); ++n;
  XtSetValues(w, args, n);
  XmStringFree(xStr);


  n = 0;
  w = XmSelectionBoxGetChild(queryBox, XmDIALOG_TEXT);
  XtSetArg(args[n], XmNmaxLength, maxlen); ++n;
  XtSetArg(args[n], XmNwidth, 0); ++n;
  XtSetArg(args[n], XmNcolumns, maxlen); ++n;
  XtSetValues(w, args, n);
  XmTextSetString(w, "");

  XtRemoveAllCallbacks(queryBox, XmNokCallback);
  XtAddCallback(queryBox, XmNokCallback, (XtCallbackProc)callBack, NULL);

  XtManageChild(queryBox);
  XtPopup(XtParent(queryBox), XtGrabNone);

}	/* END QUERYUSER */

/* -------------------------------------------------------------------- */
XmQuery::XmQuery(Widget parent)
{
  queryBox = XmCreatePromptDialog(parent, "queryBox", NULL, 0);
  XtSetSensitive(XmSelectionBoxGetChild(queryBox, XmDIALOG_HELP_BUTTON), false);
  XtAddCallback(queryBox, XmNcancelCallback, DismissQuery,(XtPointer)queryBox);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void XmQuery::ExtractAnswer(char *s)
{
  Widget	w;
  char		*a;

  w = XmSelectionBoxGetChild(queryBox, XmDIALOG_TEXT);
  a = XmTextGetString(w);

  strcpy(s, a);
  XtFree(a);

}	/* END EXTRACTANSWER */

/* END XMQUERY.C */

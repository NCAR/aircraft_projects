/*
-------------------------------------------------------------------------
OBJECT NAME:	XmError.cc

FULL NAME:	Show Error Box with Message

DESCRIPTION:	CreateError should be called once where you initialize
		your X stuff.  To use just call ShowError(ErrMsg)

INPUT:		String to Display.

OUTPUT:		Error message in its own tidy little window.

COPYRIGHT:	University Corporation for Atmospheric Research, 1991
-------------------------------------------------------------------------
*/

#include "XmError.h"


/* -------------------------------------------------------------------- */
XmError::XmError(Widget parent, char str[])
{
  Widget	label;
  Arg		args[5];
  XmString	xStr;

  errorBox = XmCreateErrorDialog(parent, "errorBox", NULL, 0);
  XtSetSensitive(XmMessageBoxGetChild(errorBox, XmDIALOG_CANCEL_BUTTON), false);
  XtSetSensitive(XmMessageBoxGetChild(errorBox, XmDIALOG_HELP_BUTTON), false);

  XtAddCallback(errorBox, XmNokCallback, (XtCallbackProc)XtDestroyWidget, NULL);

  label = XmMessageBoxGetChild(errorBox, XmDIALOG_MESSAGE_LABEL);
  xStr = XmStringCreateLtoR(str, XmSTRING_DEFAULT_CHARSET);
  XtSetArg(args[0], XmNlabelString, xStr);
  XtSetValues(label, args, 1);
  XmStringFree(xStr);

  XtManageChild(errorBox);
  XtPopup(XtParent(errorBox), XtGrabNonexclusive);

}	/* END CONTRUCTOR */

/* END XMERROR.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	XmWarn.c

FULL NAME:	Show Warning Box with Message

DESCRIPTION:	CreateWarn should be called once where you initialize
		your X stuff.  To use just call WarnUser(ErrMsg, callBack)

INPUT:		String to Display.  Callback to call if user hits OK.

OUTPUT:		Warning message in its own tidy little window.

AUTHOR:		websterc@ncar
-------------------------------------------------------------------------
*/

#include "XmWarn.h"


/* -------------------------------------------------------------------- */
XmWarn::XmWarn(Widget parent, char warning[], XtCallbackProc okCB, XtCallbackProc cancelCB)
{
  Widget	label;
  Arg		args[5];
  XmString	xStr;

  warnBox = XmCreateWarningDialog(parent, "warnBox", NULL, 0);
  XtSetSensitive(XmMessageBoxGetChild(warnBox, XmDIALOG_HELP_BUTTON), false);

  label = XmMessageBoxGetChild(warnBox, XmDIALOG_MESSAGE_LABEL);
  xStr = XmStringCreateLtoR(warning, XmSTRING_DEFAULT_CHARSET);
  XtSetArg(args[0], XmNlabelString, xStr);
  XtSetValues(label, args, 1);
  XmStringFree(xStr);

  if (okCB)
    XtAddCallback(warnBox, XmNokCallback, (XtCallbackProc)okCB, NULL);
  if (cancelCB)
    XtAddCallback(warnBox, XmNcancelCallback, (XtCallbackProc)cancelCB, NULL);

  XtAddCallback(warnBox,XmNokCallback,(XtCallbackProc)XtDestroyWidget, NULL);
  XtAddCallback(warnBox,XmNcancelCallback,(XtCallbackProc)XtDestroyWidget,NULL);

  XtManageChild(warnBox);
  XtPopup(XtParent(warnBox), XtGrabNone);

}	/* END CONTRUCTOR */

/* END XMWARN.C */

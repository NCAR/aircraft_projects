/*
-------------------------------------------------------------------------
OBJECT NAME:	MagnifyWindow.cc

FULL NAME:	Data Set Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "MagnifyWindow.h"


/* -------------------------------------------------------------------- */
MagnifyWindow::MagnifyWindow(Widget parent) : WinForm(parent, "mag", Form)
{
  Widget        frame, rc, b[3];
  Cardinal      n;
  Arg           args[8];
 

  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  frame = XmCreateFrame(Window(), "buttonFrame", args, n);
  XtManageChild(frame);
 
  n = 0;
  rc = XmCreateRowColumn(frame, "buttonRC", args, n);
  XtManageChild(rc);
 
  n = 0;
  b[0] = XmCreatePushButton(rc, "dismissButton", args, n);
  b[1] = XmCreatePushButton(rc, "printButton", args, n);
  XtManageChildren(b, 2);
  XtAddCallback(b[0], XmNactivateCallback, DismissWindow, Window());
//  XtAddCallback(b[1], XmNactivateCallback, diffPostScript, NULL);
XtSetSensitive(b[1], false);
 
 
  /* Create Graphics Canvas
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNtopWidget, frame); n++;
  XtSetArg(args[n], XmNbottomAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  drawA = XmCreateDrawingArea(Window(), "magCanvas", args, n);
  XtManageChild(drawA);

  XtAddCallback(drawA, XmNexposeCallback, (XtCallbackProc)MagnifyExpose, NULL);
//  XtAddCallback(drawA, XmNinputCallback, (XtCallbackProc)MagnifyInput, NULL);
  XtAddCallback(drawA, XmNresizeCallback, (XtCallbackProc)MagnifyResize, NULL);

}	/* END CONSTRUCTOR */

/* END MAGNIFYWINDOW.CC */

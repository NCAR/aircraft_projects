/*
-------------------------------------------------------------------------
OBJECT NAME:	ccb.cc

FULL NAME:	Misc. Callbacks

ENTRY POINTS:	DismissWindow()
		DestroyWindow()

STATIC FNS:	none

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "define.h"

#include "Printer.h"
#include "TextWindow.h"

#include <Xm/Text.h>

extern Printer		*printerSetup;

/* -------------------------------------------------------------------- */
void DestroyWindow(Widget w, XtPointer client, XtPointer call)
{
  XtPopdown(XtParent((Widget)client));
  XtUnmanageChild((Widget)client);

  XtDestroyWidget((Widget)client);

}	/* END DESTROYWINDOW */

/* -------------------------------------------------------------------- */
void DismissWindow(Widget w, XtPointer client, XtPointer call)
{
  XtPopdown(XtParent((Widget)client));
  XtUnmanageChild((Widget)client);

}	/* END DISMISSWINDOW */

/* END CCB.CC */

/*
-------------------------------------------------------------------------
OBJECT NAME:	ccb.c

FULL NAME:	Misc. Callback Wrappers

ENTRY POINTS:	DismissWindow()
		DestroyWindow()

STATIC FNS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#include "define.h"


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

/* END CCB.C */

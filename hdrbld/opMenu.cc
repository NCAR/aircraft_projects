/*
-------------------------------------------------------------------------
OBJECT NAME:	opMenu.c

FULL NAME:	Utilities for Option Menus

ENTRY POINTS:	InitializeOpMenu()
		GetOpMenu()
		SetOpMenu()

STATIC FNS:	none

DESCRIPTION:	The Initialize function only supports the same callback
		for all buttons.

REFERENCES:	none

REFERENCED BY:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1996
-------------------------------------------------------------------------
*/

#include "hdrbld.h"

#include <Xm/PushB.h>
#include <Xm/RowColumn.h>


/* -------------------------------------------------------------------- */
void InitializeOpMenu(Widget pd, char *list[], void (*cb)())
{
  int     i, n;
  Arg     args[8];
  XmString    name;
  Widget  b[MAX_DSM];

  for (i = 0; list[i]; ++i)
    {
    name = XmStringCreateLocalized(list[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    b[i] = XmCreatePushButton(pd, "opButton", args, n);

    if (cb)
      XtAddCallback(b[i], XmNactivateCallback, cb, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(b, i);
 
}	/* END INITIALIZEOPMENU */

/* -------------------------------------------------------------------- */
char *GetOpMenu(Widget opMenu)
{
  Widget	cascade;
  Arg		args[3];
  Cardinal	n;
  XmString	label;
  char		*p;

  cascade = XmOptionButtonGadget(opMenu);

  n = 0;
  XtSetArg(args[n], XmNlabelString, &label); ++n;
  XtGetValues(cascade, args, n);

  XmStringGetLtoR(label, XmSTRING_DEFAULT_CHARSET, &p);
  XmStringFree(label);

  return(p);

}	/* END GETOPMENU */

/* -------------------------------------------------------------------- */
void SetOpMenu(Widget opMenu, char *target)
{
  Arg		args[2];
  Cardinal	n;
  XmString	name;

  name = XmStringCreateLocalized(target);

  n = 0;
  XtSetArg(args[n], XmNlabelString, name); ++n;
  XtSetValues(XmOptionButtonGadget(opMenu), args, 1);
  XmStringFree(name);

}	/* END SETOPMENU */

/* END OPMENU.C */

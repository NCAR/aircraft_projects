/*
-------------------------------------------------------------------------
OBJECT NAME:    menu.c

FULL NAME:      Utilities for PMS Option Menus

ENTRY POINTS:   GetMenu()
                SetMenu()

STATIC FNS:     none

DESCRIPTION:

REFERENCES:     none

REFERENCED BY:

COPYRIGHT:      University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "hdrbld.h"

#include <Xm/RowColumn.h>

/* -------------------------------------------------------------------- */
char *GetMenu(Widget dsmMenu)
{
  Widget        cascade;
  Arg           args[3];
  Cardinal      n;
  XmString      label;
  char          *p;

  cascade = XmOptionButtonGadget(dsmMenu);

  n = 0;
  XtSetArg(args[n], XmNlabelString, &label); ++n;
  XtGetValues(cascade, args, n);

  XmStringGetLtoR(label, XmSTRING_DEFAULT_CHARSET, &p);
  XmStringFree(label);

  return(p);

}       /* END GETMENU */

/* -------------------------------------------------------------------- */
void SetMenu(Widget menu, char dsm[])
{
  Arg           args[2];
  Cardinal      n;
  XmString      name;

  name = XmStringCreateLocalized(dsm);

  n = 0;
  XtSetArg(args[n], XmNlabelString, name); ++n;
  XtSetValues(XmOptionButtonGadget(menu), args, 1);
  XmStringFree(name);

}	/* END SETMENU */

/* END MENU.C */

/*
-------------------------------------------------------------------------
OBJECT NAME:	dsm.c

FULL NAME:	Utilities for DSM Option Menus

ENTRY POINTS:	InitializeDSMmenu()
		SetDSMlist()	Get DSM_LIST for given Aircraft

STATIC FNS:	none

DESCRIPTION:	

REFERENCES:	none

REFERENCED BY:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1996
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"
#include "ac.h"

#include <Xm/PushB.h>
#include <Xm/RowColumn.h>


/* -------------------------------------------------------------------- */
void InitializeDSMmenu(Widget dsmMenu, char *dsmList[], void (*cb)())
{
  int		i, n;
  Arg		args[8];
  XmString	name;
  Widget	b[MAX_DSM];

  for (i = 0; dsmList[i]; ++i)
    {
    name = XmStringCreateLocalized(dsmList[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    b[i] = XmCreatePushButton(dsmMenu, "dsmButton", args, n);

    if (cb)
      XtAddCallback(b[i], XmNactivateCallback, cb, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(b, i);
 
}	/* END INITIALIZEDSMMENU */

/* -------------------------------------------------------------------- */
void SetDSMlist(char ac[])
{
  int     i;
  char    *p;

  for (i = 0; DSM[i]; ++i)
    free(DSM[i]);

  p = GetAircraftParameter(ac, "DSM_LIST");
  strcpy(buffer, GetAircraftParameter(ac, "DSM_LIST"));

  p = strtok(buffer, ", \t\n");

  for (i = 0; p; ++i)
    {
    DSM[i] = GetMemory(strlen(p));
    strcpy(DSM[i], p);
    p = strtok(NULL, ", \t\n");
    }

  DSM[i] = NULL;
 
}	/* END SETDSMLIST */

/* END DSM.C */

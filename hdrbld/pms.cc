/*
-------------------------------------------------------------------------
OBJECT NAME:	pms.c

FULL NAME:	Utilities for PMS Option Menus

ENTRY POINTS:	InitializePMSmenu()
		SetPMSlocns()	Get PMS_LOCNS for given Aircraft

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
void InitializePMSmenu(Widget dsmMenu, char *dsmList[], void (*cb)())
{
  int     i, n;
  Arg     args[8];
  XmString    name;
  Widget  b[64];

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
 
}	/* END INITIALIZEPMSMENU */

/* -------------------------------------------------------------------- */
void SetPMSlocns(char ac[])
{
  int     i, j;
  char    *p;

  strcpy(buffer, GetAircraftParameter(ac, "PMS_LOCNS"));

  for (i = 0; pmsInfo[i].title; ++i)
    {
    pmsInfo[i].enabled = FALSE;
    XtSetSensitive(pmsInfo[i].rc, FALSE);
    }

  p = strtok(buffer, ", \t\n");

  for (i = 0; p; ++i)
    {
    for (j = 0; pmsInfo[j].title; ++j)
      if (strcmp(pmsInfo[j].abbrev, p) == 0)
        {
        XtSetSensitive(pmsInfo[j].rc, TRUE);
        pmsInfo[j].enabled = TRUE;
        }

    p = strtok(NULL, ", \t\n");
    }

}	/* END SETPMSLOCNS */

/* END PMS.C */

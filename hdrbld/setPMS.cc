/*
-------------------------------------------------------------------------
OBJECT NAME:	setPMS.c

FULL NAME:	

ENTRY POINTS:	SetPMS()

STATIC FNS:	none

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"

extern Widget resButts[];

/* -------------------------------------------------------------------- */
void SetPMS(Widget w, XtPointer client, XtPointer call)
{
  char	*p;
  int	index = (int)client;

  /* Retreive probe serial number. */
  p = GetMenu(pmsInfo[index].probe);

  if (w)
    {
    sprintf(buffer, "PMS location %s set to %s\n", pmsInfo[index].abbrev, p);
    AddToChangeLog(buffer);
    }

  if (strcmp(p, "None") == 0)
    {
    pmsInfo[index].type = 0;
    XtSetSensitive(pmsInfo[index].DSMom, FALSE);
    XtSetSensitive(pmsInfo[index].interfaceNum, FALSE);
    XtSetSensitive(pmsInfo[index].channelNum, FALSE);
    return;
    }

  XtSetSensitive(pmsInfo[index].DSMom, TRUE);
  XtSetSensitive(pmsInfo[index].interfaceNum, TRUE);
  XtSetSensitive(pmsInfo[index].channelNum, TRUE);

  if (strncmp(p, "2D", 2) == 0)
    {
    pmsInfo[index].type = 2;
    }
  else
    {
    pmsInfo[index].type = 1;
    }

}	/* END SETPMS */

/* -------------------------------------------------------------------- */
int LocatePMSlocn(char locn[])
{
  int	i;

  for (i = 0; pmsInfo[i].title; ++i)
    if (strcmp(pmsInfo[i].abbrev, locn) == 0)
      return(i);

  return(0);

}	/* END LOCATEPMSLOCN */

/* END SETPMS.C */
